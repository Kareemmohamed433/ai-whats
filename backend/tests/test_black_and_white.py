import io
import os
import json
import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from app.extensions import db
from app.models import (
    User, Customer, Conversation, Message, MessageAttachment,
    ServiceCategory, ServicePackage, Lead
)
from app.services.storage_service import StorageService
from app.services import ai_tools, AIService, WhatsAppService


@pytest.fixture
def app(tmp_path):
    storage_dir = tmp_path / "test_uploads"
    storage_dir.mkdir()

    app = create_app(test_config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "STORAGE_DIR": str(storage_dir),
        "MAX_CONTENT_LENGTH": 5 * 1024 * 1024, # 5 MB
        "JWT_SECRET_KEY": "test-jwt-secret-key-32-bytes-long!!"
    })

    with app.app_context():
        db.create_all()

        admin = User(email="admin@blackandwhite.com", name="Admin B&W", role="admin")
        admin.set_password("password123")
        db.session.add(admin)

        # Seed categories
        cat1 = ServiceCategory(
            name="Graphic Design",
            name_ar="تصميم جرافيك",
            slug="graphic-design",
            icon="🎨",
            description="تصميم الهويات البصرية والشعارات",
            is_active=True
        )
        cat2 = ServiceCategory(
            name="Advertising & Marketing",
            name_ar="دعاية وإعلان وتسويق",
            slug="advertising-marketing",
            icon="📢",
            description="حملات إعلانية وإدارة السوشيال ميديا",
            is_active=True
        )
        cat3 = ServiceCategory(
            name="Interior Decoration",
            name_ar="ديكور وتشطيب داخلي",
            slug="interior-decoration",
            icon="🏠",
            description="تصميم وتنفيذ الديكورات المعمارية",
            is_active=True
        )
        db.session.add_all([cat1, cat2, cat3])
        db.session.commit()

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    res = client.post("/api/auth/login", json={
        "email": "admin@blackandwhite.com",
        "password": "password123"
    })
    token = res.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}



# ==========================================
# 1. CATEGORY & SERVICE CATALOG TESTS
# ==========================================
def test_categories_crud(client, auth_headers):
    # List categories
    res = client.get("/api/packages/categories")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["categories"]) == 3

    # Create new category
    res = client.post("/api/packages/categories", json={
        "name": "Printing Services",
        "name_ar": "خدمات الطباعة",
        "slug": "printing-services",
        "icon": "🖨️",
        "description": "طباعة البنرات والبروشورات"
    }, headers=auth_headers)
    assert res.status_code == 201
    cat_id = res.get_json()["category"]["id"]

    # Update category
    res = client.put(f"/api/packages/categories/{cat_id}", json={
        "name_ar": "خدمات الطباعة الرقمية"
    }, headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["category"]["name_ar"] == "خدمات الطباعة الرقمية"

    # Delete category
    res = client.delete(f"/api/packages/categories/{cat_id}", headers=auth_headers)
    assert res.status_code == 200


def test_services_flexible_pricing(client, auth_headers):
    # 1. Fixed price service
    res1 = client.post("/api/packages", json={
        "name": "Logo Design Standard",
        "name_ar": "تصميم لوجو احترافي",
        "slug": "logo-design-standard",
        "category_slug": "graphic-design",
        "pricing_type": "fixed",
        "fixed_price": 1500,
        "currency": "EGP",
        "delivery_estimate": "3 أيام عمل",
        "is_active": True
    }, headers=auth_headers)
    assert res1.status_code == 201

    # 2. Starting at price service
    res2 = client.post("/api/packages", json={
        "name": "Social Media Campaign",
        "name_ar": "إدارة حملة إعلانية",
        "slug": "social-media-campaign",
        "category_slug": "advertising-marketing",
        "pricing_type": "starting_at",
        "starting_price": 3000,
        "currency": "EGP",
        "is_active": True
    }, headers=auth_headers)
    assert res2.status_code == 201

    # 3. Quotation required service (e.g. Interior Design)
    res3 = client.post("/api/packages", json={
        "name": "Villa Interior Design",
        "name_ar": "تصميم ديكور فيلا كاملة",
        "slug": "villa-interior-design",
        "category_slug": "interior-decoration",
        "pricing_type": "quotation_only",
        "quotation_required": True,
        "is_active": True
    }, headers=auth_headers)
    assert res3.status_code == 201

    # Filter by category
    res_filter = client.get("/api/packages?category=graphic-design")
    assert res_filter.status_code == 200
    packages = res_filter.get_json()["packages"]
    assert any(p["slug"] == "logo-design-standard" for p in packages)
    assert not any(p["slug"] == "villa-interior-design" for p in packages)


# ==========================================
# 2. AI LIVE CATALOG & PRICING RULES TESTS
# ==========================================
def test_ai_catalog_tools_and_pricing_rules(app):
    with app.app_context():
        # Test categories tool
        categories = ai_tools.get_service_categories()
        assert len(categories) >= 3
        cat_slugs = [c["slug"] for c in categories]
        assert "graphic-design" in cat_slugs
        assert "advertising-marketing" in cat_slugs
        assert "interior-decoration" in cat_slugs

        # Test pricing formatter: fixed
        fixed_text = ai_tools.format_service_pricing_text({
            "pricing_type": "fixed",
            "fixed_price": 2000,
            "currency": "EGP"
        })
        assert "2,000" in fixed_text or "2000" in fixed_text
        assert "السعر المحدد" in fixed_text

        # Test pricing formatter: starting at
        start_text = ai_tools.format_service_pricing_text({
            "pricing_type": "starting_at",
            "starting_price": 5000,
            "currency": "EGP"
        })
        assert "5,000" in start_text or "5000" in start_text
        assert "تبدأ من" in start_text

        # Test pricing formatter: quotation only
        quote_text = ai_tools.format_service_pricing_text({
            "pricing_type": "quotation_only",
            "quotation_required": True
        })
        assert "عرض سعر مخصص" in quote_text
        assert "Quotation" in quote_text or "متطلبات" in quote_text


        # Test pricing formatter: missing price
        missing_text = ai_tools.format_service_pricing_text({
            "pricing_type": None,
            "fixed_price": None,
            "starting_price": None
        })
        assert "عرض سعر مخصص" in missing_text


def test_ai_lead_creation_and_deduplication(app):
    with app.app_context():
        # First lead creation
        res1 = ai_tools.create_lead(
            customer_name="كريم محمد",
            phone="01099887766",
            notes="طلب تصميم هوية بصرية كاملة",
            category="graphic-design"
        )
        assert res1["success"] is True
        lead1 = res1["lead"]
        assert lead1["customer_name"] == "كريم محمد"

        # Duplicate lead with same phone should update existing, not duplicate
        res2 = ai_tools.create_lead(
            customer_name="كريم محمد",
            phone="01099887766",
            notes="إضافة: يحتاج كروت شخصية أيضاً",
            category="graphic-design"
        )
        assert res2["success"] is True
        assert res2["deduplicated"] is True
        lead2 = res2["lead"]
        assert lead2["id"] == lead1["id"]
        assert "كروت شخصية" in lead2["project_description"]



# ==========================================
# 3. ATTACHMENT STORAGE & SECURITY TESTS
# ==========================================
def test_storage_validation_and_path_traversal(app):
    with app.app_context():
        # 1. Allowed extensions
        valid, _ = StorageService.validate_file("logo.png")
        assert valid is True
        valid, _ = StorageService.validate_file("presentation.pdf")
        assert valid is True
        valid, _ = StorageService.validate_file("design.ai")
        assert valid is True

        # 2. Dangerous extensions blocked
        valid, msg = StorageService.validate_file("malicious.exe")
        assert valid is False
        assert "غير مسموح" in msg

        valid, msg = StorageService.validate_file("backdoor.php")
        assert valid is False

        valid, msg = StorageService.validate_file("script.py")
        assert valid is False

        # 3. Oversized file blocked
        valid, msg = StorageService.validate_file("huge.mp4", file_size=100 * 1024 * 1024)
        assert valid is False
        assert "يتجاوز الحد الأقصى" in msg

        # 4. Path traversal prevention
        assert StorageService.get_file_path("../../etc/passwd") is None
        assert StorageService.get_file_path("../config.py") is None
        assert StorageService.get_file_path("C:\\Windows\\System32\\cmd.exe") is None


def test_attachment_upload_and_download(client, auth_headers):
    # Upload an image
    file_bytes = b"fake-png-binary-content-12345"
    data = {
        "file": (io.BytesIO(file_bytes), "mock_logo.png")
    }
    res = client.post("/api/attachments/upload", data=data, content_type="multipart/form-data", headers=auth_headers)
    assert res.status_code == 201
    att_info = res.get_json()["attachment"]
    storage_key = att_info["storage_key"]
    assert "mock_logo.png" in att_info["file_name"]

    # Preview by storage key
    res_preview = client.get(f"/api/attachments/preview/{storage_key}")
    assert res_preview.status_code == 200
    assert res_preview.data == file_bytes

    # Download by storage key
    res_dl = client.get(f"/api/attachments/download/{storage_key}")
    assert res_dl.status_code == 200
    assert res_dl.data == file_bytes


# ==========================================
# 4. SENDING MESSAGE WITH ATTACHMENTS
# ==========================================
def test_send_message_with_attachment(client, auth_headers, app):
    with app.app_context():
        cust = Customer(name="عميل تجريبي", phone="201012345678")
        db.session.add(cust)
        db.session.flush()
        conv = Conversation(customer_id=cust.id, platform="whatsapp", platform_conversation_id="201012345678")
        db.session.add(conv)
        db.session.commit()
        conv_id = conv.id

    # Post message with attachment
    with patch("app.services.whatsapp_service.WhatsAppService.send_media") as mock_send_media:
        mock_send_media.return_value = {"success": True}

        res = client.post("/api/messages", json={
            "conversation_id": conv_id,
            "content": "إليك مقترح التصميم المبدئي",
            "message_type": "image",
            "media_url": "/api/attachments/preview/sample_key.png",
            "attachments": [{
                "file_type": "image",
                "file_name": "concept_1.png",
                "file_size": 1024,
                "file_url": "/api/attachments/preview/sample_key.png",
                "storage_key": "sample_key.png",
                "mime_type": "image/png"
            }]
        }, headers=auth_headers)

        assert res.status_code == 201
        msg_data = res.get_json()["message"]
        assert msg_data["message_type"] == "image"
        assert len(msg_data["attachments"]) == 1
        assert msg_data["attachments"][0]["file_name"] == "concept_1.png"
        assert mock_send_media.called


# ==========================================
# 5. INBOUND WHATSAPP MEDIA WEBHOOK & DEDUPLICATION
# ==========================================
def test_whatsapp_inbound_media_webhook(client, app):
    dummy_image_bytes = b"real-downloaded-image-bytes"

    with patch("app.services.whatsapp_service.WhatsAppService.retrieve_and_download_media") as mock_retrieve:
        mock_retrieve.return_value = {
            "success": True,
            "data_bytes": dummy_image_bytes,
            "mime_type": "image/jpeg",
            "file_size": len(dummy_image_bytes)
        }

        webhook_payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "contacts": [{
                            "wa_id": "201099887766",
                            "profile": {"name": "أحمد الشريف"}
                        }],
                        "messages": [{
                            "id": "wamid.HBgLMjAxMDk5ODg3NzY2FQIAEhgg",
                            "from": "201099887766",
                            "type": "image",
                            "image": {
                                "id": "media_id_9999",
                                "caption": "هذا تصميم يعجبني وأريد مثله",
                                "mime_type": "image/jpeg"
                            }
                        }]
                    }
                }]
            }]
        }

        # 1. First event
        res1 = client.post("/api/webhooks/whatsapp", json=webhook_payload)
        assert res1.status_code == 200

        with app.app_context():
            msg = Message.query.filter_by(platform_message_id="wamid.HBgLMjAxMDk5ODg3NzY2FQIAEhgg").first()
            assert msg is not None
            assert msg.message_type == "image"
            assert msg.content == "هذا تصميم يعجبني وأريد مثله"
            assert len(msg.attachments) == 1
            att = msg.attachments[0]
            assert att.direction == "inbound"
            assert att.status == "completed"
            assert att.provider_media_id == "media_id_9999"

        # 2. Duplicate webhook event (retry)
        res2 = client.post("/api/webhooks/whatsapp", json=webhook_payload)
        assert res2.status_code == 200

        with app.app_context():
            count = Message.query.filter_by(platform_message_id="wamid.HBgLMjAxMDk5ODg3NzY2FQIAEhgg").count()
            assert count == 1, "Duplicate webhook event must not create duplicate messages"


def test_attachment_preview_headers_and_cors(app, client, auth_headers):
    """
    Ensure image preview endpoints return 200 OK with correct Content-Type,
    Access-Control-Allow-Origin: *, and Cache-Control headers without requiring JWT auth
    (supporting native <img> DOM elements).
    """
    dummy_img = io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00")
    dummy_img.name = "sample_photo.jpg"

    upload_res = client.post(
        "/api/attachments/upload",
        data={"file": (dummy_img, "sample_photo.jpg")},
        content_type="multipart/form-data",
        headers=auth_headers
    )
    assert upload_res.status_code == 201
    att_data = upload_res.get_json()["attachment"]
    storage_key = att_data["storage_key"]

    # 1. Preview by storage key (without auth header, like browser <img>)
    preview_res = client.get(f"/api/attachments/preview/{storage_key}")
    assert preview_res.status_code == 200
    assert "image/jpeg" in preview_res.headers.get("Content-Type", "")
    assert preview_res.headers.get("Access-Control-Allow-Origin") == "*"
    assert "public" in preview_res.headers.get("Cache-Control", "")

    # 2. Download by storage key (without auth header)
    download_res = client.get(f"/api/attachments/download/{storage_key}")
    assert download_res.status_code == 200
    assert download_res.headers.get("Access-Control-Allow-Origin") == "*"

