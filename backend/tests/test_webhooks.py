import pytest
from app import create_app
from app.extensions import db

@pytest.fixture
def app():
    app = create_app(test_config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_whatsapp_webhook_verification(client):
    res = client.get('/api/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=khams_sinaa_verify_token_2026&hub.challenge=123456')
    assert res.status_code == 200
    assert res.get_data(as_text=True) == "123456"

def test_telegram_webhook_paths(client):
    payload = {
        "update_id": 1001,
        "message": {
            "message_id": 1,
            "from": {"id": 998877, "first_name": "Test", "username": "testuser"},
            "chat": {"id": 998877},
            "text": "السلام عليكم"
        }
    }

    # Test path 1: /api/telegram/webhook
    res1 = client.post('/api/telegram/webhook', json=payload)
    assert res1.status_code == 200
    assert res1.get_json()["status"] == "OK"

    # Test path 2: /api/telegram/webhook/
    res2 = client.post('/api/telegram/webhook/', json=payload)
    assert res2.status_code == 200
    assert res2.get_json()["status"] == "OK"

    # Test path 3: /api/webhooks/telegram
    res3 = client.post('/api/webhooks/telegram', json=payload)
    assert res3.status_code == 200
    assert res3.get_json()["status"] == "OK"

    # Test path 4: /api/webhooks/telegram/
    res4 = client.post('/api/webhooks/telegram/', json=payload)
    assert res4.status_code == 200
    assert res4.get_json()["status"] == "OK"


def test_whatsapp_incoming_message_triggers_notification(client):
    from unittest.mock import patch

    wa_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "123456",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"display_phone_number": "123", "phone_number_id": "456"},
                    "contacts": [{"profile": {"name": "أحمد محمود"}, "wa_id": "201012345678"}],
                    "messages": [{
                        "from": "201012345678",
                        "id": "wamid.HBgLMjAxMDEyMzQ1Njc4FQIAEhggNTUx",
                        "timestamp": "1710000000",
                        "text": {"body": "استفسار عن تطوير متجر إلكتروني"},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }

    with patch('app.services.notification_service.NotificationService.dispatch_new_message_notification') as mock_dispatch:
        res = client.post('/api/webhooks/whatsapp', json=wa_payload)
        assert res.status_code == 200
        assert res.get_json()["status"] == "EVENT_RECEIVED"
        assert mock_dispatch.called is True


def test_webhook_deduplication(client):
    from app.models.message import Message

    wa_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "123456",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"display_phone_number": "123", "phone_number_id": "456"},
                    "contacts": [{"profile": {"name": "أحمد محمود"}, "wa_id": "201099999999"}],
                    "messages": [{
                        "from": "201099999999",
                        "id": "wamid.unique_test_msg_id_12345",
                        "timestamp": "1710000000",
                        "text": {"body": "رسالة اختبارية فريدة"},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }

    # First post creates message
    res1 = client.post('/api/webhooks/whatsapp', json=wa_payload)
    assert res1.status_code == 200

    # Second post with identical platform_message_id is skipped by deduplication
    res2 = client.post('/api/webhooks/whatsapp', json=wa_payload)
    assert res2.status_code == 200

    # Count in DB should be exactly 1
    msgs = Message.query.filter_by(platform_message_id="wamid.unique_test_msg_id_12345").all()
    assert len(msgs) == 1
