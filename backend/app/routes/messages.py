from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Message, Conversation, InternalNote, User, Customer
from app.extensions import db
from app.services import SocketService, WhatsAppService, TelegramService, InstagramService, TikTokService

messages_bp = Blueprint('messages', __name__, url_prefix='/api/messages')

@messages_bp.route('', methods=['POST'])
@jwt_required()
def send_message():
    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    conv_id = data.get('conversation_id')
    content = data.get('content', '').strip()
    message_type = data.get('message_type', 'text')
    media_url = data.get('media_url')

    if not conv_id or not content:
        return jsonify({"success": False, "error": {"code": "INVALID_REQUEST", "message": "المحادثة ونص الرسالة مطلوبان."}}), 400

    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المحادثة غير موجودة"}}), 404

    user = User.query.get(current_user_id)
    sender_name = user.name if (user and user.name) else "موظف الدعم"

    # Requirement #2: Dynamic template variables replacement
    customer_name = conv.customer.name if (conv.customer and conv.customer.name) else "العميل"
    content = content.replace("{{agent_name}}", sender_name).replace("{{customer_name}}", customer_name)

    # Create message model
    msg = Message(
        conversation_id=conv_id,
        sender_type='agent',
        sender_id=str(current_user_id),
        sender_name=sender_name,
        content=content,
        message_type=message_type,
        media_url=media_url,
        status='sent'
    )

    conv.last_message_at = datetime.utcnow()
    # Requirement #4: Keep ai_status = human_handled when agent replies
    if conv.ai_status == 'active':
        conv.ai_status = 'human_handled'
        conv.requires_human = True
        conv.human_handoff_at = datetime.utcnow()
    
    db.session.add(msg)
    db.session.commit()

    # Dispatch to platform API channel (Requirement #12: Channel Independence)
    customer = conv.customer
    if conv.platform == 'whatsapp':
        WhatsAppService.send_message(customer.phone or conv.platform_conversation_id, content)
    elif conv.platform == 'telegram':
        TelegramService.send_message(conv.platform_conversation_id, content)
    elif conv.platform == 'instagram':
        InstagramService.send_message(conv.platform_conversation_id, content)
    elif conv.platform == 'tiktok':
        TikTokService.send_message(conv.platform_conversation_id, content)

    # Real-time WebSocket emissions (Requirement #10)
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
