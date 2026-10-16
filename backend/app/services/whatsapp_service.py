import os
import requests
from app.config import Config

class WhatsAppService:
    @staticmethod
    def send_message(phone_number, text):
        token = Config.WHATSAPP_ACCESS_TOKEN
        phone_id = Config.WHATSAPP_PHONE_NUMBER_ID

        if not token or not phone_id:
            # Platform integration configured or test mode
            print(f"[WhatsApp Simulation/Sandbox] Sent to {phone_number}: {text}")
            return {"success": True, "simulated": True}

        url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        body = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": text}
        }
        try:
            res = requests.post(url, json=body, headers=headers, timeout=10)
            return res.json()
        except Exception as e:
            return {"error": str(e)}
