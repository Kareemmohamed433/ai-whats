import json
from datetime import datetime, timezone
from app.extensions import db


class ServicePackage(db.Model):
    __tablename__ = 'service_packages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    name_ar = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    target_audience = db.Column(db.Text, nullable=True)
    indicative_price_min = db.Column(db.Float, nullable=True)
    indicative_price_max = db.Column(db.Float, nullable=True)
    indicative_price_text = db.Column(db.String(100), nullable=True)
    currency = db.Column(db.String(10), default='EGP')
    is_approved = db.Column(db.Boolean, default=False)  # Mark unapproved until verified
    is_popular = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    support_period = db.Column(db.String(100), nullable=True)
    features_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def features(self):
        if self.features_json:
            try:
                return json.loads(self.features_json)
            except Exception:
                return []
        return []

    @features.setter
    def features(self, val):
        if val is None:
            self.features_json = None
        else:
            self.features_json = json.dumps(val, ensure_ascii=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "slug": self.slug,
            "description": self.description,
            "target_audience": self.target_audience,
            "indicative_price_min": self.indicative_price_min,
            "indicative_price_max": self.indicative_price_max,
            "indicative_price_text": self.indicative_price_text,
            "currency": self.currency,
            "is_approved": self.is_approved,
            "is_popular": self.is_popular,
            "is_active": self.is_active,
            "support_period": self.support_period,
            "features": self.features,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
