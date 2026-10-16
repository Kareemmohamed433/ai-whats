from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Conversation, Customer, User, Tag, ConversationTag, Message, ConversationAuditLog, PinnedMessage, PaymentReview
from app.extensions import db
from app.services import SocketService

conversations_bp = Blueprint('conversations', __name__, url_prefix='/api/conversations')

@conversations_bp.route('', methods=['GET'])
@jwt_required()
def get_conversations():
    current_user_id = int(get_jwt_identity())
    filter_type = request.args.get('filter', 'all')
    search = request.args.get('search', '').strip()
    platform = request.args.get('platform')

    query = Conversation.query.join(Customer)

    # Filter by tab / requirement #17
    if filter_type == 'unread':
        query = query.filter(Conversation.unread_count > 0)
    elif filter_type == 'assigned_me':
        query = query.filter(Conversation.assigned_agent_id == current_user_id)
    elif filter_type == 'ai' or filter_type == 'ai_handled':
        query = query.filter(Conversation.ai_status == 'active')
    elif filter_type == 'human' or filter_type == 'human_handled':
        query = query.filter(Conversation.ai_status == 'human_handled')
    elif filter_type == 'human_requests' or filter_type == 'waiting':
        query = query.filter(db.or_(Conversation.requires_human == True, Conversation.ai_status == 'human_handled'))
    elif filter_type == 'pending_payments':
        pending_conv_ids = [r.conversation_id for r in PaymentReview.query.filter_by(status='pending').all() if r.conversation_id]
        query = query.filter(Conversation.id.in_(pending_conv_ids))
    elif filter_type == 'open':
        query = query.filter(Conversation.conversation_status == 'open')
    elif filter_type == 'resolved' or filter_type == 'closed':
        query = query.filter(Conversation.conversation_status == 'closed')

    # Platform filter
    if platform and platform in ['whatsapp', 'instagram', 'tiktok', 'telegram']:
        query = query.filter(Conversation.platform == platform)

    # Search filter
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Customer.name.ilike(pattern),
                Customer.phone.ilike(pattern),
                Customer.email.ilike(pattern),
                Conversation.platform_conversation_id.ilike(pattern)
            )
        )

    conversations = query.order_by(Conversation.last_message_at.desc()).all()
    return jsonify({
        "success": True,
        "conversations": [c.to_dict() for c in conversations]
    })

@conversations_bp.route('/<int:conv_id>', methods=['GET'])
@jwt_required()
def get_conversation_detail(conv_id):
    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المحادثة غير موجودة"}}), 404

    # Reset unread count when opened
    if conv.unread_count > 0:
        conv.unread_count = 0
        db.session.commit()
        SocketService.broadcast_conversation_update(conv)

    return jsonify({
        "success": True,
        "conversation": conv.to_dict(include_messages=True)
    })

@conversations_bp.route('/<int:conv_id>/toggle-ai', methods=['POST'])
@jwt_required()
def toggle_ai(conv_id):
    current_user_id = str(get_jwt_identity())
    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المحادثة غير موجودة"}}), 404

    data = request.get_json() or {}
    target_status = data.get('ai_status')
    if not target_status:
        target_status = 'human_handled' if conv.ai_status == 'active' else 'active'

    prev_ai = conv.ai_status
    conv.ai_status = target_status
    if target_status == 'active':
        conv.requires_human = False
        conv.ai_enabled_at = datetime.utcnow()
    elif target_status == 'human_handled':
        conv.requires_human = True
        conv.human_handoff_at = datetime.utcnow()

    audit = ConversationAuditLog(
        conversation_id=conv.id,
        actor_type='agent',
        actor_id=current_user_id,
        previous_ai_status=prev_ai,
        new_ai_status=conv.ai_status,
        previous_conv_status=conv.conversation_status,
        new_conv_status=conv.conversation_status,
        reason='agent_toggled_ai_status'
    )
    db.session.add(audit)
    db.session.commit()

    SocketService.broadcast_ai_status_changed(conv, prev_ai, conv.ai_status)
    SocketService.broadcast_conversation_update(conv)

    return jsonify({
        "success": True,
        "message": f"تم {'تفعيل' if conv.ai_status == 'active' else 'إيقاف'} الذكاء الاصطناعي للمحادثة.",
        "conversation": conv.to_dict()
    })

@conversations_bp.route('/<int:conv_id>/status', methods=['PUT'])
@jwt_required()
def update_status(conv_id):
    current_user_id = str(get_jwt_identity())
    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المحادثة غير موجودة"}}), 404

    data = request.get_json() or {}
    
    prev_conv_status = conv.conversation_status
    prev_ai_status = conv.ai_status

    new_conv_status = data.get('conversation_status') or data.get('status')
    new_ai_status = data.get('ai_status')
    priority = data.get('priority')
    agent_id = data.get('assigned_agent_id')
    reason = data.get('reason', 'agent_action')

    # Update conversation_status if provided
    if new_conv_status in ['open', 'closed', 'resolved']:
        actual_conv_status = 'closed' if new_conv_status in ['closed', 'resolved'] else 'open'
        conv.conversation_status = actual_conv_status
        if actual_conv_status == 'closed':
            conv.closed_at = datetime.utcnow()
        elif actual_conv_status == 'open':
            conv.closed_at = None

    # Update ai_status if provided
    if new_ai_status in ['active', 'human_handled', 'disabled']:
        conv.ai_status = new_ai_status
        if new_ai_status == 'human_handled':
            conv.requires_human = True
            conv.human_handoff_at = datetime.utcnow()
        elif new_ai_status == 'active':
            conv.requires_human = False
            conv.ai_enabled_at = datetime.utcnow()

    # Legacy helper boolean
    if 'ai_enabled' in data and new_ai_status is None:
        conv.ai_status = 'active' if data['ai_enabled'] else 'human_handled'

    if priority:
        conv.priority = priority
    if agent_id is not None:
        conv.assigned_agent_id = agent_id if agent_id != 0 else None

    # Audit log
    audit = ConversationAuditLog(
        conversation_id=conv.id,
        actor_type='agent',
        actor_id=current_user_id,
        previous_conv_status=prev_conv_status,
        new_conv_status=conv.conversation_status,
        previous_ai_status=prev_ai_status,
        new_ai_status=conv.ai_status,
        reason=reason
    )
    db.session.add(audit)
    db.session.commit()

    # Emit Socket.IO events
    if prev_conv_status != conv.conversation_status:
        SocketService.broadcast_conversation_status_changed(conv, prev_conv_status, conv.conversation_status)

    if prev_ai_status != conv.ai_status:
        SocketService.broadcast_ai_status_changed(conv, prev_ai_status, conv.ai_status)
        if conv.ai_status == 'human_handled':
            SocketService.broadcast_human_handoff(conv, reason)

    SocketService.broadcast_conversation_update(conv)

    return jsonify({
        "success": True,
        "conversation": conv.to_dict()
    })

@conversations_bp.route('/<int:conv_id>/assign', methods=['PUT'])
@jwt_required()
def assign_agent(conv_id):
    data = request.get_json() or {}
    agent_id = data.get('assigned_agent_id')
    
    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المحادثة غير موجودة"}}), 404

    conv.assigned_agent_id = agent_id if (agent_id and agent_id != 0) else None
    db.session.commit()

    SocketService.broadcast_conversation_update(conv)
    return jsonify({"success": True, "conversation": conv.to_dict()})

@conversations_bp.route('/<int:conv_id>/pin', methods=['POST'])
@jwt_required()
def toggle_pin_message(conv_id):
    agent_id = int(get_jwt_identity())
    data = request.get_json() or {}
    message_id = data.get('message_id')
    note = data.get('note', '')

    if not message_id:
        return jsonify({"success": False, "error": {"code": "INVALID_DATA", "message": "معرف الرسالة مطلوب."}}), 400

    existing = PinnedMessage.query.filter_by(conversation_id=conv_id, message_id=message_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"success": True, "pinned": False, "message": "تم إزالة تثبيت الرسالة"})

    pinned = PinnedMessage(
        conversation_id=conv_id,
        message_id=message_id,
        pinned_by_agent_id=agent_id,
        note=note
    )
    db.session.add(pinned)
    db.session.commit()
    return jsonify({"success": True, "pinned": True, "pinned_message": pinned.to_dict()})

@conversations_bp.route('/<int:conv_id>/pinned', methods=['GET'])
@jwt_required()
def get_pinned_messages(conv_id):
    pinned = PinnedMessage.query.filter_by(conversation_id=conv_id).order_by(PinnedMessage.created_at.desc()).all()
    return jsonify({
        "success": True,
        "pinned_messages": [p.to_dict() for p in pinned]
    })
