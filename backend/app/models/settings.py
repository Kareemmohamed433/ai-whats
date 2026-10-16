import json
from datetime import datetime
from app.extensions import db

class StoreSettings(db.Model):
    __tablename__ = 'store_settings'

    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(100), default='خام سينا - Khams Sinaa')
    logo_url = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(30), default='+201000000000')
    whatsapp = db.Column(db.String(30), default='+201000000000')
    email = db.Column(db.String(100), default='info@khams-sinaa.eg')
    address = db.Column(db.Text, default='العريش - سيناء / القاهرة - مصر')
    shipping_policy = db.Column(db.Text, default='الشحن لجميع محافظات مصر خلال 2-4 أيام عمل')
    free_shipping_threshold = db.Column(db.Float, default=500.0) # Free shipping over 500 EGP
    payment_methods = db.Column(db.Text, default='الدفع عند الاستلام، إنستا باي (InstaPay)، فودافون كاش')
    return_policy = db.Column(db.Text, default='إمكانية الاستبدال والاسترجاع خلال 14 يوما بشرط أن تكون العبوة بحالتها الأصلية')
    working_hours_json = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        hours = {
            "working_days": "من السبت إلى الخميس",
            "opening_time": "09:00",
            "closing_time": "21:00"
        }
        if self.working_hours_json:
            try:
                hours = json.loads(self.working_hours_json)
            except Exception:
                pass

        return {
            "id": self.id,
            "store_name": self.store_name,
            "logo_url": self.logo_url,
            "phone": self.phone,
            "whatsapp": self.whatsapp,
            "email": self.email,
            "address": self.address,
            "shipping_policy": self.shipping_policy,
            "free_shipping_threshold": self.free_shipping_threshold,
            "payment_methods": self.payment_methods,
            "return_policy": self.return_policy,
            "working_hours": hours,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class AISettings(db.Model):
    __tablename__ = 'ai_settings'

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), default='openai')
    api_key = db.Column(db.String(255), nullable=True)
    api_base_url = db.Column(db.String(255), default='https://api.openai.com/v1')
    model = db.Column(db.String(100), default='gpt-4o-mini')
    temperature = db.Column(db.Float, default=0.3)
    max_tokens = db.Column(db.Integer, default=500)
    system_prompt = db.Column(db.Text, nullable=True)
    escalation_behavior = db.Column(db.String(50), default='pause_ai_and_assign')
    is_enabled = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, hide_key=True):
        key = self.api_key or ""
        if hide_key and key:
            key = "••••••••" + key[-4:] if len(key) > 4 else "••••••••"

        return {
            "id": self.id,
            "provider": self.provider,
            "api_key": key,
            "api_base_url": self.api_base_url,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "system_prompt": self.system_prompt,
            "escalation_behavior": self.escalation_behavior,
            "is_enabled": self.is_enabled,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
