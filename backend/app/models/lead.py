from datetime import datetime, timezone
from app.extensions import db


class Lead(db.Model):
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    customer_name = db.Column(db.String(100), nullable=True)
    contact_info = db.Column(db.String(150), nullable=False)
    business_name = db.Column(db.String(150), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    requested_service = db.Column(db.String(100), nullable=False, default='تطوير مواقع وبرمجيات')
    package_interest = db.Column(db.String(50), nullable=True)
    project_description = db.Column(db.Text, nullable=True)
    budget = db.Column(db.String(100), nullable=True)
    expected_timeline = db.Column(db.String(100), nullable=True)
    lead_source = db.Column(db.String(50), default='direct_chat')  # whatsapp, telegram, instagram, web, etc.
    assigned_employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(50), default='New', nullable=False)  # New, Qualified, Awaiting Human Review, Contacted, Closed
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    customer = db.relationship('Customer', backref='leads', lazy=True)
    assigned_employee = db.relationship('User', backref='assigned_leads', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name or (self.customer.name if self.customer else "عميل"),
            "contact_info": self.contact_info,
            "business_name": self.business_name,
            "industry": self.industry,
            "requested_service": self.requested_service,
            "package_interest": self.package_interest,
            "project_description": self.project_description,
            "budget": self.budget,
            "expected_timeline": self.expected_timeline,
            "lead_source": self.lead_source,
            "assigned_employee_id": self.assigned_employee_id,
            "assigned_employee_name": self.assigned_employee.name if self.assigned_employee else None,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
