import os
import requests
from app.config import Config

GRAPH_URL = "https://graph.facebook.com/v24.0"


def _is_phone(value):
    """Phone numbers are digits only; a BSUID looks like 'EG.abc123...'."""
    return bool(value) and str(value).lstrip('+').isdigit()


class WhatsAppService:
    @staticmethod
    def send_message(recipient, text):
        token = Config.WHATSAPP_ACCESS_TOKEN
        phone_id = Config.WHATSAPP_PHONE_NUMBER_ID

        if not token or not phone_id:
            # Platform integration configured or test mode
            print(f"[WhatsApp Simulation/Sandbox] Sent to {recipient}: {text}")
            return {"success": True, "simulated": True}

        url = f"{GRAPH_URL}/{phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        body = {
            "messaging_product": "whatsapp",
            "type": "text",
            "text": {"body": text}
        }

        # Phone number -> "to", BSUID (username-only users) -> "recipient"
        recipient = str(recipient).strip()
        if _is_phone(recipient):
            body["to"] = recipient.lstrip('+')
        else:
            body["recipient"] = recipient

        try:
            res = requests.post(url, json=body, headers=headers, timeout=10)
            data = res.json()
            print(f"[WhatsApp API] status={res.status_code}, response={data}")
            if res.ok:
                return {"success": True, "data": data}
            return {"success": False, "status_code": res.status_code, "error": data}
        except Exception as e:
            print(f"[WhatsApp API Exception]: {e}")
            return {"success": False, "error": str(e)}