import json
from datetime import datetime
from app.extensions import db

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30), nullable=True, index=True)
    email = db.Column(db.String(120), nullable=True, index=True)
    avatar = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String(255), nullable=True, default='') # comma-separated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    identities = db.relationship('CustomerIdentity', backref='customer', cascade='all, delete-orphan', lazy=True)
    conversations = db.relationship('Conversation', backref='customer', cascade='all, delete-orphan', lazy=True)
    orders = db.relationship('Order', backref='customer', lazy=True)
    notes_rel = db.relationship('CustomerNote', backref='customer', cascade='all, delete-orphan', lazy=True, order_by='CustomerNote.created_at.desc()')
    activities_rel = db.relationship('CustomerActivity', backref='customer', cascade='all, delete-orphan', lazy=True, order_by='CustomerActivity.created_at.desc()')

    def to_dict(self, include_details=True):
        total_spent = sum([o.total_amount for o in self.orders if o.payment_status == 'paid' or o.order_status in ['confirmed', 'processing', 'shipped', 'delivered']])
        last_ord = self.orders[-1] if self.orders else None

        res = {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "avatar": self.avatar or f"https://ui-avatars.com/api/?name={self.name.replace(' ', '+')}&background=059669&color=fff",
            "notes": self.notes,
            "tags": [t.strip() for t in self.tags.split(',')] if self.tags else [],
            "identities": [ident.to_dict() for ident in self.identities],
            "total_conversations": len(self.conversations),
            "total_orders": len(self.orders),
            "total_spent": total_spent,
            "last_order": last_ord.to_dict() if last_ord else None,
            "current_order_status": last_ord.order_status if last_ord else None,
            "last_interaction": self.conversations[0].last_message_at.isoformat() if self.conversations and self.conversations[0].last_message_at else (self.created_at.isoformat() if self.created_at else None),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

        if include_details:
            res["notes_list"] = [n.to_dict() for n in self.notes_rel]
            res["activities"] = [a.to_dict() for a in self.activities_rel[:20]]

        return res

class CustomerIdentity(db.Model):
    __tablename__ = 'customer_identities'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    platform = db.Column(db.String(30), nullable=False) # whatsapp, instagram, tiktok, telegram
    platform_user_id = db.Column(db.String(100), nullable=False, index=True)
    username = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "platform": self.platform,
            "platform_user_id": self.platform_user_id,
            "username": self.username
        }

class CustomerNote(db.Model):
    __tablename__ = 'customer_notes'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    note_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "author_id": self.author_id,
            "author_name": self.author.name if self.author else "موظف الدعم",
            "note_text": self.note_text,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class CustomerActivity(db.Model):
    __tablename__ = 'customer_activities'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False) # open_conversation, ask_product, create_order, send_payment, payment_review, request_human
    description = db.Column(db.Text, nullable=False)
    metadata_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        meta = {}
        if self.metadata_json:
            try:
                meta = json.loads(self.metadata_json)
            except Exception:
                meta = {}
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "activity_type": self.activity_type,
            "description": self.description,
            "metadata": meta,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
