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

    conv = db.session.get(Conversation, conv_id)
    if not conv:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المحادثة غير موجودة"}}), 404

    last_msg = conv.messages.order_by(db.desc('created_at')).first()
    text = (last_msg.content if last_msg else "").lower()

    suggested_shortcuts = []
    if any(w in text for w in ['بورتفوليو', 'شغلكم', 'اعمالكم', 'نماذج', 'مواقع', 'سابقة اعمال', 'portfolio', 'work']):
        suggested_shortcuts = ['/portfolio', '/services', '/packages']
    elif any(w in text for w in ['سعر', 'اسعار', 'بكم', 'بكام', 'تكلفة', 'باقات', 'باقة', 'starter', 'business', 'enterprise', 'price', 'cost']):
        suggested_shortcuts = ['/pricing', '/packages', '/requirements']
    elif any(w in text for w in ['شات بوت', 'ذكاء اصطناعي', 'بوت', 'ai', 'chatbot']):
        suggested_shortcuts = ['/ai_chatbot', '/requirements', '/portfolio']
    elif any(w in text for w in ['اتمته', 'أتمتة', 'ربط', 'نظام', 'automation', 'n8n', 'crm']):
        suggested_shortcuts = ['/automation', '/requirements']
    elif any(w in text for w in ['موظف', 'دعم', 'خدمة العملاء', 'حد يكلمني', 'مكالمة', 'human', 'agent']):
        suggested_shortcuts = ['/human', '/lead']
    elif any(w in text for w in ['مشروع', 'عايز اعمل', 'محتاج', 'تفاصيل', 'lead', 'start']):
        suggested_shortcuts = ['/requirements', '/lead', '/portfolio']
    else:
        suggested_shortcuts = ['/hello', '/services', '/portfolio', '/closing']

    matched_replies = QuickReply.query.filter(
        QuickReply.shortcut.in_(suggested_shortcuts),
        QuickReply.is_enabled == True
    ).all()

    # Fill up with other enabled quick replies if fewer than 3 matched
    if len(matched_replies) < 3:
        fillers = QuickReply.query.filter(
            QuickReply.is_enabled == True,
            ~QuickReply.id.in_([r.id for r in matched_replies])
        ).limit(4 - len(matched_replies)).all()
        matched_replies.extend(fillers)

    return jsonify({
        "success": True,
        "suggested": [r.to_dict() for r in matched_replies]
    })


@quick_replies_bp.route('', methods=['POST'])
@jwt_required()
def create_quick_reply():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    shortcut = data.get('shortcut', '').strip()
    response_text = data.get('response_text', '').strip()

    if not title or not shortcut or not response_text:
        return jsonify({"success": False, "error": {"code": "INVALID_FIELDS", "message": "العنوان، الاختصار، ونص الرد مطلوبة."}}), 400

    if not shortcut.startswith('/'):
        shortcut = f"/{shortcut}"

    existing = QuickReply.query.filter_by(shortcut=shortcut).first()
    if existing:
        return jsonify({"success": False, "error": {"code": "SHORTCUT_EXISTS", "message": "الاختصار مستخدم مسبقاً."}}), 400

    reply = QuickReply(
        title=title,
        shortcut=shortcut,
        category=data.get('category', 'general'),
        response_text=response_text,
        is_enabled=data.get('is_enabled', True)
    )
    db.session.add(reply)
    db.session.commit()

    return jsonify({"success": True, "quick_reply": reply.to_dict()}), 201


@quick_replies_bp.route('/<int:reply_id>', methods=['PUT'])
@jwt_required()
def update_quick_reply(reply_id):
    reply = db.session.get(QuickReply, reply_id)
    if not reply:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "الرد السريع غير موجود"}}), 404

    data = request.get_json() or {}
    if 'title' in data:
        reply.title = data['title']
    if 'shortcut' in data:
        shortcut = data['shortcut'].strip()
        if not shortcut.startswith('/'):
            shortcut = f"/{shortcut}"
        reply.shortcut = shortcut
    if 'category' in data:
        reply.category = data['category']
    if 'response_text' in data:
        reply.response_text = data['response_text']
    if 'is_enabled' in data:
        reply.is_enabled = bool(data['is_enabled'])

    db.session.commit()
    return jsonify({"success": True, "quick_reply": reply.to_dict()})


@quick_replies_bp.route('/<int:reply_id>', methods=['DELETE'])
@jwt_required()
def delete_quick_reply(reply_id):
    reply = db.session.get(QuickReply, reply_id)
    if not reply:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "الرد السريع غير موجود"}}), 404

    db.session.delete(reply)
    db.session.commit()
    return jsonify({"success": True, "message": "تم حذف الرد السريع بنجاح."})
