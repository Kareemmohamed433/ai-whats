import json
from datetime import datetime
from app.extensions import db

class Integration(db.Model):
    __tablename__ = 'integrations'

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), unique=True, nullable=False) # whatsapp, instagram, tiktok, telegram, ai_provider
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(30), default='disconnected') # connected, disconnected, pending, error, unavailable
    config_json = db.Column(db.Text, nullable=True) # credentials / details stored securely
    last_sync_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        cfg = {}
        if self.config_json:
            try:
                cfg = json.loads(self.config_json)
                # Mask sensitive fields
                masked_cfg = {}
                for k, v in cfg.items():
                    if any(secret_key in k.lower() for secret_key in ['token', 'key', 'secret', 'password']):
                        masked_cfg[k] = "••••••••" + v[-4:] if v and len(v) > 4 else "••••••••"
                    else:
                        masked_cfg[k] = v
                cfg = masked_cfg
            except Exception:
                cfg = {}

        return {
            "id": self.id,
            "provider": self.provider,
            "name": self.name,
            "status": self.status,
            "config": cfg,
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
