import json
from datetime import datetime
from app.extensions import db


class NotificationPreference(db.Model):
    __tablename__ = 'notification_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False, index=True)
    desktop_enabled = db.Column(db.Boolean, default=True, nullable=False)
    mobile_push_enabled = db.Column(db.Boolean, default=True, nullable=False)
    sound_enabled = db.Column(db.Boolean, default=True, nullable=False)
    preview_enabled = db.Column(db.Boolean, default=True, nullable=False)
    notify_on_all = db.Column(db.Boolean, default=True, nullable=False)
    notify_on_assigned_only = db.Column(db.Boolean, default=False, nullable=False)
    muted_conversations_json = db.Column(db.Text, default='[]', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('notification_preference', uselist=False, cascade='all, delete-orphan'))

    def get_muted_conversations(self):
        try:
            return json.loads(self.muted_conversations_json or '[]')
        except Exception:
            return []

    def set_muted_conversations(self, conv_ids):
        self.muted_conversations_json = json.dumps(conv_ids or [])

    def is_conversation_muted(self, conv_id):
        return conv_id in self.get_muted_conversations()

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "desktop_enabled": self.desktop_enabled,
            "mobile_push_enabled": self.mobile_push_enabled,
            "sound_enabled": self.sound_enabled,
            "preview_enabled": self.preview_enabled,
            "notify_on_all": self.notify_on_all,
            "notify_on_assigned_only": self.notify_on_assigned_only,
            "muted_conversations": self.get_muted_conversations(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
