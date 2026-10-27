import traceback
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Message, MessageAttachment, Conversation, InternalNote, User, Customer
from app.extensions import db
from app.config import Config
from app.services import SocketService, WhatsAppService, TelegramService, InstagramService, TikTokService

messages_bp = Blueprint('messages', __name__, url_prefix='/api/messages')


def _build_public_media_url(att_record, fallback_url):
    """
    Build a public (no-auth) URL that Meta can fetch.

    Always uses BACKEND_URL (the Railway domain). FRONTEND_URL is intentionally
    NOT used: the files live on the backend, not on Vercel.
    Prefers /api/attachments/preview/<storage_key>, which has no @jwt_required.
    """
    base = (getattr(Config, 'BACKEND_URL', '') or '').rstrip('/')
    if not base:
        raise RuntimeError("BACKEND_URL is not configured")

    if att_record and getattr(att_record, 'storage_key', None):
        return f"{base}/api/attachments/preview/{att_record.storage_key}"

    # Fallback: make absolute if relative
    url = fallback_url or ''
    if url.startswith('/'):
        return f"{base}{url}"
    return url


class _AttRef:
    """Light stand-in for an attachment record when only request data is available."""
    def __init__(self, storage_key, file_name):
        self.storage_key = storage_key
        self.file_name = file_name


def _collect_media_items(msg, attachments_data):
    """
    Return ALL media of a message as a list of dicts:
    {type, file_url, file_name, record}
    Sources, in order of preference: saved attachment rows -> request payload -> msg.media_url.
    """
    valid = ('image', 'video', 'document', 'audio')
    items = []

    if msg.attachments:
        for att in sorted(msg.attachments, key=lambda a: a.id or 0):
            ftype = att.file_type if att.file_type in valid else 'document'
            items.append({
                'type': ftype,
                'file_url': att.file_url,
                'file_name': att.file_name,
                'record': att,
            })
    elif attachments_data:
        for a in attachments_data:
            ftype = a.get('file_type', 'document')
            ftype = ftype if ftype in valid else 'document'
            items.append({
                'type': ftype,
                'file_url': a.get('file_url'),
                'file_name': a.get('file_name'),
                'record': _AttRef(a.get('storage_key'), a.get('file_name')),
            })
    elif msg.message_type in valid and msg.media_url:
        items.append({
            'type': msg.message_type,
            'file_url': msg.media_url,
            'file_name': None,
            'record': None,
        })

    return items


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

    auto_caption = False
    if not content and attachments_data:
        first_name = attachments_data[0].get('file_name') or 'ملف مرفق'
        content = f"مرفق: {first_name}"
        auto_caption = True

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

    # If attachment_ids were passed, link them to msg.id and backfill msg fields
    for aid in attachment_ids:
        existing_att = MessageAttachment.query.get(aid)
        if existing_att and not existing_att.message_id:
            existing_att.message_id = msg.id
            existing_att.conversation_id = conv.id
            # Backfill msg so WhatsApp dispatch can see the media
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
            media_items = _collect_media_items(msg, attachments_data)
            if media_items:
                # WhatsApp allows ONE media per message -> send each attachment separately.
                # The caption (agent text) is attached to the first item only.
                for idx, item in enumerate(media_items):
                    public_url = _build_public_media_url(item['record'], item['file_url'])
                    caption = content if (idx == 0 and not auto_caption) else None

                    print(f"[WhatsApp Media Dispatch {idx + 1}/{len(media_items)}] "
                          f"type={item['type']} url={public_url}")

                    result = WhatsAppService.send_media(
                        recipient=recipient,
                        media_type=item['type'],
                        media_url=public_url,
                        caption=caption,
                        filename=item['file_name']
                    )
                    if not result.get("success"):
                        print(f"[WhatsApp Media FAILED] conv={conv_id} item={idx + 1}: {result}")
            else:
                WhatsAppService.send_message(recipient, content)
        elif conv.platform == 'telegram':
            TelegramService.send_message(conv.platform_conversation_id, content)
        elif conv.platform == 'instagram':
            InstagramService.send_message(conv.platform_conversation_id, content)
        elif conv.platform == 'tiktok' and TikTokService:
            TikTokService.send_message(conv.platform_conversation_id, content)
    except Exception as platform_err:
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