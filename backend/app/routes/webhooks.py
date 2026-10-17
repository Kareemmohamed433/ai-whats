from datetime import datetime
from flask import Blueprint, request, jsonify
from app.models import Conversation, Customer, CustomerIdentity, Message, CustomerActivity, ConversationAuditLog
from app.extensions import db
from app.config import Config
from app.services import AIService, WhatsAppService, TelegramService, InstagramService, SocketService

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/api/webhooks')
telegram_api_bp = Blueprint('telegram_api', __name__, url_prefix='/api/telegram')

# --- WHATSAPP WEBHOOK ---
@webhooks_bp.route('/whatsapp', methods=['GET'], strict_slashes=False)
def verify_whatsapp_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == Config.WHATSAPP_VERIFY_TOKEN:
        return challenge, 200
    return jsonify({"error": "Forbidden"}), 403

@webhooks_bp.route('/whatsapp', methods=['POST'], strict_slashes=False)
def handle_whatsapp_webhook():
    data = request.get_json() or {}
    try:
        entries = data.get('entry', [])
        for entry in entries:
            changes = entry.get('changes', [])
            for change in changes:
                value = change.get('value', {})
                messages = value.get('messages', [])
                contacts = value.get('contacts', [])

                for msg_data in messages:
                    phone = msg_data.get('from')
                    text = msg_data.get('text', {}).get('body', '')
                    msg_type = msg_data.get('type', 'text')
                    msg_id = msg_data.get('id')
                    sender_name = contacts[0].get('profile', {}).get('name', phone) if contacts else phone

                    _process_incoming_message(
                        platform='whatsapp',
                        platform_user_id=phone,
                        customer_name=sender_name,
                        phone=phone,
                        content=text,
                        msg_type=msg_type,
                        platform_msg_id=msg_id
                    )
    except Exception as e:
        print(f"WhatsApp webhook parse error: {e}")

    return jsonify({"status": "EVENT_RECEIVED"}), 200

# --- TELEGRAM WEBHOOK ---
@webhooks_bp.route('/telegram', methods=['POST'], strict_slashes=False)
@telegram_api_bp.route('/webhook', methods=['POST'], strict_slashes=False)
def handle_telegram_webhook():
    print("Telegram webhook received")
    data = request.get_json() or {}
    try:
        msg = data.get('message', {})
        if msg:
            chat_id = str(msg.get('chat', {}).get('id'))
            text = msg.get('text', '') or msg.get('caption', '')
            user = msg.get('from', {})
            first_name = user.get('first_name', '')
            last_name = user.get('last_name', '')
            username = user.get('username')
            sender_name = f"{first_name} {last_name}".strip() or username or chat_id

            msg_type = 'text'
            media_url = None

            # Requirement #18: Handle Telegram photo attachments
            photos = msg.get('photo')
            if photos and isinstance(photos, list) and len(photos) > 0:
                msg_type = 'image'
                best_photo = photos[-1]
                file_id = best_photo.get('file_id')
                if hasattr(TelegramService, 'get_file_url'):
                    media_url = TelegramService.get_file_url(file_id)
                if not text:
                    text = "صورة مرفقة عبر تيليجرام"

            _process_incoming_message(
                platform='telegram',
                platform_user_id=chat_id,
                customer_name=sender_name,
                username=username,
                content=text,
                msg_type=msg_type,
                media_url=media_url,
                platform_msg_id=str(msg.get('message_id'))
            )
    except Exception as e:
        print(f"Telegram webhook parse error: {e}")

    return jsonify({"status": "OK"}), 200

# --- INSTAGRAM WEBHOOK ---
@webhooks_bp.route('/instagram', methods=['GET'], strict_slashes=False)
def verify_instagram_webhook():
    mode = request.args.get('hub.mode') or request.args.get('hub_mode')
    token = request.args.get('hub.verify_token') or request.args.get('hub_verify_token')
    challenge = request.args.get('hub.challenge') or request.args.get('hub_challenge')

    expected_token = Config.INSTAGRAM_VERIFY_TOKEN

    print(f"[Instagram Webhook Verification] Mode: {repr(mode)}")
    print(f"[Instagram Webhook Verification] Token received: {repr(token)}")
    print(f"[Instagram Webhook Verification] Token expected: {repr(expected_token)}")
    print(f"[Instagram Webhook Verification] Challenge: {repr(challenge)}")
    print(f"[Instagram Webhook Verification] Token match: {token == expected_token}")

    if mode == 'subscribe' and token and (token == expected_token or token == Config.WHATSAPP_VERIFY_TOKEN):
        return str(challenge), 200, {'Content-Type': 'text/plain'}

    return jsonify({"error": "Forbidden"}), 403

@webhooks_bp.route('/instagram', methods=['POST'], strict_slashes=False)
def handle_instagram_webhook():
    data = request.get_json() or {}
    print(f"[Instagram Webhook POST] Received payload: {data}")
    try:
        entries = data.get('entry', [])
        for entry in entries:
            messaging = entry.get('messaging', [])
            for msg_item in messaging:
                sender_id = str(msg_item.get('sender', {}).get('id', ''))
                recipient_id = str(msg_item.get('recipient', {}).get('id', ''))
                message = msg_item.get('message', {})

                # Ignore echo messages sent by our bot/page
                if message.get('is_echo'):
                    print(f"[Instagram Webhook] Ignoring echo message from {sender_id}")
                    continue

                # Ignore bot's own account ID
                our_account_id = str(Config.INSTAGRAM_ACCOUNT_ID)
                if sender_id and sender_id == our_account_id:
                    print(f"[Instagram Webhook] Ignoring message from our account ID {sender_id}")
                    continue

                text = message.get('text', '')
                msg_id = message.get('mid')
                attachments = message.get('attachments', [])
                msg_type = 'text'
                media_url = None

                if not text and attachments:
                    first_att = attachments[0]
                    att_type = first_att.get('type')
                    media_url = first_att.get('payload', {}).get('url')
                    if att_type == 'image':
                        msg_type = 'image'
                        text = "صورة مرفقة من إنستغرام"
                    else:
                        msg_type = att_type or 'document'
                        text = f"مرفق {att_type} من إنستغرام"

                if sender_id and text:
                    _process_incoming_message(
                        platform='instagram',
                        platform_user_id=sender_id,
                        customer_name=f"عميل إنستغرام ({sender_id[-4:]})",
                        username=f"ig_{sender_id[-4:]}",
                        content=text,
                        msg_type=msg_type,
                        media_url=media_url,
                        platform_msg_id=msg_id
                    )
    except Exception as e:
        print(f"Instagram webhook parse error: {e}")

    return jsonify({"status": "EVENT_RECEIVED"}), 200

# --- TIKTOK WEBHOOK ---
@webhooks_bp.route('/tiktok', methods=['POST'])
def handle_tiktok_webhook():
    data = request.get_json() or {}
    return jsonify({"status": "SUCCESS", "message": "TikTok webhook endpoint active"}), 200

# --- UNIFIED PROCESSING PIPELINE ---
def _process_incoming_message(platform, platform_user_id, customer_name, phone=None, email=None, username=None, content="", msg_type="text", platform_msg_id=None, media_url=None):
    from app.services.ai_service import HANDOFF_MESSAGE, AIService

    # 1. Identify/Create Customer Identity & Customer (Requirement #3)
    identity = CustomerIdentity.query.filter_by(platform=platform, platform_user_id=platform_user_id).first()
    is_new_customer = False
    if identity:
        customer = identity.customer
    else:
        customer = None
        if phone:
            customer = Customer.query.filter_by(phone=phone).first()

        if not customer:
            customer = Customer(
                name=customer_name,
                phone=phone,
                email=email,
                avatar=f"https://ui-avatars.com/api/?name={customer_name.replace(' ', '+')}&background=1E6BFF&color=fff"
            )
            db.session.add(customer)
            db.session.flush()
            is_new_customer = True

        identity = CustomerIdentity(
            customer_id=customer.id,
            platform=platform,
            platform_user_id=platform_user_id,
            username=username
        )
        db.session.add(identity)
        db.session.commit()

    # 2. Identify/Create Conversation
    conv = Conversation.query.filter_by(customer_id=customer.id, platform=platform).first()
    if not conv:
        conv = Conversation(
            customer_id=customer.id,
            platform=platform,
            platform_conversation_id=platform_user_id,
            conversation_status='open',
            ai_status='active',
            priority='medium',
            unread_count=0
        )
        db.session.add(conv)
        db.session.flush()

    # Requirement #22: Webhook Deduplication check
    if platform_msg_id:
        existing_msg = Message.query.filter_by(conversation_id=conv.id, platform_message_id=str(platform_msg_id)).first()
        if existing_msg:
            print(f"[Webhook Deduplication] Message {platform_msg_id} already exists for conversation {conv.id}. Skipping.")
            return conv

    # Reopening logic if conversation was closed (Requirements #6 & #7)
    if conv.conversation_status == 'closed':
        conv.conversation_status = 'open'
        conv.closed_at = None

        audit = ConversationAuditLog(
            conversation_id=conv.id,
            actor_type='customer',
            actor_id=platform_user_id,
            previous_conv_status='closed',
            new_conv_status='open',
            previous_ai_status=conv.ai_status,
            new_ai_status=conv.ai_status,
            reason='reopened_by_new_customer_message'
        )
        db.session.add(audit)
        SocketService.broadcast_conversation_status_changed(conv, 'closed', 'open')

    conv.last_message_at = datetime.utcnow()
    conv.unread_count += 1

    # 3. Store Incoming Customer Message
    cust_msg = Message(
        conversation_id=conv.id,
        platform_message_id=platform_msg_id,
        sender_type='customer',
        sender_id=platform_user_id,
        content=content,
        message_type=msg_type,
        media_url=media_url,
        status='received'
    )
    db.session.add(cust_msg)
    db.session.commit()

    # Broadcast to dashboard in real-time
    SocketService.broadcast_new_message(cust_msg)
    SocketService.broadcast_conversation_update(conv)

    # 4. AI Service Pipeline (Requirement #8, #9, #11, #12, #16)
    if conv.ai_status == 'active':
        ai_reply = AIService.generate_response(conv.id, content, is_media=(msg_type != 'text'), media_url=media_url)
        if ai_reply:
            # Race condition protection: Re-query conversation state (Requirement #16)
            db.session.refresh(conv)
            is_handoff_response = (ai_reply == HANDOFF_MESSAGE)

            if conv.ai_status == 'active' or is_handoff_response:
                ai_msg = Message(
                    conversation_id=conv.id,
                    sender_type='ai',
                    content=ai_reply,
                    message_type='text',
                    status='sent'
                )
                db.session.add(ai_msg)
                db.session.commit()

                # Dispatch AI response back to customer's platform channel
                if platform == 'whatsapp':
                    WhatsAppService.send_message(phone or platform_user_id, ai_reply)
                elif platform == 'telegram':
                    TelegramService.send_message(platform_user_id, ai_reply)
                elif platform == 'instagram':
                    InstagramService.send_message(platform_user_id, ai_reply)
                elif platform == 'tiktok':
                    TikTokService.send_message(platform_user_id, ai_reply)

                # Broadcast AI message to dashboard
                SocketService.broadcast_new_message(ai_msg)
                SocketService.broadcast_conversation_update(conv)
            else:
                print(f"[Race Protection] Suppressed AI response for conv {conv.id} because ai_status changed to '{conv.ai_status}'")

    return conv
