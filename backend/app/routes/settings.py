import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import CompanySettings, StoreSettings, AISettings
from app.extensions import db

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')


@settings_bp.route('/company', methods=['GET'])
def get_company_settings():
    cs = CompanySettings.query.first()
    if not cs:
        cs = CompanySettings()
        db.session.add(cs)
        db.session.commit()
    return jsonify({"success": True, "settings": cs.to_dict()})


@settings_bp.route('/company', methods=['PUT'])
@jwt_required()
def update_company_settings():
    cs = CompanySettings.query.first()
    if not cs:
        cs = CompanySettings()
        db.session.add(cs)

    data = request.get_json() or {}
    if 'company_name' in data:
        cs.company_name = data['company_name']
    if 'tagline' in data:
        cs.tagline = data['tagline']
    if 'logo_url' in data:
        cs.logo_url = data['logo_url']
    if 'phone' in data:
        cs.phone = data['phone']
    if 'whatsapp' in data:
        cs.whatsapp = data['whatsapp']
    if 'email' in data:
        cs.email = data['email']
    if 'address' in data:
        cs.address = data['address']
    if 'portfolio_url' in data:
        cs.portfolio_url = data['portfolio_url']
    if 'facebook_url' in data:
        cs.facebook_url = data['facebook_url']
    if 'instagram_url' in data:
        cs.instagram_url = data['instagram_url']
    if 'telegram_endpoint' in data:
        cs.telegram_endpoint = data['telegram_endpoint']
    if 'services_summary' in data:
        cs.services_summary = data['services_summary']
    if 'working_hours' in data:
        cs.working_hours_json = json.dumps(data['working_hours'], ensure_ascii=False)

    db.session.commit()
    return jsonify({"success": True, "settings": cs.to_dict()})


@settings_bp.route('/store', methods=['GET'])
def get_store_settings():
    # Sync or return company settings
    cs = CompanySettings.query.first()
    st = StoreSettings.query.first()
    if not st:
        st = StoreSettings()
        db.session.add(st)
        db.session.commit()
    res = st.to_dict()
    if cs:
        res["portfolio_url"] = cs.portfolio_url
        res["company_name"] = cs.company_name
        res["tagline"] = cs.tagline
        res["facebook_url"] = cs.facebook_url
        res["instagram_url"] = cs.instagram_url
        res["telegram_endpoint"] = cs.telegram_endpoint
    return jsonify({"success": True, "settings": res})


@settings_bp.route('/store', methods=['PUT'])
@jwt_required()
def update_store_settings():
    st = StoreSettings.query.first()
    if not st:
        st = StoreSettings()
        db.session.add(st)

    cs = CompanySettings.query.first()
    if not cs:
        cs = CompanySettings()
        db.session.add(cs)

    data = request.get_json() or {}
    if 'store_name' in data or 'company_name' in data:
        val = data.get('company_name') or data.get('store_name')
        st.store_name = val
        cs.company_name = val
    if 'tagline' in data:
        cs.tagline = data['tagline']
    if 'logo_url' in data:
        st.logo_url = data['logo_url']
        cs.logo_url = data['logo_url']
    if 'phone' in data:
        st.phone = data['phone']
        cs.phone = data['phone']
    if 'whatsapp' in data:
        st.whatsapp = data['whatsapp']
        cs.whatsapp = data['whatsapp']
    if 'email' in data:
        st.email = data['email']
        cs.email = data['email']
    if 'address' in data:
        st.address = data['address']
        cs.address = data['address']
    if 'portfolio_url' in data:
        st.portfolio_url = data['portfolio_url']
        cs.portfolio_url = data['portfolio_url']
    if 'shipping_policy' in data:
        st.shipping_policy = data['shipping_policy']
    if 'payment_methods' in data:
        st.payment_methods = data['payment_methods']
    if 'return_policy' in data:
        st.return_policy = data['return_policy']
    if 'working_hours' in data:
        hours_str = json.dumps(data['working_hours'], ensure_ascii=False)
        st.working_hours_json = hours_str
        cs.working_hours_json = hours_str

    db.session.commit()
    return jsonify({"success": True, "settings": cs.to_dict()})


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
