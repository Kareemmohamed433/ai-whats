import json
from datetime import datetime, timezone
from app.extensions import db


class ServiceCategory(db.Model):
    __tablename__ = 'service_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    name_ar = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), default='palette')
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    services = db.relationship('ServicePackage', backref='category_rel', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_services=False):
        data = {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "slug": self.slug,
            "description": self.description,
            "icon": self.icon,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
            "services_count": len([s for s in self.services if s.is_active]) if self.services else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_services:
            data["services"] = [s.to_dict() for s in self.services if s.is_active]
        return data


class ServicePackage(db.Model):
    __tablename__ = 'service_packages'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('service_categories.id'), nullable=True)
    category_slug = db.Column(db.String(100), nullable=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    name_ar = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    target_audience = db.Column(db.Text, nullable=True)

    # Flexible pricing models: 'fixed', 'starting_at', 'range', 'quotation_required'
    pricing_type = db.Column(db.String(30), default='quotation_required')
    fixed_price = db.Column(db.Float, nullable=True)
    starting_price = db.Column(db.Float, nullable=True)
    indicative_price_min = db.Column(db.Float, nullable=True)
    indicative_price_max = db.Column(db.Float, nullable=True)
    indicative_price_text = db.Column(db.String(100), nullable=True)
    quotation_required = db.Column(db.Boolean, default=False)
    pricing_notes = db.Column(db.Text, nullable=True)
    delivery_estimate = db.Column(db.String(100), nullable=True)
    requirements_text = db.Column(db.Text, nullable=True)
    currency = db.Column(db.String(10), default='EGP')

    is_approved = db.Column(db.Boolean, default=False)
    is_popular = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    support_period = db.Column(db.String(100), nullable=True)
    features_json = db.Column(db.Text, nullable=True)
    example_images_json = db.Column(db.Text, nullable=True)

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

    @property
    def example_images(self):
        if self.example_images_json:
            try:
                return json.loads(self.example_images_json)
            except Exception:
                return []
        return []

    @example_images.setter
    def example_images(self, val):
        if val is None:
            self.example_images_json = None
        else:
            self.example_images_json = json.dumps(val, ensure_ascii=False)

    def to_dict(self):
        cat_name = self.category_rel.name_ar if self.category_rel else None
        return {
            "id": self.id,
            "category_id": self.category_id,
            "category_slug": self.category_slug or (self.category_rel.slug if self.category_rel else None),
            "category_name": cat_name,
            "name": self.name,
            "name_ar": self.name_ar,
            "slug": self.slug,
            "description": self.description,
            "target_audience": self.target_audience,
            "pricing_type": self.pricing_type or ('range' if (self.indicative_price_min is not None or self.indicative_price_max is not None) else ('fixed' if self.fixed_price is not None else ('starting_at' if self.starting_price is not None else 'quotation_required'))),
            "fixed_price": self.fixed_price,
            "starting_price": self.starting_price,
            "indicative_price_min": self.indicative_price_min,
            "indicative_price_max": self.indicative_price_max,
            "indicative_price_text": self.indicative_price_text,
            "quotation_required": bool(self.quotation_required or (self.pricing_type == 'quotation_required') or (self.fixed_price is None and self.starting_price is None and self.indicative_price_min is None and self.indicative_price_max is None)),
            "pricing_notes": self.pricing_notes,
            "delivery_estimate": self.delivery_estimate,
            "requirements_text": self.requirements_text,
            "currency": self.currency or 'EGP',
            "is_approved": self.is_approved,
            "is_popular": self.is_popular,
            "is_active": self.is_active,
            "support_period": self.support_period,
            "features": self.features,
            "example_images": self.example_images,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
