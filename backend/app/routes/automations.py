import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import AutomationRule
from app.extensions import db

automations_bp = Blueprint('automations', __name__, url_prefix='/api/automations')

@automations_bp.route('', methods=['GET'])
@jwt_required()
def get_automations():
    rules = AutomationRule.query.order_by(AutomationRule.id.asc()).all()
    return jsonify({
        "success": True,
        "automations": [r.to_dict() for r in rules]
    })

@automations_bp.route('', methods=['POST'])
@jwt_required()
def create_automation():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    trigger_event = data.get('trigger_event', '').strip()
    actions = data.get('actions', [])

    if not name or not trigger_event or not actions:
        return jsonify({"success": False, "error": {"code": "INVALID_FIELDS", "message": "الاسم، حدث المشغل والإجراءات مطلوبة."}}), 400

    rule = AutomationRule(
        name=name,
        trigger_event=trigger_event,
        conditions_json=json.dumps(data.get('conditions', {})),
        actions_json=json.dumps(actions),
        is_active=bool(data.get('is_active', True))
    )
    db.session.add(rule)
    db.session.commit()

    return jsonify({"success": True, "automation": rule.to_dict()}), 201

@automations_bp.route('/<int:rule_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_automation(rule_id):
    rule = AutomationRule.query.get(rule_id)
    if not rule:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "القاعدة غير موجودة"}}), 404

    rule.is_active = not rule.is_active
    db.session.commit()
    return jsonify({"success": True, "automation": rule.to_dict()})

@automations_bp.route('/<int:rule_id>', methods=['DELETE'])
@jwt_required()
def delete_automation(rule_id):
    rule = AutomationRule.query.get(rule_id)
    if not rule:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "القاعدة غير موجودة"}}), 404

    db.session.delete(rule)
    db.session.commit()
    return jsonify({"success": True, "message": "تم حذف القاعدة بنجاح."})
