import os
from datetime import timedelta
from dotenv import load_dotenv

# Disable C extensions if Windows Application Control blocks compiled DLLs
os.environ["DISABLE_SQLALCHEMY_CEXT"] = "1"

load_dotenv()


class Config:

    # =========================
    # General
    # =========================
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "khams-sinaa-secret-key-super-secure-2026"
    )

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "khams-sinaa-jwt-secret-key-2026"
    )

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # =========================
    # Database
    # =========================
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        db_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "khams_sinaa.db"
        )
        DATABASE_URL = f"sqlite:///{db_path}"

    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://",
            "postgresql://",
            1
        )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =========================
    # AI
    # =========================
    AI_API_KEY = os.getenv("AI_API_KEY", "")

    AI_API_BASE_URL = os.getenv(
        "AI_API_BASE_URL",
        "https://api.openai.com/v1"
    )

    AI_MODEL = os.getenv(
        "AI_MODEL",
        "gpt-4o-mini"
    )

    AI_TEMPERATURE = float(
        os.getenv("AI_TEMPERATURE", "0.3")
    )

    AI_MAX_TOKENS = int(
        os.getenv("AI_MAX_TOKENS", "500")
    )

    # =========================
    # WhatsApp
    # =========================
    WHATSAPP_ACCESS_TOKEN = os.getenv(
        "WHATSAPP_ACCESS_TOKEN",
        ""
    )

    WHATSAPP_PHONE_NUMBER_ID = os.getenv(
        "WHATSAPP_PHONE_NUMBER_ID",
        ""
    )

    WHATSAPP_VERIFY_TOKEN = os.getenv(
        "WHATSAPP_VERIFY_TOKEN",
        "khams_sinaa_verify_token_2026"
    )

    WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv(
        "WHATSAPP_BUSINESS_ACCOUNT_ID",
        ""
    )

    # =========================
    # Instagram
    # =========================
    INSTAGRAM_ACCESS_TOKEN = os.getenv(
        "INSTAGRAM_ACCESS_TOKEN",
        ""
    )

    # Instagram Webhook verification token
    INSTAGRAM_VERIFY_TOKEN = os.getenv(
        "INSTAGRAM_VERIFY_TOKEN",
        "khams_sinaa_instagram_verify_2026"
    )

    # Instagram Business Account ID
    INSTAGRAM_ACCOUNT_ID = os.getenv(
        "INSTAGRAM_ACCOUNT_ID",
        "17841422010205813"
    )

    INSTAGRAM_PAGE_ID = os.getenv(
        "INSTAGRAM_PAGE_ID",
        ""
    )

    # =========================
    # TikTok
    # =========================
    TIKTOK_ACCESS_TOKEN = os.getenv(
        "TIKTOK_ACCESS_TOKEN",
        ""
    )

    TIKTOK_APP_ID = os.getenv(
        "TIKTOK_APP_ID",
        ""
    )

    # =========================
    # Telegram
    # =========================
    TELEGRAM_BOT_TOKEN = os.getenv(
        "TELEGRAM_BOT_TOKEN",
        ""
    )

    # =========================
    # Frontend
    # =========================
    FRONTEND_URL = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173"
    )