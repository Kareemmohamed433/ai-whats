import requests
from app.config import Config

GRAPH_URL = "https://graph.facebook.com/v21.0"


class MessengerService:

    @staticmethod
    def send_message(recipient_id, text):
        token = getattr(Config, "MESSENGER_PAGE_ACCESS_TOKEN", None)
        if not token:
            print("[Messenger] ERROR: MESSENGER_PAGE_ACCESS_TOKEN is missing")
            return {"success": False, "error": "MESSENGER_PAGE_ACCESS_TOKEN is missing"}

        body = {
            "recipient": {"id": str(recipient_id)},
            "messaging_type": "RESPONSE",
            "message": {"text": text[:2000]},
        }

        try:
            res = requests.post(
                f"{GRAPH_URL}/me/messages",
                params={"access_token": token},
                json=body,
                timeout=10,
            )
            data = res.json()
            print(f"[Messenger API] status={res.status_code}, response={data}")
            if res.ok:
                return {"success": True, "data": data}
            return {"success": False, "status_code": res.status_code, "error": data}
        except requests.RequestException as e:
            print(f"[Messenger API Exception]: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_user_profile(psid):
        """Fetch the real name of the person who messaged the Page (PSID)."""
        token = getattr(Config, "MESSENGER_PAGE_ACCESS_TOKEN", None)
        if not token or not psid:
            return None

        try:
            res = requests.get(
                f"{GRAPH_URL}/{psid}",
                params={"fields": "first_name,last_name", "access_token": token},
                timeout=8,
            )
            if res.ok:
                d = res.json()
                name = f"{d.get('first_name', '')} {d.get('last_name', '')}".strip()
                return {"name": name or None, "username": None}
            print(f"[Messenger Profile] status={res.status_code}, response={res.text}")
        except requests.RequestException as e:
            print(f"[Messenger Profile Exception]: {e}")

        # Fallback: Conversations API (participants include the user's name)
        return MessengerService._get_name_from_conversations(psid, token)

    @staticmethod
    def _get_name_from_conversations(psid, token):
        try:
            res = requests.get(
                f"{GRAPH_URL}/me/conversations",
                params={
                    "user_id": psid,
                    "fields": "participants",
                    "access_token": token,
                },
                timeout=8,
            )
            if not res.ok:
                print(f"[Messenger Conversations Fallback] status={res.status_code}, response={res.text}")
                return None
            for conv in res.json().get("data", []):
                for p in conv.get("participants", {}).get("data", []):
                    if str(p.get("id")) == str(psid) and p.get("name"):
                        return {"name": p["name"], "username": None}
        except requests.RequestException as e:
            print(f"[Messenger Conversations Fallback Exception]: {e}")
        return None