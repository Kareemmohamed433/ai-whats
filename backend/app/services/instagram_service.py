import requests
from app.config import Config


class InstagramService:

    @staticmethod
    def send_message(recipient_id, text):
        token = Config.INSTAGRAM_ACCESS_TOKEN
        ig_account_id = Config.INSTAGRAM_ACCOUNT_ID

        if not token:
            print("[Instagram] ERROR: INSTAGRAM_ACCESS_TOKEN is missing")
            return {
                "success": False,
                "error": "INSTAGRAM_ACCESS_TOKEN is missing"
            }

        if not ig_account_id:
            print("[Instagram] ERROR: INSTAGRAM_ACCOUNT_ID is missing")
            return {
                "success": False,
                "error": "INSTAGRAM_ACCOUNT_ID is missing"
            }

        url = f"https://graph.instagram.com/v26.0/{ig_account_id}/messages"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        body = {
            "recipient": {
                "id": str(recipient_id)
            },
            "message": {
                "text": text
            }
        }

        try:
            res = requests.post(
                url,
                json=body,
                headers=headers,
                timeout=10
            )

            response_data = res.json()

            print(
                f"[Instagram API] status={res.status_code}, "
                f"response={response_data}"
            )

            if res.ok:
                return {
                    "success": True,
                    "data": response_data
                }

            return {
                "success": False,
                "status_code": res.status_code,
                "error": response_data
            }

        except requests.RequestException as e:
            print(f"[Instagram API Exception]: {e}")

            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def get_user_profile(igsid):
        """Fetch name/username of the person who messaged us (IGSID)."""
        token = Config.INSTAGRAM_ACCESS_TOKEN
        if not token or not igsid:
            return None

        try:
            res = requests.get(
                f"https://graph.instagram.com/v26.0/{igsid}",
                params={"fields": "name,username"},
                headers={"Authorization": f"Bearer {token}"},
                timeout=8
            )
            if res.ok:
                data = res.json()
                return {
                    "name": data.get("name") or data.get("username"),
                    "username": data.get("username")
                }
            print(f"[Instagram Profile] status={res.status_code}, response={res.text}")
        except requests.RequestException as e:
            print(f"[Instagram Profile Exception]: {e}")
        return None