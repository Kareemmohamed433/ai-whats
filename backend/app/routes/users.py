from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Conversation, Message
from app.extensions import db

users_bp = Blueprint('users', __name__, url_prefix='/api/users')
agents_bp = Blueprint('agents', __name__, url_prefix='/api/agents')

def _format_user(u):
    data = u.to_dict()
    assigned = Conversation.query.filter_by(assigned_agent_id=u.id).count()
    active_human = Conversation.query.filter_by(assigned_agent_id=u.id, ai_status='human_handled', conversation_status='open').count()
    
    # Calculate last reply sent by user
    last_msg = Message.query.filter_by(sender_type='agent', sender_id=str(u.id)).order_by(Message.created_at.desc()).first()
    last_reply_at = None
    last_reply_customer_name = None
    last_reply_conv_id = None

    if last_msg:
        last_reply_at = last_msg.created_at.isoformat()
        conv = Conversation.query.get(last_msg.conversation_id)
        if conv:
            last_reply_conv_id = conv.id
            if conv.customer:
                last_reply_customer_name = conv.customer.name

    # Calculate replies sent today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    replies_today = Message.query.filter(
        Message.sender_type == 'agent',
        Message.sender_id == str(u.id),
        Message.created_at >= today_start
    ).count()

    # Automatic status calculation
    now = datetime.utcnow()
    computed_status = u.status or 'offline'
    if u.last_seen_at:
        diff_minutes = (now - u.last_seen_at).total_seconds() / 60.0
        if diff_minutes <= 2:
            computed_status = 'online'
        elif diff_minutes <= 5:
            computed_status = 'away'
        else:
            computed_status = 'offline'

    if active_human >= 5 and computed_status == 'online':
        computed_status = 'busy'

    data['assigned_chats'] = assigned
    data['active_chats'] = active_human
    data['last_reply_at'] = last_reply_at
    data['last_reply_customer_name'] = last_reply_customer_name
    data['last_reply_conv_id'] = last_reply_conv_id
    data['replies_today_count'] = replies_today
    data['computed_status'] = computed_status
    return data

@users_bp.route('', methods=['GET'])
@agents_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.order_by(User.id.asc()).all()
    return jsonify({
        "success": True,
        "users": [_format_user(u) for u in users],
        "agents": [_format_user(u) for u in users]
    })

@users_bp.route('', methods=['POST'])
@agents_bp.route('', methods=['POST'])
@jwt_required()
def create_user():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    name = data.get('name', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', 'agent')

    if not email or not name or not password:
        return jsonify({
            "success": False,
            "error": {"code": "MISSING_FIELDS", "message": "جميع الحقول المطلوبة يجب إدخالها."}
        }), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({
            "success": False,
            "error": {"code": "EMAIL_EXISTS", "message": "البريد الإلكتروني مستخدم بالفعل."}
        }), 400

    user = User(email=email, name=name, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"success": True, "user": _format_user(user)}), 201

@users_bp.route('/<int:user_id>', methods=['PUT'])
@agents_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المستخدم غير موجود"}}), 404

    data = request.get_json() or {}
    if 'name' in data:
        user.name = data['name']
    if 'role' in data:
        user.role = data['role']
    if 'status' in data:
        user.status = data['status']
    if 'password' in data and data['password']:
        user.set_password(data['password'])

    db.session.commit()
    return jsonify({"success": True, "user": _format_user(user)})

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@agents_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المستخدم غير موجود"}}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"success": True, "message": "تم حذف المستخدم بنجاح."})
