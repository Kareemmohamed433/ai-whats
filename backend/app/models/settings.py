import json
from datetime import datetime, timezone
from app.extensions import db


class CompanySettings(db.Model):
    __tablename__ = 'company_settings'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), default='NEXORA Software Solutions')
    tagline = db.Column(db.String(150), default='Ideas → Code → Impact')
    logo_url = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(30), default='+201556441133')
    whatsapp = db.Column(db.String(30), default='+201556441133')
    email = db.Column(db.String(100), default='contact@nexorasolutions.com')
    address = db.Column(db.Text, default='القاهرة، مصر')
    portfolio_url = db.Column(db.String(255), default='https://company-pi-two.vercel.app/')
    facebook_url = db.Column(db.String(255), default='https://www.facebook.com/profile.php?id=61595024167397')
    instagram_url = db.Column(db.String(255), default='https://www.instagram.com/nexorasoftwarre/')
    telegram_endpoint = db.Column(db.String(255), default='https://ai-whats-production.up.railway.app/')
    services_summary = db.Column(db.Text, default='تطوير المواقع والمنصات، حلول الذكاء الاصطناعي والشات بوت، أتمتة العمليات والربط البرمجي، وتطوير البرمجيات المخصصة.')
    working_hours_json = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        hours = {
            "working_days": "الأحد - الخميس",
            "opening_time": "09:00",
            "closing_time": "18:00",
            "timezone": "توقيت القاهرة"
        }
        if self.working_hours_json:
            try:
                hours = json.loads(self.working_hours_json)
            except Exception:
                pass

        return {
            "id": self.id,
            "company_name": self.company_name,
            "tagline": self.tagline,
            "logo_url": self.logo_url,
            "phone": self.phone,
            "whatsapp": self.whatsapp,
            "email": self.email,
            "address": self.address,
            "portfolio_url": self.portfolio_url,
            "facebook_url": self.facebook_url,
            "instagram_url": self.instagram_url,
            "telegram_endpoint": self.telegram_endpoint,
            "services_summary": self.services_summary,
            "working_hours": hours,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class StoreSettings(db.Model):
    """Retained for backward compatibility with existing legacy routes/tests."""
    __tablename__ = 'store_settings'

    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(150), default='NEXORA Software Solutions')
    logo_url = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(30), default='+201556441133')
    whatsapp = db.Column(db.String(30), default='+201556441133')
    email = db.Column(db.String(100), default='contact@nexorasolutions.com')
    address = db.Column(db.Text, default='القاهرة، مصر')
    shipping_policy = db.Column(db.Text, default='خدمات برمجية ورقمية سحابية تُسلّم وتُنشر عبر الإنترنت.')
    free_shipping_threshold = db.Column(db.Float, default=0.0)
    payment_methods = db.Column(db.Text, default='تحويل بنكي، إنستا باي (InstaPay)، فودافون كاش، دفع إلكتروني')
    return_policy = db.Column(db.Text, default='ضمان جودة البرمجيات ودعم فني وصيانة وفق اتفاقية مستوى الخدمة المعتمدة.')
    portfolio_url = db.Column(db.String(255), default='https://company-pi-two.vercel.app/')
    working_hours_json = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        hours = {
            "working_days": "الأحد - الخميس",
            "opening_time": "09:00",
            "closing_time": "18:00",
            "timezone": "توقيت القاهرة"
        }
        if self.working_hours_json:
            try:
                hours = json.loads(self.working_hours_json)
            except Exception:
                pass

        return {
            "id": self.id,
            "store_name": self.store_name,
            "company_name": self.store_name,
            "logo_url": self.logo_url,
            "phone": self.phone,
            "whatsapp": self.whatsapp,
            "email": self.email,
            "address": self.address,
            "shipping_policy": self.shipping_policy,
            "free_shipping_threshold": self.free_shipping_threshold,
            "payment_methods": self.payment_methods,
            "return_policy": self.return_policy,
            "portfolio_url": self.portfolio_url or 'https://company-pi-two.vercel.app/',
            "working_hours": hours,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class AISettings(db.Model):
    __tablename__ = 'ai_settings'

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), default='groq')
    api_key = db.Column(db.String(255), nullable=True)
    api_base_url = db.Column(db.String(255), default='https://api.groq.com/openai/v1')
    model = db.Column(db.String(100), default='llama-3.3-70b-versatile')
    temperature = db.Column(db.Float, default=0.3)
    max_tokens = db.Column(db.Integer, default=500)
    system_prompt = db.Column(db.Text, nullable=True)
    escalation_behavior = db.Column(db.String(50), default='pause_ai_and_assign')
    is_enabled = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

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
