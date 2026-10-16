from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import PaymentReview, Order, Customer, Message, CustomerActivity
from app.extensions import db
from app.services.socket_service import SocketService
from datetime import datetime

payment_reviews_bp = Blueprint('payment_reviews', __name__, url_prefix='/api/payment-reviews')

@payment_reviews_bp.route('', methods=['GET'])
@jwt_required()
def get_payment_reviews():
    status = request.args.get('status')
    search = request.args.get('search', '').strip()

    query = PaymentReview.query.join(Customer)

    if status:
        query = query.filter(PaymentReview.status == status)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Customer.name.ilike(pattern),
                Customer.phone.ilike(pattern),
                PaymentReview.reference_number.ilike(pattern)
            )
        )

    reviews = query.order_by(PaymentReview.created_at.desc()).all()
    return jsonify({
        "success": True,
        "payment_reviews": [r.to_dict() for r in reviews],
        "pending_count": PaymentReview.query.filter_by(status='pending').count()
    })

@payment_reviews_bp.route('/<int:review_id>', methods=['GET'])
@jwt_required()
def get_payment_review(review_id):
    review = PaymentReview.query.get(review_id)
    if not review:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "طلب مراجعة الدفع غير موجود"}}), 404
    return jsonify({"success": True, "payment_review": review.to_dict()})

@payment_reviews_bp.route('/<int:review_id>/approve', methods=['PUT'])
@jwt_required()
def approve_payment(review_id):
    agent_id = int(get_jwt_identity())
    review = PaymentReview.query.get(review_id)
    if not review:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "طلب مراجعة الدفع غير موجود"}}), 404

    review.status = 'approved'
    review.reviewed_by_agent_id = agent_id

    # Update order payment status if linked
    if review.order:
        review.order.payment_status = 'paid'
        if review.order.order_status == 'pending':
            review.order.order_status = 'confirmed'

    # Add customer activity
    act = CustomerActivity(
        customer_id=review.customer_id,
        activity_type='payment_approved',
        description=f"تم اعتماد إثبات الدفع للطلب #{review.order.order_number if review.order else ''} بقيمة {review.detected_amount or review.expected_amount or 0} ج.م"
    )
    db.session.add(act)
    db.session.commit()

    # Emit socket updates
    SocketService.broadcast_payment_review_updated(review)
    if review.order:
        SocketService.broadcast_order_updated(review.order)

    return jsonify({"success": True, "payment_review": review.to_dict()})

@payment_reviews_bp.route('/<int:review_id>/reject', methods=['PUT'])
@jwt_required()
def reject_payment(review_id):
    agent_id = int(get_jwt_identity())
    data = request.get_json() or {}
    reason = data.get('reason', 'إثبات الدفع غير واضح أو غير مطابقة للبيانات')

    review = PaymentReview.query.get(review_id)
    if not review:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "طلب مراجعة الدفع غير موجود"}}), 404

    review.status = 'rejected'
    review.rejection_reason = reason
    review.reviewed_by_agent_id = agent_id

    if review.order:
        review.order.payment_status = 'rejected'

    act = CustomerActivity(
        customer_id=review.customer_id,
        activity_type='payment_rejected',
        description=f"تم رفض إثبات الدفع: {reason}"
    )
    db.session.add(act)
    db.session.commit()

    SocketService.broadcast_payment_review_updated(review)
    if review.order:
        SocketService.broadcast_order_updated(review.order)

    return jsonify({"success": True, "payment_review": review.to_dict()})
