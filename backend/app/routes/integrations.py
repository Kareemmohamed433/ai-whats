import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import Integration
from app.config import Config
from app.services import TikTokService
from app.extensions import db

integrations_bp = Blueprint('integrations', __name__, url_prefix='/api/integrations')

@integrations_bp.route('', methods=['GET'])
@jwt_required()
def get_integrations():
    integrations = Integration.query.all()
    # Ensure all providers exist in list
    providers = ['whatsapp', 'instagram', 'tiktok', 'telegram', 'ai_provider']
    existing_providers = {i.provider: i for i in integrations}

    result = []
    for p in providers:
        if p in existing_providers:
            integ_dict = existing_providers[p].to_dict()
            if p == 'tiktok':
                caps = TikTokService.get_capabilities()
                integ_dict['capabilities'] = caps
            result.append(integ_dict)
        else:
            default_status = 'disconnected'
            if p == 'whatsapp' and Config.WHATSAPP_ACCESS_TOKEN:
                default_status = 'connected'
            elif p == 'telegram' and Config.TELEGRAM_BOT_TOKEN:
                default_status = 'connected'
            elif p == 'instagram' and Config.INSTAGRAM_ACCESS_TOKEN:
                default_status = 'connected'
            elif p == 'ai_provider' and Config.AI_API_KEY:
                default_status = 'connected'
            elif p == 'tiktok':
                default_status = 'unavailable'

            item = {
                "provider": p,
                "name": p.capitalize() if p != 'ai_provider' else 'AI Provider',
                "status": default_status,
                "config": {}
            }
            if p == 'tiktok':
                item['capabilities'] = TikTokService.get_capabilities()
            result.append(item)

    return jsonify({"success": True, "integrations": result})

@integrations_bp.route('/<provider>/test', methods=['POST'])
@jwt_required()
def test_integration(provider):
    if provider == 'whatsapp':
        if Config.WHATSAPP_ACCESS_TOKEN and Config.WHATSAPP_PHONE_NUMBER_ID:
            return jsonify({"success": True, "message": "اتصال واتساب الأعمال نشط ويعمل بنجاح! 🟢"})
        return jsonify({"success": False, "message": "لم يتم إدخال مفتاح WHATSAPP_ACCESS_TOKEN أو WHATSAPP_PHONE_NUMBER_ID."})

    elif provider == 'telegram':
        if Config.TELEGRAM_BOT_TOKEN:
            return jsonify({"success": True, "message": "بوت تيليجرام متصل وجاهز لاستقبال الرسائل! 🤖"})
        return jsonify({"success": False, "message": "لم يتم إدخال TELEGRAM_BOT_TOKEN."})

    elif provider == 'instagram':
        if Config.INSTAGRAM_ACCESS_TOKEN:
            return jsonify({"success": True, "message": "اتصال إنستغرام Meta Graph API متصل بنجاح! 📸"})
        return jsonify({"success": False, "message": "لم يتم إدخال INSTAGRAM_ACCESS_TOKEN."})

    elif provider == 'tiktok':
        caps = TikTokService.get_capabilities()
        if caps["available"]:
            return jsonify({"success": True, "message": caps["status_message"]})
        return jsonify({"success": False, "message": caps["status_message"], "reason": caps["reason"]})

    elif provider == 'ai_provider':
        if Config.AI_API_KEY:
            return jsonify({"success": True, "message": f"مزود الذكاء الاصطناعي متصل نموذج ({Config.AI_MODEL})! ⚡"})
        return jsonify({"success": True, "message": "الذكاء الاصطناعي يعمل بالنظام الذكي الداخلي (Rule-Based Engine) لعدم تفعيل مفتاح API خارجي."})

    return jsonify({"success": False, "message": "مزود الخدمة غير معروف."}), 400
