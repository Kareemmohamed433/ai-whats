from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import QuickReply, Conversation, Message
from app.extensions import db

quick_replies_bp = Blueprint('quick_replies', __name__, url_prefix='/api/quick-replies')

@quick_replies_bp.route('', methods=['GET'])
@jwt_required()
def get_quick_replies():
    category = request.args.get('category')
    search = request.args.get('search', '').strip()

    query = QuickReply.query.filter_by(is_enabled=True)
    if category:
        query = query.filter(QuickReply.category == category)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                QuickReply.title.ilike(pattern),
                QuickReply.shortcut.ilike(pattern),
                QuickReply.response_text.ilike(pattern)
            )
        )

    replies = query.order_by(QuickReply.title.asc()).all()
    return jsonify({
        "success": True,
        "quick_replies": [r.to_dict() for r in replies]
    })

@quick_replies_bp.route('/suggested', methods=['GET'])
@jwt_required()
def get_suggested_quick_replies():
    conv_id = request.args.get('conversation_id', type=int)
    if not conv_id:
        replies = QuickReply.query.filter_by(is_enabled=True).limit(4).all()
        return jsonify({"success": True, "suggested": [r.to_dict() for r in replies]})

    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المحادثة غير موجودة"}}), 404

    last_msg = conv.messages.order_by(db.desc('created_at')).first()
    text = (last_msg.content if last_msg else "").lower()

    # Rule-based suggestions based on customer's last message intent
    suggested_shortcuts = []
    if any(w in text for w in ['حول', 'حولت', 'فودافون', 'انستا', 'صورة', 'اثبات', 'إثبات', 'دفعت']):
        suggested_shortcuts = ['/payment', '/order', '/customer_service']
    elif any(w in text for w in ['طلب', 'اوردر', 'أوردر', 'شحنة', 'وين', 'فين']):
        suggested_shortcuts = ['/order', '/shipping', '/customer_service']
    elif any(w in text for w in ['شحن', 'توصيل', 'محافظات']):
        suggested_shortcuts = ['/shipping', '/payment']
    elif any(w in text for w in ['سعر', 'اسعار', 'بكم', 'بكام', 'زيت', 'منتج']):
        suggested_shortcuts = ['/products', '/order']
    else:
        suggested_shortcuts = ['/hello', '/customer_service', '/closing']

    suggested = QuickReply.query.filter(QuickReply.shortcut.in_(suggested_shortcuts), QuickReply.is_enabled == True).all()
    if not suggested:
        suggested = QuickReply.query.filter_by(is_enabled=True).limit(4).all()

    return jsonify({
        "success": True,
        "suggested": [r.to_dict() for r in suggested]
    })

@quick_replies_bp.route('', methods=['POST'])
@jwt_required()
def create_quick_reply():
    data = request.get_json() or {}
    title = data.get('title')
    shortcut = data.get('shortcut', '').strip()
    category = data.get('category', 'general')
    response_text = data.get('response_text')

    if not title or not shortcut or not response_text:
        return jsonify({"success": False, "error": {"code": "INVALID_DATA", "message": "العنوان، الاختصار والنص مطلوبة."}}), 400

    if not shortcut.startswith('/'):
        shortcut = '/' + shortcut

    existing = QuickReply.query.filter_by(shortcut=shortcut).first()
    if existing:
        return jsonify({"success": False, "error": {"code": "ALREADY_EXISTS", "message": "هذا الاختصار مستخدم بالفعل."}}), 400

    reply = QuickReply(
        title=title,
        shortcut=shortcut,
        category=category,
        response_text=response_text,
        is_enabled=data.get('is_enabled', True)
    )
    db.session.add(reply)
    db.session.commit()

    return jsonify({"success": True, "quick_reply": reply.to_dict()}), 201

@quick_replies_bp.route('/<int:reply_id>', methods=['PUT'])
@jwt_required()
def update_quick_reply(reply_id):
    reply = QuickReply.query.get(reply_id)
    if not reply:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "الرد السريع غير موجود"}}), 404

    data = request.get_json() or {}
    if 'title' in data:
        reply.title = data['title']
    if 'shortcut' in data:
        sc = data['shortcut'].strip()
        if not sc.startswith('/'):
            sc = '/' + sc
        reply.shortcut = sc
    if 'category' in data:
        reply.category = data['category']
    if 'response_text' in data:
        reply.response_text = data['response_text']
    if 'is_enabled' in data:
        reply.is_enabled = data['is_enabled']

    db.session.commit()
    return jsonify({"success": True, "quick_reply": reply.to_dict()})

@quick_replies_bp.route('/<int:reply_id>', methods=['DELETE'])
@jwt_required()
def delete_quick_reply(reply_id):
    reply = QuickReply.query.get(reply_id)
    if not reply:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "الرد السريع غير موجود"}}), 404

    db.session.delete(reply)
    db.session.commit()
    return jsonify({"success": True, "message": "تم حذف الرد السريع بنجاح"})
