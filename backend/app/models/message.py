import json
from datetime import datetime
from app.extensions import db

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    platform_message_id = db.Column(db.String(100), nullable=True)
    sender_type = db.Column(db.String(20), nullable=False) # customer, ai, agent, system
    sender_id = db.Column(db.String(100), nullable=True)
    sender_name = db.Column(db.String(100), nullable=True)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text') # text, image, video, document, audio
    media_url = db.Column(db.String(500), nullable=True)
    metadata_json = db.Column(db.Text, nullable=True) # JSON stored as string for cross-db compatibility
    status = db.Column(db.String(20), default='sent') # sent, delivered, read, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    attachments = db.relationship('MessageAttachment', backref='message', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        meta = {}
        if self.metadata_json:
            try:
                meta = json.loads(self.metadata_json)
            except Exception:
                meta = {}

        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "platform_message_id": self.platform_message_id,
            "sender_type": self.sender_type,
            "sender_id": self.sender_id,
            "sender_name": self.sender_name,
            "content": self.content,
            "message_type": self.message_type,
            "media_url": self.media_url,
            "metadata": meta,
            "status": self.status,
            "attachments": [att.to_dict() for att in self.attachments],
            "created_at": (self.created_at.isoformat() + 'Z') if self.created_at else None
        }

class MessageAttachment(db.Model):
    __tablename__ = 'message_attachments'

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=True)
    file_type = db.Column(db.String(50), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)
    file_name = db.Column(db.String(200), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    storage_key = db.Column(db.String(255), nullable=True)
    mime_type = db.Column(db.String(100), nullable=True)
    direction = db.Column(db.String(20), default='inbound')
    provider_media_id = db.Column(db.String(150), nullable=True)
    status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "message_id": self.message_id,
            "conversation_id": self.conversation_id,
            "file_type": self.file_type,
            "file_url": self.file_url,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "storage_key": self.storage_key,
            "mime_type": self.mime_type,
            "direction": self.direction,
            "provider_media_id": self.provider_media_id,
            "status": self.status,
            "created_at": (self.created_at.isoformat() + 'Z') if self.created_at else None
        }