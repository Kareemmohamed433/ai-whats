from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Customer, CustomerIdentity, CustomerNote, CustomerActivity, Order, Conversation
from app.extensions import db
from app.services import SocketService

customers_bp = Blueprint('customers', __name__, url_prefix='/api/customers')

@customers_bp.route('', methods=['GET'])
@jwt_required()
def get_customers():
    search = request.args.get('search', '').strip()
    query = Customer.query

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Customer.name.ilike(pattern),
                Customer.phone.ilike(pattern),
                Customer.email.ilike(pattern)
            )
        )

    customers = query.order_by(Customer.created_at.desc()).all()
    return jsonify({
        "success": True,
        "customers": [c.to_dict(include_details=False) for c in customers]
    })

@customers_bp.route('/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer_detail(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "العميل غير موجود"}}), 404
    return jsonify({"success": True, "customer": customer.to_dict(include_details=True)})

@customers_bp.route('/<int:customer_id>/notes', methods=['POST'])
@jwt_required()
def add_customer_note(customer_id):
    agent_id = int(get_jwt_identity())
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "العميل غير موجود"}}), 404

    data = request.get_json() or {}
    note_text = data.get('note_text', '').strip()
    if not note_text:
        return jsonify({"success": False, "error": {"code": "MISSING_NOTE", "message": "نص الملاحظة مطلوب."}}), 400

    note = CustomerNote(
        customer_id=customer.id,
        author_id=agent_id,
        note_text=note_text
    )
    db.session.add(note)

    act = CustomerActivity(
        customer_id=customer.id,
        activity_type='add_note',
        description=f"إضافة ملاحظة جديدة: {note_text[:40]}..."
    )
    db.session.add(act)
    db.session.commit()

    SocketService.broadcast_customer_updated(customer)

    return jsonify({"success": True, "note": note.to_dict(), "customer": customer.to_dict(include_details=True)}), 201

@customers_bp.route('/<int:customer_id>/orders', methods=['GET'])
@jwt_required()
def get_customer_orders_api(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "العميل غير موجود"}}), 404

    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).all()
    return jsonify({
        "success": True,
        "orders": [o.to_dict() for o in orders]
    })

@customers_bp.route('/<int:customer_id>/conversations', methods=['GET'])
@jwt_required()
def get_customer_conversations_api(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "العميل غير موجود"}}), 404

    conversations = Conversation.query.filter_by(customer_id=customer_id).order_by(Conversation.last_message_at.desc()).all()
    return jsonify({
        "success": True,
        "conversations": [c.to_dict() for c in conversations]
    })

@customers_bp.route('', methods=['POST'])
@jwt_required()
def create_customer():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({"success": False, "error": {"code": "MISSING_NAME", "message": "اسم العميل مطلوب."}}), 400

    customer = Customer(
        name=name,
        phone=data.get('phone'),
        email=data.get('email'),
        notes=data.get('notes'),
        tags=','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else data.get('tags', '')
    )
    db.session.add(customer)
    db.session.flush()

    platform = data.get('platform')
    platform_user_id = data.get('platform_user_id')
    if platform and platform_user_id:
        identity = CustomerIdentity(
            customer_id=customer.id,
            platform=platform,
            platform_user_id=platform_user_id,
            username=data.get('username')
        )
        db.session.add(identity)
    
    db.session.commit()
    return jsonify({"success": True, "customer": customer.to_dict()}), 201

@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "العميل غير موجود"}}), 404

    data = request.get_json() or {}
    if 'name' in data:
        customer.name = data['name']
    if 'phone' in data:
        customer.phone = data['phone']
    if 'email' in data:
        customer.email = data['email']
    if 'notes' in data:
        customer.notes = data['notes']
    if 'tags' in data:
        customer.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']

    db.session.commit()
    return jsonify({"success": True, "customer": customer.to_dict()})
