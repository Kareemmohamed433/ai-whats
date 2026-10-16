import json
from datetime import datetime
from app.extensions import db

class PaymentReview(db.Model):
    __tablename__ = 'payment_reviews'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=True)
    
    expected_amount = db.Column(db.Float, nullable=True)
    detected_amount = db.Column(db.Float, nullable=True)
    reference_number = db.Column(db.String(100), nullable=True)
    date_str = db.Column(db.String(50), nullable=True)
    screenshot_url = db.Column(db.String(500), nullable=True)
    ocr_data_json = db.Column(db.Text, nullable=True)
    
    status = db.Column(db.String(20), default='pending', nullable=False) # pending, approved, rejected
    rejection_reason = db.Column(db.Text, nullable=True)
    reviewed_by_agent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = db.relationship('Customer', backref='payment_reviews', lazy=True)
    order = db.relationship('Order', backref='payment_reviews', lazy=True)
    reviewed_by = db.relationship('User', foreign_keys=[reviewed_by_agent_id], lazy=True)

    def to_dict(self):
        ocr = {}
        if self.ocr_data_json:
            try:
                ocr = json.loads(self.ocr_data_json)
            except Exception:
                ocr = {}

        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_name": self.customer.name if self.customer else "عميل",
            "customer_phone": self.customer.phone if self.customer else "",
            "order_id": self.order_id,
            "order_number": self.order.order_number if self.order else None,
            "conversation_id": self.conversation_id,
            "expected_amount": self.expected_amount,
            "detected_amount": self.detected_amount,
            "reference_number": self.reference_number,
            "date_str": self.date_str,
            "screenshot_url": self.screenshot_url,
            "ocr_data": ocr,
            "status": self.status,
            "rejection_reason": self.rejection_reason,
            "reviewed_by_agent_id": self.reviewed_by_agent_id,
            "reviewed_by_name": self.reviewed_by.name if self.reviewed_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
