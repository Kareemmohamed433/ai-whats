from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import Order, OrderItem, Product, Customer
from app.extensions import db
from datetime import datetime

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    status = request.args.get('status')
    search = request.args.get('search', '').strip()

    query = Order.query.join(Customer)

    if status:
        query = query.filter(Order.order_status == status)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Order.order_number.ilike(pattern),
                Customer.name.ilike(pattern),
                Customer.phone.ilike(pattern),
                Order.city.ilike(pattern)
            )
        )

    orders = query.order_by(Order.created_at.desc()).all()
    return jsonify({
        "success": True,
        "orders": [o.to_dict() for o in orders]
    })

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_detail(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "الطلب غير موجود"}}), 404
    return jsonify({"success": True, "order": order.to_dict()})

@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    data = request.get_json() or {}
    customer_id = data.get('customer_id')
    items = data.get('items', [])
    shipping_address = data.get('shipping_address', '')
    city = data.get('city', 'القاهرة')
    payment_method = data.get('payment_method', 'cash_on_delivery')

    if not customer_id or not items:
        return jsonify({"success": False, "error": {"code": "INVALID_ORDER", "message": "العميل والمنتجات مطلوبة لإنشاء الطلب."}}), 400

    order_num = f"KS-{int(datetime.utcnow().timestamp())}"
    total_amount = 0.0

    order = Order(
        order_number=order_num,
        customer_id=customer_id,
        total_amount=0.0,
        payment_method=payment_method,
        payment_status='pending',
        order_status='pending',
        shipping_address=shipping_address,
        city=city
    )
    db.session.add(order)
    db.session.flush()

    for item in items:
        product_id = item.get('product_id')
        qty = int(item.get('quantity', 1))
        product = Product.query.get(product_id)
        if product:
            unit_p = product.price
            tot_p = unit_p * qty
            total_amount += tot_p

            order_item = OrderItem(
                order_id=order.id,
                product_id=product_id,
                quantity=qty,
                unit_price=unit_p,
                total_price=tot_p
            )
            db.session.add(order_item)
            # Deduct stock
            product.stock = max(0, product.stock - qty)

    order.total_amount = total_amount
    db.session.commit()

    return jsonify({"success": True, "order": order.to_dict()}), 201

@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "الطلب غير موجود"}}), 404

    data = request.get_json() or {}
    order_status = data.get('order_status')
    payment_status = data.get('payment_status')
    tracking_number = data.get('tracking_number')

    if order_status:
        order.order_status = order_status
    if payment_status:
        order.payment_status = payment_status
    if tracking_number:
        order.tracking_number = tracking_number

    db.session.commit()
    return jsonify({"success": True, "order": order.to_dict()})
