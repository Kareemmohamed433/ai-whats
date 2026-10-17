import pytest
from app import create_app
from app.extensions import db
from app.models import User, CompanySettings, StoreSettings

@pytest.fixture
def app():
    app = create_app(test_config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        admin = User(email="admin@nexorasolutions.com", name="Admin", role="admin")
        admin.set_password("password123")
        db.session.add(admin)

        settings = CompanySettings(
            company_name="NEXORA Software Solutions",
            tagline="Ideas → Code → Impact",
            portfolio_url="https://company-pi-two.vercel.app/",
            email="contact@nexorasolutions.com",
            phone="+20 155 644 1133",
            whatsapp="+20 155 644 1133",
            facebook_url="https://www.facebook.com/profile.php?id=61595024167397",
            instagram_url="https://www.instagram.com/nexorasoftwarre/"
        )
        db.session.add(settings)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_token(client):
    res = client.post('/api/auth/login', json={
        "email": "admin@nexorasolutions.com",
        "password": "password123"
    })
    return res.get_json()["token"]

def test_get_company_settings(client):
    res = client.get('/api/settings/company')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    settings = data["settings"]
    assert settings["company_name"] == "NEXORA Software Solutions"
    assert settings["tagline"] == "Ideas → Code → Impact"
    assert settings["portfolio_url"] == "https://company-pi-two.vercel.app/"
    assert settings["phone"] == "+20 155 644 1133"
    assert "facebook.com" in settings["facebook_url"]
    assert "instagram.com" in settings["instagram_url"]

def test_update_company_settings(client, auth_token):
    res = client.put('/api/settings/company', json={
        "tagline": "Ideas → Code → Impact | Custom Software & AI",
        "working_hours": "Sun - Thu: 10:00 AM - 6:00 PM"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["settings"]["tagline"] == "Ideas → Code → Impact | Custom Software & AI"

def test_store_settings_backward_compatibility(client):
    res = client.get('/api/settings/store')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    # Store settings fallback includes portfolio_url
    assert "portfolio_url" in data["settings"]
