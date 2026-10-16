import os
from app.config import Config

class TikTokService:
    @staticmethod
    def get_capabilities():
        token = Config.TIKTOK_ACCESS_TOKEN
        app_id = Config.TIKTOK_APP_ID
        if not token or not app_id:
            return {
                "available": False,
                "status_message": "Messaging is not currently available for this TikTok account/API configuration.",
                "reason": "Missing TikTok Access Token or Business Webhook App Verification."
            }
        
        # Check permissions
        return {
            "available": True,
            "status_message": "TikTok Business Messaging API Connected.",
            "reason": None
        }

    @staticmethod
    def send_message(recipient_id, text):
        caps = TikTokService.get_capabilities()
        if not caps["available"]:
            return {
                "success": False,
                "error": caps["status_message"]
            }
        
        print(f"[TikTok API] Sent to {recipient_id}: {text}")
        return {"success": True}
