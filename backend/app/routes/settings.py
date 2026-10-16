import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import StoreSettings, AISettings
from app.extensions import db

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')

@settings_bp.route('/store', methods=['GET'])
def get_store_settings():
    st = StoreSettings.query.first()
    if not st:
        st = StoreSettings()
        db.session.add(st)
        db.session.commit()
    return jsonify({"success": True, "settings": st.to_dict()})

@settings_bp.route('/store', methods=['PUT'])
@jwt_required()
def update_store_settings():
    st = StoreSettings.query.first()
    if not st:
        st = StoreSettings()
        db.session.add(st)

    data = request.get_json() or {}
    if 'store_name' in data:
        st.store_name = data['store_name']
    if 'logo_url' in data:
        st.logo_url = data['logo_url']
    if 'phone' in data:
        st.phone = data['phone']
    if 'whatsapp' in data:
        st.whatsapp = data['whatsapp']
    if 'email' in data:
        st.email = data['email']
    if 'address' in data:
        st.address = data['address']
    if 'shipping_policy' in data:
        st.shipping_policy = data['shipping_policy']
    if 'free_shipping_threshold' in data:
        st.free_shipping_threshold = float(data['free_shipping_threshold'])
    if 'payment_methods' in data:
        st.payment_methods = data['payment_methods']
    if 'return_policy' in data:
        st.return_policy = data['return_policy']
    if 'working_hours' in data:
        st.working_hours_json = json.dumps(data['working_hours'])

    db.session.commit()
    return jsonify({"success": True, "settings": st.to_dict()})

@settings_bp.route('/ai', methods=['GET'])
@jwt_required()
def get_ai_settings():
    ai = AISettings.query.first()
    if not ai:
        ai = AISettings()
        db.session.add(ai)
        db.session.commit()
    return jsonify({"success": True, "settings": ai.to_dict()})

@settings_bp.route('/ai', methods=['PUT'])
@jwt_required()
def update_ai_settings():
    ai = AISettings.query.first()
    if not ai:
        ai = AISettings()
        db.session.add(ai)

    data = request.get_json() or {}
    if 'provider' in data:
        ai.provider = data['provider']
    if 'api_key' in data and not data['api_key'].startswith('••••'):
        ai.api_key = data['api_key']
    if 'api_base_url' in data:
        ai.api_base_url = data['api_base_url']
    if 'model' in data:
        ai.model = data['model']
    if 'temperature' in data:
        ai.temperature = float(data['temperature'])
    if 'max_tokens' in data:
        ai.max_tokens = int(data['max_tokens'])
    if 'system_prompt' in data:
        ai.system_prompt = data['system_prompt']
    if 'escalation_behavior' in data:
        ai.escalation_behavior = data['escalation_behavior']
    if 'is_enabled' in data:
        ai.is_enabled = bool(data['is_enabled'])

    db.session.commit()
    return jsonify({"success": True, "settings": ai.to_dict()})
