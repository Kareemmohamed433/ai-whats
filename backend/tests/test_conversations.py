import pytest
from app import create_app
from app.extensions import db
from app.models import User, Customer, Conversation

@pytest.fixture
def app():
    app = create_app(test_config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        user = User(email="agent1@nexorasolutions.com", name="Agent", role="agent")
        user.set_password("password123")
        db.session.add(user)

        cust = Customer(name="Test Customer", phone="+201009988776")
        db.session.add(cust)
        db.session.flush()

        conv = Conversation(customer_id=cust.id, platform="whatsapp", platform_conversation_id="+201009988776")
        db.session.add(conv)
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_conversations_unauthenticated(client):
    res = client.get('/api/conversations')
    assert res.status_code == 401
