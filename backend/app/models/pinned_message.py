from datetime import datetime
from app.extensions import db

class PinnedMessage(db.Model):
    __tablename__ = 'pinned_messages'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    pinned_by_agent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    note = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    message = db.relationship('Message', lazy=True)
    pinned_by = db.relationship('User', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "message_id": self.message_id,
            "message": self.message.to_dict() if self.message else None,
            "pinned_by_agent_id": self.pinned_by_agent_id,
            "pinned_by_name": self.pinned_by.name if self.pinned_by else "النظام",
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
