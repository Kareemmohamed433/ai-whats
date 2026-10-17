from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import Lead, Customer
from app.extensions import db

leads_bp = Blueprint('leads', __name__, url_prefix='/api/leads')


@leads_bp.route('', methods=['GET'])
@jwt_required()
def get_leads():
    status = request.args.get('status')
    service = request.args.get('service')
    search = request.args.get('search', '').strip()

    query = Lead.query

    if status:
        query = query.filter_by(status=status)
    if service:
        query = query.filter(Lead.requested_service.ilike(f"%{service}%"))
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Lead.customer_name.ilike(pattern),
                Lead.contact_info.ilike(pattern),
                Lead.business_name.ilike(pattern),
                Lead.project_description.ilike(pattern)
            )
        )

    leads = query.order_by(Lead.created_at.desc()).all()
    return jsonify({
        "success": True,
        "leads": [l.to_dict() for l in leads]
    })


@leads_bp.route('/<int:lead_id>', methods=['GET'])
@jwt_required()
def get_lead_detail(lead_id):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "طلب المشروع غير موجود"}}), 404
    return jsonify({"success": True, "lead": lead.to_dict()})


@leads_bp.route('', methods=['POST'])
def create_lead():
    data = request.get_json() or {}
    contact_info = data.get('contact_info', '').strip()
    if not contact_info:
        return jsonify({"success": False, "error": {"code": "INVALID_FIELDS", "message": "معلومات الاتصال مطلوبة. Contact information is required."}}), 400

    lead = Lead(
        customer_id=data.get('customer_id'),
        customer_name=data.get('customer_name', '').strip() or 'عميل مهتم',
        contact_info=contact_info,
        business_name=data.get('business_name'),
        industry=data.get('industry'),
        requested_service=data.get('requested_service', 'تطوير مواقع وبرمجيات'),
        package_interest=data.get('package_interest'),
        project_description=data.get('project_description'),
        budget=data.get('budget'),
        expected_timeline=data.get('expected_timeline'),
        lead_source=data.get('lead_source', 'direct_chat'),
        status=data.get('status', 'New'),
        notes=data.get('notes')
    )
    db.session.add(lead)
    db.session.commit()
    return jsonify({"success": True, "lead": lead.to_dict()}), 201


@leads_bp.route('/<int:lead_id>', methods=['PUT', 'PATCH'])
@leads_bp.route('/<int:lead_id>/status', methods=['PUT', 'PATCH'])
@jwt_required()
def update_lead(lead_id):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "طلب المشروع غير موجود"}}), 404

    data = request.get_json() or {}
    new_status = data.get('status')
    valid_statuses = ['New', 'Qualified', 'Awaiting Human Review', 'Contacted', 'Closed']
    if new_status:
        if new_status not in valid_statuses:
            return jsonify({"success": False, "error": {"code": "INVALID_STATUS", "message": f"الحالة غير صحيحة. الحالات المقبولة: {valid_statuses}"}}), 400
        lead.status = new_status

    if 'assigned_employee_id' in data:
        lead.assigned_employee_id = data['assigned_employee_id']
    if 'notes' in data:
        lead.notes = data['notes']
    if 'requested_service' in data:
        lead.requested_service = data['requested_service']
    if 'budget' in data:
        lead.budget = data['budget']
    if 'business_name' in data:
        lead.business_name = data['business_name']

    db.session.commit()
    return jsonify({"success": True, "lead": lead.to_dict()})



@leads_bp.route('/<int:lead_id>', methods=['DELETE'])
@jwt_required()
def delete_lead(lead_id):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "طلب المشروع غير موجود"}}), 404

    db.session.delete(lead)
    db.session.commit()
    return jsonify({"success": True, "message": "تم حذف طلب المشروع بنجاح."})
