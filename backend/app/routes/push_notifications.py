from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.config import Config
from app.extensions import db
from app.models.push_subscription import PushSubscription
from app.models.notification_preference import NotificationPreference
from app.services.notification_service import NotificationService

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')
push_alias_bp = Blueprint('push_alias', __name__, url_prefix='/api/push')


def _get_current_user_id():
    identity = get_jwt_identity()
    try:
        return int(identity)
    except (ValueError, TypeError):
        return identity


def _get_vapid_keys():
    pub = getattr(Config, "VAPID_PUBLIC_KEY", "")
    priv = getattr(Config, "VAPID_PRIVATE_KEY", "")
    try:
        if current_app:
            pub = current_app.config.get("VAPID_PUBLIC_KEY", pub)
            priv = current_app.config.get("VAPID_PRIVATE_KEY", priv)
    except Exception:
        pass
    return pub, priv


# --- VAPID PUBLIC KEY ---
@notifications_bp.route('/vapid-public-key', methods=['GET'])
@push_alias_bp.route('/vapid-public-key', methods=['GET'])
def get_vapid_public_key():
    """Return public VAPID key for browser PushManager subscription."""
    public_key, _ = _get_vapid_keys()
    return jsonify({
        "configured": bool(public_key),
        "public_key": public_key
    }), 200


# --- SUBSCRIPTION STATUS ---
@notifications_bp.route('/status', methods=['GET'])
@push_alias_bp.route('/status', methods=['GET'])
@jwt_required()
def get_notification_status():
    """Get active push subscriptions and preferences for authenticated user."""
    user_id = _get_current_user_id()
    pref = NotificationService.get_user_preferences(user_id)
    subscriptions = PushSubscription.query.filter_by(user_id=user_id, is_active=True).order_by(PushSubscription.last_used_at.desc()).all()
    pub, priv = _get_vapid_keys()

    return jsonify({
        "vapid_configured": bool(pub and priv),
        "preferences": pref.to_dict(),
        "devices_count": len(subscriptions),
        "devices": [s.to_dict() for s in subscriptions]
    }), 200


# --- SUBSCRIBE ---
@notifications_bp.route('/subscribe', methods=['POST'])
@push_alias_bp.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe_device():
    """Register or reactivate Web Push subscription for authenticated user."""
    user_id = _get_current_user_id()
    data = request.get_json() or {}

    endpoint = data.get('endpoint')
    keys = data.get('keys', {})
    p256dh = keys.get('p256dh')
    auth = keys.get('auth')
    device_name = data.get('device_name') or "جهاز غير محدد"
    user_agent = request.headers.get('User-Agent', '')[:250]

    if not endpoint or not p256dh or not auth:
        return jsonify({
            "error": "بيانات الاشتراك غير مكتملة (endpoint, p256dh, auth مطلوبة)"
        }), 400

    # Check existing subscription by endpoint
    sub = PushSubscription.query.filter_by(endpoint=endpoint).first()
    if sub:
        sub.user_id = user_id
        sub.p256dh_key = p256dh
        sub.auth_key = auth
        sub.device_name = device_name
        sub.user_agent = user_agent
        sub.is_active = True
    else:
        sub = PushSubscription(
            user_id=user_id,
            endpoint=endpoint,
            p256dh_key=p256dh,
            auth_key=auth,
            device_name=device_name,
            user_agent=user_agent,
            is_active=True
        )
        db.session.add(sub)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "تم تفعيل اشتراك الإشعارات للجهاز بنجاح",
        "subscription": sub.to_dict()
    }), 201


# --- UNSUBSCRIBE ---
@notifications_bp.route('/unsubscribe', methods=['POST'])
@push_alias_bp.route('/unsubscribe', methods=['POST'])
@jwt_required()
def unsubscribe_device():
    """Deactivate subscription for current user."""
    user_id = _get_current_user_id()
    data = request.get_json() or {}

    endpoint = data.get('endpoint')
    subscription_id = data.get('subscription_id')

    query = PushSubscription.query.filter_by(user_id=user_id)
    if endpoint:
        query = query.filter_by(endpoint=endpoint)
    elif subscription_id:
        query = query.filter_by(id=subscription_id)
    else:
        return jsonify({"error": "يرجى تحديد endpoint أو subscription_id لإلغاء الاشتراك"}), 400

    sub = query.first()
    if sub:
        sub.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "تم إلغاء الاشتراك بنجاح"}), 200

    return jsonify({"error": "الاشتراك غير موجود"}), 404


# --- PREFERENCES GET & PUT ---
@notifications_bp.route('/preferences', methods=['GET'])
@push_alias_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """Get notification preferences for authenticated user."""
    user_id = _get_current_user_id()
    pref = NotificationService.get_user_preferences(user_id)
    return jsonify(pref.to_dict()), 200


@notifications_bp.route('/preferences', methods=['PUT'])
@push_alias_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    """Update notification preferences for authenticated user."""
    user_id = _get_current_user_id()
    pref = NotificationService.get_user_preferences(user_id)
    data = request.get_json() or {}

    if 'desktop_enabled' in data:
        pref.desktop_enabled = bool(data['desktop_enabled'])
    if 'mobile_push_enabled' in data:
        pref.mobile_push_enabled = bool(data['mobile_push_enabled'])
    if 'sound_enabled' in data:
        pref.sound_enabled = bool(data['sound_enabled'])
    if 'preview_enabled' in data:
        pref.preview_enabled = bool(data['preview_enabled'])
    if 'notify_on_all' in data:
        pref.notify_on_all = bool(data['notify_on_all'])
    if 'notify_on_assigned_only' in data:
        pref.notify_on_assigned_only = bool(data['notify_on_assigned_only'])
    if 'muted_conversations' in data:
        pref.set_muted_conversations(data['muted_conversations'])

    db.session.commit()
    return jsonify({
        "success": True,
        "message": "تم حفظ تفضيلات الإشعارات بنجاح",
        "preferences": pref.to_dict()
    }), 200


# --- TEST NOTIFICATION ---
@notifications_bp.route('/test', methods=['POST'])
@push_alias_bp.route('/test', methods=['POST'])
@jwt_required()
def test_notification():
    """Send an immediate test push notification to user's registered devices."""
    user_id = _get_current_user_id()
    success, message = NotificationService.send_test_notification(user_id)
    status_code = 200 if success else 400
    return jsonify({
        "success": success,
        "message": message
    }), status_code


# --- DELETE REGISTERED DEVICE ---
@notifications_bp.route('/devices/<int:device_id>', methods=['DELETE'])
@push_alias_bp.route('/devices/<int:device_id>', methods=['DELETE'])
@jwt_required()
def delete_device(device_id):
    """Permanently delete device subscription owned by user."""
    user_id = _get_current_user_id()
    sub = PushSubscription.query.filter_by(id=device_id, user_id=user_id).first()
    if not sub:
        return jsonify({"error": "الجهاز غير موجود أو غير مصرح بحذفه"}), 404

    db.session.delete(sub)
    db.session.commit()
    return jsonify({"success": True, "message": "تم حذف الجهاز بنجاح"}), 200
