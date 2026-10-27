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

    @staticmethod
    def send_media(recipient, media_type, media_url, caption=None, filename=None):
        """
        Send media (image, video, document, audio) to recipient via WhatsApp Cloud API.
        """
        token = Config.WHATSAPP_ACCESS_TOKEN
        phone_id = Config.WHATSAPP_PHONE_NUMBER_ID

        valid_types = {'image', 'video', 'document', 'audio'}
        if media_type not in valid_types:
            media_type = 'document'

        if not token or not phone_id:
            print(f"[WhatsApp Simulation/Sandbox Media] Sent {media_type} to {recipient}: {media_url} (caption: {caption})")
            return {"success": True, "simulated": True, "media_type": media_type, "media_url": media_url}

        url = f"{GRAPH_URL}/{phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        media_payload = {"link": media_url}
        if caption and media_type in ('image', 'video', 'document'):
            media_payload["caption"] = caption
        if filename and media_type == 'document':
            media_payload["filename"] = filename

        body = {
            "messaging_product": "whatsapp",
            "type": media_type,
            media_type: media_payload
        }

        recipient = str(recipient).strip()
        if _is_phone(recipient):
            body["to"] = recipient.lstrip('+')
        else:
            body["recipient"] = recipient

        try:
            res = requests.post(url, json=body, headers=headers, timeout=15)
            data = res.json()
            print(f"[WhatsApp Media API] status={res.status_code}, response={data}")
            if res.ok:
                return {"success": True, "data": data}
            return {"success": False, "status_code": res.status_code, "error": data}
        except Exception as e:
            print(f"[WhatsApp Media Exception]: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def retrieve_and_download_media(media_id):
        """
        Retrieve media details from WhatsApp Cloud API and download the raw bytes.
        Returns dict with success, data_bytes, mime_type, file_size.
        """
        token = Config.WHATSAPP_ACCESS_TOKEN
        if not token or not media_id:
            return {"success": False, "error": "WhatsApp access token or media_id missing"}

        try:
            # Step 1: Query media URL
            info_url = f"{GRAPH_URL}/{media_id}"
            headers = {"Authorization": f"Bearer {token}"}
            res_info = requests.get(info_url, headers=headers, timeout=10)
            if not res_info.ok:
                return {
                    "success": False,
                    "status_code": res_info.status_code,
                    "error": f"Failed to retrieve media info: {res_info.text}"
                }

            media_info = res_info.json()
            download_url = media_info.get("url")
            mime_type = media_info.get("mime_type", "application/octet-stream")
            file_size = media_info.get("file_size")

            if not download_url:
                return {"success": False, "error": "No download URL returned by WhatsApp API"}

            # Step 2: Download raw binary bytes
            # Meta requires Authorization header when downloading from lookaside.fbsbx.com
            res_media = requests.get(
                download_url,
                headers={"Authorization": f"Bearer {token}", "User-Agent": "curl/7.64.1"},
                timeout=30
            )
            if not res_media.ok:
                return {
                    "success": False,
                    "status_code": res_media.status_code,
                    "error": f"Failed to download media content: {res_media.status_code}"
                }

            return {
                "success": True,
                "data_bytes": res_media.content,
                "mime_type": mime_type,
                "file_size": file_size or len(res_media.content)
            }
        except Exception as e:
            print(f"[WhatsApp Retrieve Media Exception]: {e}")
            return {"success": False, "error": str(e)}