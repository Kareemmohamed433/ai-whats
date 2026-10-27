import os
from datetime import timedelta
from dotenv import load_dotenv

# Disable C extensions if Windows Application Control blocks compiled DLLs
os.environ["DISABLE_SQLALCHEMY_CEXT"] = "1"

load_dotenv()


class Config:

    # =========================
    # NEXORA Company Identity & Public References
    # =========================
    COMPANY_NAME = "NEXORA Software Solutions"
    COMPANY_TAGLINE = "Ideas → Code → Impact"
    COMPANY_PHONE = "+201556441133"
    COMPANY_EMAIL = "contact@nexorasolutions.com"
    COMPANY_ADDRESS = "القاهرة، مصر"
    NEXORA_PORTFOLIO_URL = os.getenv(
        "NEXORA_PORTFOLIO_URL",
        "https://company-pi-two.vercel.app/"
    )
    NEXORA_FACEBOOK_URL = "https://www.facebook.com/profile.php?id=61595024167397"
    NEXORA_INSTAGRAM_URL = "https://www.instagram.com/nexorasoftwarre/"
    TELEGRAM_SERVICE_URL = os.getenv(
        "TELEGRAM_SERVICE_URL",
        "https://ai-whats-production.up.railway.app/"
    )

    # =========================
    # General & Security
    # =========================
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "nexora-secret-key-super-secure-production-2026"
    )

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "nexora-jwt-secret-key-production-2026"
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
    # AI Provider Configuration
    # =========================
    AI_API_KEY = os.getenv("AI_API_KEY", "")

    AI_API_BASE_URL = os.getenv(
        "AI_API_BASE_URL",
        "https://api.groq.com/openai/v1"
    )

    AI_MODEL = os.getenv(
        "AI_MODEL",
        "llama-3.3-70b-versatile"
    )

    AI_TEMPERATURE = float(
        os.getenv("AI_TEMPERATURE", "0.3")
    )

    AI_MAX_TOKENS = int(
        os.getenv("AI_MAX_TOKENS", "500")
    )

    # =========================
    # WhatsApp Business Cloud API
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
        "nexora_verify_token_2026"
    )

    WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv(
        "WHATSAPP_BUSINESS_ACCOUNT_ID",
        ""
    )

    # =========================
    # Instagram Direct Graph API
    # =========================
    INSTAGRAM_ACCESS_TOKEN = os.getenv(
        "INSTAGRAM_ACCESS_TOKEN",
        ""
    )

    INSTAGRAM_VERIFY_TOKEN = os.getenv(
        "INSTAGRAM_VERIFY_TOKEN",
        "nexora_instagram_verify_2026"
    )

    INSTAGRAM_ACCOUNT_ID = os.getenv(
        "INSTAGRAM_ACCOUNT_ID",
        "17841422010205813"
    )

    INSTAGRAM_PAGE_ID = os.getenv(
        "INSTAGRAM_PAGE_ID",
        ""
    )

    # =========================
    # Facebook Messenger (Page) API
    # =========================
    MESSENGER_PAGE_ACCESS_TOKEN = os.getenv(
        "MESSENGER_PAGE_ACCESS_TOKEN",
        ""
    )

    MESSENGER_VERIFY_TOKEN = os.getenv(
        "MESSENGER_VERIFY_TOKEN",
        ""
    )

    MESSENGER_PAGE_ID = os.getenv(
        "MESSENGER_PAGE_ID",
        ""
    )

    # =========================
    # TikTok Business Messaging API
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
    # Telegram Bot API
    # =========================
    TELEGRAM_BOT_TOKEN = os.getenv(
        "TELEGRAM_BOT_TOKEN",
        ""
    )

    # =========================
    # Frontend Application URL
    # =========================
    FRONTEND_URL = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173"
    )

    # =========================
    # Web Push (VAPID) Settings
    # =========================
    VAPID_PUBLIC_KEY = os.getenv(
        "VAPID_PUBLIC_KEY",
        ""
    )
    # =========================
    # Storage & Upload Settings
    # =========================
    STORAGE_DIR = os.getenv(
        "STORAGE_DIR",
        os.getenv(
            "UPLOAD_FOLDER",
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                "storage",
                "uploads"
            )
        )
    )
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 25 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {
        'jpg', 'jpeg', 'png', 'webp', 'gif', 'svg',
        'mp4', 'webm', 'mov',
        'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv',
        'ai', 'psd', 'eps', 'zip'
    }