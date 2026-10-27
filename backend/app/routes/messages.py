from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Message, MessageAttachment, Conversation, InternalNote, User, Customer
from app.extensions import db
from app.config import Config
from app.services import SocketService, WhatsAppService, TelegramService, InstagramService, TikTokService

messages_bp = Blueprint('messages', __name__, url_prefix='/api/messages')

@messages_bp.route('', methods=['POST'])
@jwt_required()
def send_message():
    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    conv_id = data.get('conversation_id')
    content = (data.get('content') or '').strip()
    message_type = data.get('message_type', 'text')
    media_url = data.get('media_url')
    attachments_data = data.get('attachments') or []
    attachment_ids = data.get('attachment_ids') or []

    if not conv_id or (not content and not media_url and not attachments_data and not attachment_ids):
        return jsonify({"success": False, "error": {"code": "INVALID_REQUEST", "message": "المحادثة ونص الرسالة أو المرفق مطلوب."}}), 400

    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المحادثة غير موجودة"}}), 404

    user = User.query.get(current_user_id)
    sender_name = user.name if (user and user.name) else "موظف الدعم"

    # Dynamic template variables replacement
    customer_name = conv.customer.name if (conv.customer and conv.customer.name) else "العميل"
    if content:
        content = content.replace("{{agent_name}}", sender_name).replace("{{customer_name}}", customer_name)

    # Infer message type from attachments if not explicitly specified
    if message_type == 'text' and attachments_data:
        first_att = attachments_data[0]
        f_type = first_att.get('file_type', 'document')
        message_type = f_type if f_type in ('image', 'video', 'document', 'audio') else 'document'
        if not media_url:
            media_url = first_att.get('file_url')

    if not content and attachments_data:
        first_name = attachments_data[0].get('file_name') or 'ملف مرفق'
        content = f"مرفق: {first_name}"

    # Create message model
    msg = Message(
        conversation_id=conv_id,
        sender_type='agent',
        sender_id=str(current_user_id),
        sender_name=sender_name,
        content=content or "مرفق",
        message_type=message_type,
        media_url=media_url,
        status='sent'
    )

    conv.last_message_at = datetime.utcnow()
    # Keep ai_status = human_handled when agent replies
    if conv.ai_status == 'active':
        conv.ai_status = 'human_handled'
        conv.requires_human = True
        conv.human_handoff_at = datetime.utcnow()
    
    db.session.add(msg)
    db.session.flush()

    # Link/create message attachments
    for att_data in attachments_data:
        new_att = MessageAttachment(
            message_id=msg.id,
            conversation_id=conv.id,
            file_type=att_data.get('file_type', 'document'),
            file_url=att_data.get('file_url', ''),
            file_name=att_data.get('file_name'),
            file_size=att_data.get('file_size'),
            storage_key=att_data.get('storage_key'),
            mime_type=att_data.get('mime_type'),
            direction='outbound',
            status='completed'
        )
        db.session.add(new_att)

    # If attachment_ids were passed, link them to msg.id
    for aid in attachment_ids:
        existing_att = MessageAttachment.query.get(aid)
        if existing_att and not existing_att.message_id:
            existing_att.message_id = msg.id
            existing_att.conversation_id = conv.id
            # FIX: backfill msg fields so WhatsApp dispatch can see the media
            if not msg.media_url and existing_att.file_url:
                msg.media_url = existing_att.file_url
            if msg.message_type == 'text' and existing_att.file_type in ('image', 'video', 'document', 'audio'):
                msg.message_type = existing_att.file_type

    db.session.commit()

    # Dispatch to platform API channel (Channel Independence)
    customer = conv.customer
    recipient = (customer.phone if customer else None) or conv.platform_conversation_id
    try:
        if conv.platform == 'whatsapp':
            if msg.message_type in ('image', 'video', 'document', 'audio') and msg.media_url:
                # Build full URL if relative — must use BACKEND_URL so Meta can fetch the file
                full_media_url = msg.media_url
                if full_media_url.startswith('/'):
                    base = (
                        getattr(Config, 'BACKEND_URL', None)
                        or getattr(Config, 'BASE_URL', None)
                        or getattr(Config, 'FRONTEND_URL', None)
                        or ''
                    ).rstrip('/')
                    full_media_url = f"{base}{full_media_url}"
                # Use file_name from attachments_data first, then fall back to linked attachment records
                first_filename = None
                if attachments_data:
                    first_filename = attachments_data[0].get('file_name')
                elif msg.attachments:
                    first_filename = msg.attachments[0].file_name
                WhatsAppService.send_media(
                    recipient=recipient,
                    media_type=msg.message_type,
                    media_url=full_media_url,
                    caption=content if content != f"مرفق: {first_filename}" else None,
                    filename=first_filename
                )
            else:
                WhatsAppService.send_message(recipient, content)
        elif conv.platform == 'telegram':
            TelegramService.send_message(conv.platform_conversation_id, content)
        elif conv.platform == 'instagram':
            InstagramService.send_message(conv.platform_conversation_id, content)
        elif conv.platform == 'tiktok' and TikTokService:
            TikTokService.send_message(conv.platform_conversation_id, content)
    except Exception as platform_err:
        # Log but don't fail the request — message is already saved
        import traceback
        print(f"[PLATFORM DISPATCH ERROR] conv={conv_id} platform={conv.platform}: {platform_err}")
        traceback.print_exc()

    # Real-time WebSocket emissions
    SocketService.broadcast_agent_message(msg)
    SocketService.broadcast_new_message(msg)
    SocketService.broadcast_conversation_update(conv)

    return jsonify({
        "success": True,
        "message": msg.to_dict()
    }), 201

@messages_bp.route('/note', methods=['POST'])
@jwt_required()
def add_internal_note():
    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    conv_id = data.get('conversation_id')
    content = data.get('content', '').strip()

    if not conv_id or not content:
        return jsonify({"success": False, "error": {"code": "INVALID_REQUEST", "message": "المحادثة ومحتوى الملاحظة مطلوبان."}}), 400

    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المحادثة غير موجودة"}}), 404

    note = InternalNote(
        conversation_id=conv_id,
        author_id=current_user_id,
        content=content
    )
    db.session.add(note)
    db.session.commit()

    # Broadcast conversation update
    SocketService.broadcast_conversation_update(conv)

    return jsonify({
        "success": True,
        "note": note.to_dict()
    }), 201