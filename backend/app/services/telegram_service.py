import os
import requests
from app.config import Config

class TelegramService:
    @staticmethod
    def send_message(chat_id, text):
        token = Config.TELEGRAM_BOT_TOKEN
        if not token:
            print(f"[Telegram Simulation] Sent to chat {chat_id}: {text}")
            return {"success": True, "simulated": True}

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        body = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        try:
            res = requests.post(url, json=body, timeout=10)
            return res.json()
        except Exception as e:
            return {"error": str(e)}
