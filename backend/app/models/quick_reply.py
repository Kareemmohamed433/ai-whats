from datetime import datetime
from app.extensions import db

class QuickReply(db.Model):
    __tablename__ = 'quick_replies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    shortcut = db.Column(db.String(50), nullable=False, unique=True, index=True) # e.g. /payment, /order
    category = db.Column(db.String(50), default='general', nullable=False) # payment, order, shipping, welcome, customer_service, closing
    response_text = db.Column(db.Text, nullable=False)
    is_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "shortcut": self.shortcut,
            "category": self.category,
            "response_text": self.response_text,
            "is_enabled": self.is_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
