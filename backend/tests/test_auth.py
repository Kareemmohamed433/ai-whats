import pytest
from app import create_app
from app.extensions import db
from app.models import User

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        user = User(email="testadmin@khams-sinaa.eg", name="Test Admin", role="admin")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_login_success(client):
    res = client.post('/api/auth/login', json={
        "email": "testadmin@khams-sinaa.eg",
        "password": "password123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "token" in data

def test_login_failure(client):
    res = client.post('/api/auth/login', json={
        "email": "testadmin@khams-sinaa.eg",
        "password": "wrongpassword"
    })
    assert res.status_code == 401
    data = res.get_json()
    assert data["success"] is False
