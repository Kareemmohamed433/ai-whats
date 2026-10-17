import json
import logging
import threading
from datetime import datetime
from flask import current_app
import pywebpush
from app.config import Config
from app.extensions import db, socketio
from app.models.push_subscription import PushSubscription
from app.models.notification_preference import NotificationPreference
from app.models.notification_event import NotificationEvent
from app.models.user import User

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def get_user_preferences(user_id):
        """Get or create default notification preferences for a user."""
        pref = NotificationPreference.query.filter_by(user_id=user_id).first()
        if not pref:
            pref = NotificationPreference(
                user_id=user_id,
                desktop_enabled=True,
                mobile_push_enabled=True,
                sound_enabled=True,
                preview_enabled=True,
                notify_on_all=True,
                notify_on_assigned_only=False
            )
            db.session.add(pref)
            db.session.commit()
        return pref

    @staticmethod
    def send_push_to_subscription(subscription_id, payload, vapid_private_key, vapid_claims):
        """Send a single Web Push payload to a subscription endpoint.
        Deactivates subscription if endpoint returns 404/410 Gone."""
        from app import create_app
        app = current_app._get_current_object() if current_app else create_app()

        with app.app_context():
            sub = PushSubscription.query.get(subscription_id)
            if not sub or not sub.is_active:
                return False

            try:
                sub_info = sub.get_subscription_info()
                data_str = json.dumps(payload, ensure_ascii=False)

                pywebpush.webpush(
                    subscription_info=sub_info,
                    data=data_str,
                    vapid_private_key=vapid_private_key,
                    vapid_claims=vapid_claims,
                    ttl=86400  # 24 hours
                )

                sub.last_used_at = datetime.utcnow()
                db.session.commit()

                # Log successful notification event
                event = NotificationEvent(
                    user_id=sub.user_id,
                    conversation_id=payload.get("data", {}).get("conversationId"),
                    message_id=payload.get("data", {}).get("messageId"),
                    channel="webpush",
                    status="sent"
                )
                db.session.add(event)
                db.session.commit()
                return True

            except pywebpush.WebPushException as ex:
                status_code = getattr(ex.response, "status_code", None) if hasattr(ex, "response") else None
                logger.warning(f"[WebPush] Failed delivery to sub {sub.id}: status={status_code}, err={ex}")

                # 404 Not Found or 410 Gone indicates expired/unsubscribed device
                if status_code in (404, 410):
                    sub.is_active = False
                    db.session.commit()
                    logger.info(f"[WebPush] Deactivated expired subscription {sub.id}")

                event = NotificationEvent(
                    user_id=sub.user_id,
                    conversation_id=payload.get("data", {}).get("conversationId"),
                    message_id=payload.get("data", {}).get("messageId"),
                    channel="webpush",
                    status="failed",
                    error_message=str(ex)[:500]
                )
                db.session.add(event)
                db.session.commit()
                return False

            except Exception as ex:
                logger.error(f"[WebPush] Unexpected error for sub {sub.id}: {ex}")
                event = NotificationEvent(
                    user_id=sub.user_id,
                    conversation_id=payload.get("data", {}).get("conversationId"),
                    message_id=payload.get("data", {}).get("messageId"),
                    channel="webpush",
                    status="failed",
                    error_message=str(ex)[:500]
                )
                db.session.add(event)
                db.session.commit()
                return False

    @staticmethod
    def _async_send_push_notifications(subscriptions_data, payload, vapid_private_key, vapid_claims):
        """Worker thread to dispatch Web Push notifications asynchronously."""
        from app import create_app
        app = create_app()
        with app.app_context():
            for sub_id in subscriptions_data:
                try:
                    NotificationService.send_push_to_subscription(
                        sub_id, payload, vapid_private_key, vapid_claims
                    )
                except Exception as e:
                    logger.error(f"[WebPush] Async dispatch error for sub {sub_id}: {e}")

    @classmethod
    def dispatch_new_message_notification(cls, message, conversation, customer):
        """
        Dispatches real-time Socket.IO notification and Web Push to authorized users.
        Ensures idempotency, respects user notification preferences, and delivers in background.
        """
        try:
            # 1. Determine target authorized users
            target_users = []
            if conversation.assigned_agent_id:
                agent = User.query.get(conversation.assigned_agent_id)
                if agent:
                    target_users.append(agent)

            # If no assigned agent or to keep team informed, find active staff
            all_staff = User.query.filter(User.role.in_(['admin', 'manager', 'agent'])).all()
            for staff in all_staff:
                if staff not in target_users:
                    target_users.append(staff)

            # 2. Prepare payload based on preferences
            platform_labels = {
                'whatsapp': 'واتساب',
                'telegram': 'تيليجرام',
                'instagram': 'إنستغرام',
                'messenger': 'ماسنجر',
                'tiktok': 'تيك توك'
            }
            platform_name = platform_labels.get(conversation.platform, conversation.platform)
            cust_name = customer.name if customer and customer.name else "عميل"

            # 3. Emit real-time Socket event with sound alert for open desktop/mobile dashboards
            try:
                socketio.emit('incoming_message_notification', {
                    "conversation_id": conversation.id,
                    "message_id": message.id,
                    "platform": conversation.platform,
                    "customer_name": cust_name,
                    "preview": message.content[:120] if message.content else "مرفق جديد",
                    "timestamp": message.created_at.isoformat() if message.created_at else datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.warning(f"SocketIO notification emit error: {e}")

            # 4. Check VAPID configuration
            vapid_private_key = Config.VAPID_PRIVATE_KEY
            if not vapid_private_key:
                logger.info("[WebPush] VAPID_PRIVATE_KEY not set. Skipping Web Push dispatch.")
                return

            vapid_claims = {
                "sub": Config.VAPID_CLAIM_EMAIL or "mailto:contact@nexorasolutions.com"
            }

            # 5. Collect active subscriptions for eligible users
            sub_ids_to_notify = []
            preview_payload = None
            generic_payload = None

            for user in target_users:
                pref = cls.get_user_preferences(user.id)
                if not pref.mobile_push_enabled:
                    continue

                if pref.is_conversation_muted(conversation.id):
                    continue

                if pref.notify_on_assigned_only and conversation.assigned_agent_id != user.id:
                    continue

                user_subs = PushSubscription.query.filter_by(user_id=user.id, is_active=True).all()
                if not user_subs:
                    continue

                # Prepare payload
                body_text = f"{cust_name}: {message.content[:80]}" if (pref.preview_enabled and message.content) else "لديك رسالة جديدة من أحد العملاء."
                user_payload = {
                    "title": f"NEXORA — رسالة جديدة ({platform_name})",
                    "body": body_text,
                    "icon": "/icon-192.png",
                    "badge": "/favicon.svg",
                    "tag": f"conv-{conversation.id}",
                    "renotify": True,
                    "data": {
                        "url": f"/inbox?conversationId={conversation.id}",
                        "conversationId": conversation.id,
                        "messageId": message.id,
                        "platform": conversation.platform
                    }
                }

                for s in user_subs:
                    sub_ids_to_notify.append((s.id, user_payload))

            if not sub_ids_to_notify:
                return

            # 6. Dispatch Web Push in background thread (non-blocking for webhooks)
            def _dispatch_worker(subs_with_payloads, priv_key, claims):
                from app import create_app
                app = create_app()
                with app.app_context():
                    for s_id, payload in subs_with_payloads:
                        NotificationService.send_push_to_subscription(s_id, payload, priv_key, claims)

            thread = threading.Thread(
                target=_dispatch_worker,
                args=(sub_ids_to_notify, vapid_private_key, vapid_claims),
                daemon=True
            )
            thread.start()

        except Exception as e:
            logger.error(f"[NotificationService] Dispatch error: {e}")

    @classmethod
    def send_test_notification(cls, user_id):
        """Sends a test Web Push notification to all active devices of the user."""
        pref = cls.get_user_preferences(user_id)
        vapid_private_key = Config.VAPID_PRIVATE_KEY
        if not vapid_private_key:
            return False, "VAPID_PRIVATE_KEY غير مهيأ في السيرفر"

        vapid_claims = {
            "sub": Config.VAPID_CLAIM_EMAIL or "mailto:contact@nexorasolutions.com"
        }

        user_subs = PushSubscription.query.filter_by(user_id=user_id, is_active=True).all()
        if not user_subs:
            return False, "لا توجد أجهزة مسجلة لهذا الحساب حالياً. يرجى تفعيل الإشعارات أولاً."

        payload = {
            "title": "NEXORA — إشعار تجريبي ناجح 🎉",
            "body": "تم ربط جهازك بنجاح بنظام إشعارات NEXORA Web Push وستصلك الرسائل الجديدة فوراً.",
            "icon": "/icon-192.png",
            "badge": "/favicon.svg",
            "tag": "nexora-test-notification",
            "data": {
                "url": "/inbox",
                "test": True
            }
        }

        sent_count = 0
        for s in user_subs:
            ok = cls.send_push_to_subscription(s.id, payload, vapid_private_key, vapid_claims)
            if ok:
                sent_count += 1

        if sent_count > 0:
            return True, f"تم إرسال إشعار التجربة بنجاح إلى {sent_count} جهاز مسجل."
        else:
            return False, "فشل إرسال الإشعار لجميع الأجهزة المسجلة. قد تكون اشتراكات المتصفح منتهية."
