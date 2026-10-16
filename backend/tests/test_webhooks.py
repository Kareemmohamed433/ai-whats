import pytest
from app import create_app
from app.extensions import db

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
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
