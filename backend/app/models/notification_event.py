from datetime import datetime
from app.extensions import db


class NotificationEvent(db.Model):
    __tablename__ = 'notification_events'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=True, index=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=True, index=True)
    channel = db.Column(db.String(50), nullable=False, default='webpush')  # webpush, socket, in_app
    status = db.Column(db.String(50), nullable=False, default='sent')     # sent, failed, suppressed
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "message_id": self.message_id,
            "channel": self.channel,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
