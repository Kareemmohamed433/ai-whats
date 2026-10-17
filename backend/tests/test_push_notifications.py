import json
from unittest.mock import patch, MagicMock
import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.push_subscription import PushSubscription
from app.models.notification_preference import NotificationPreference
from app.services.notification_service import NotificationService
import pywebpush


@pytest.fixture
def app():
    app = create_app(test_config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "VAPID_PUBLIC_KEY": "BKS2unBwvA_pXKtcQoVH7Ql7J6tQ7k6957TyeqZ0Q_k_LThHobxryq6nBec0MAZ868S_pwFCGcZbHbzXAJWC9Ig",
        "VAPID_PRIVATE_KEY": "xGN3v39NwEHJgQ8I6lSBZMN39NACyL1JrelYKri1x7k",
        "VAPID_CLAIM_EMAIL": "mailto:contact@nexorasolutions.com"
    })

    with app.app_context():
        db.create_all()
        user = User(email="admin@nexorasolutions.com", name="NEXORA Admin", role="admin")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_header(client):
    """Authenticate admin and return authorization headers."""
    login_res = client.post('/api/auth/login', json={
        "email": "admin@nexorasolutions.com",
        "password": "password123"
    })
    data = login_res.get_json()
    token = data.get("token") or data.get("access_token")
    return {"Authorization": f"Bearer {token}"}


def test_vapid_public_key(client):
    res = client.get('/api/notifications/vapid-public-key')
    assert res.status_code == 200
    data = res.get_json()
    assert "public_key" in data
    assert "configured" in data


def test_notification_status_unauthorized(client):
    res = client.get('/api/notifications/status')
    assert res.status_code == 401


def test_notification_status_authorized(client, auth_header):
    res = client.get('/api/notifications/status', headers=auth_header)
    assert res.status_code == 200
    data = res.get_json()
    assert "preferences" in data
    assert "devices_count" in data
    assert isinstance(data["devices"], list)


def test_subscribe_missing_payload(client, auth_header):
    res = client.post('/api/notifications/subscribe', json={}, headers=auth_header)
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_subscribe_and_unsubscribe_cycle(client, auth_header):
    # 1. Subscribe
    sub_payload = {
        "endpoint": "https://fcm.googleapis.com/fcm/send/test-device-token-123",
        "keys": {
            "p256dh": "BEl62iUYgUivxIkv69yViEuiBIa...",
            "auth": "5KzF0yI7y..."
        },
        "device_name": "iPhone 15 Pro (Safari PWA)"
    }
    res = client.post('/api/notifications/subscribe', json=sub_payload, headers=auth_header)
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert data["subscription"]["device_name"] == "iPhone 15 Pro (Safari PWA)"

    # 2. Check status reflects 1 device
    status_res = client.get('/api/notifications/status', headers=auth_header)
    assert status_res.status_code == 200
    assert status_res.get_json()["devices_count"] >= 1

    # 3. Unsubscribe
    unsub_res = client.post('/api/notifications/unsubscribe', json={
        "endpoint": sub_payload["endpoint"]
    }, headers=auth_header)
    assert unsub_res.status_code == 200
    assert unsub_res.get_json()["success"] is True


def test_preferences_update(client, auth_header):
    # Update preferences
    res = client.put('/api/notifications/preferences', json={
        "desktop_enabled": True,
        "mobile_push_enabled": False,
        "sound_enabled": False,
        "preview_enabled": True
    }, headers=auth_header)
    assert res.status_code == 200
    prefs = res.get_json()["preferences"]
    assert prefs["mobile_push_enabled"] is False
    assert prefs["sound_enabled"] is False


def test_send_test_push_with_mock(client, auth_header):
    # Register mock device first
    sub_payload = {
        "endpoint": "https://push.apple.com/send/mock-apple-device",
        "keys": {
            "p256dh": "mock-p256dh",
            "auth": "mock-auth"
        },
        "device_name": "iPhone Mock"
    }
    client.post('/api/notifications/subscribe', json=sub_payload, headers=auth_header)

    with patch('pywebpush.webpush', return_value=MagicMock(status_code=201)):
        res = client.post('/api/notifications/test', headers=auth_header)
        assert res.status_code == 200
        assert res.get_json()["success"] is True


def test_expired_subscription_deactivation(app, client, auth_header):
    # Test handling of 410 Gone response
    sub_payload = {
        "endpoint": "https://push.apple.com/send/expired-device-token",
        "keys": {
            "p256dh": "mock-p256dh",
            "auth": "mock-auth"
        },
        "device_name": "Expired iPhone"
    }
    res = client.post('/api/notifications/subscribe', json=sub_payload, headers=auth_header)
    sub_id = res.get_json()["subscription"]["id"]

    mock_resp = MagicMock()
    mock_resp.status_code = 410
    err = pywebpush.WebPushException("Subscription has expired", response=mock_resp)

    with patch('pywebpush.webpush', side_effect=err):
        with app.app_context():
            ok = NotificationService.send_push_to_subscription(
                sub_id,
                {"title": "Test"},
                "fake-priv-key",
                {"sub": "mailto:test@example.com"}
            )
            assert ok is False

            # Verify in DB that is_active is now False
            sub = PushSubscription.query.get(sub_id)
            assert sub.is_active is False
