import pytest
from app import create_app
from app.extensions import db
from app.models import User, Customer, CustomerIdentity, Conversation, Message, AISettings
from app.routes.webhooks import _process_incoming_message
from app.services.ai_service import HANDOFF_MESSAGE, AIService

from sqlalchemy.pool import StaticPool

@pytest.fixture
def app():
    app = create_app(test_config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool
        }
    })

    with app.app_context():
        db.create_all()

        agent = User(email="agent1@nexorasolutions.com", name="NEXORA Agent", role="agent")
        agent.set_password("password123")
        db.session.add(agent)

        cust = Customer(name="Test Customer", phone="+201009988776")
        db.session.add(cust)
        db.session.flush()

        ai_set = AISettings(
            provider="openai",
            model="gpt-4o-mini",
            api_key="", # Local fallback rule engine
            is_enabled=True
        )
        db.session.add(ai_set)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# Test 1 — Normal AI
def test_normal_ai_response(app):
    with app.app_context():
        conv = _process_incoming_message(
            platform="whatsapp",
            platform_user_id="+201009988776",
            customer_name="Test Customer",
            content="السلام عليكم، بتعملوا مواقع إلكترونية وشات بوت؟"
        )
        assert conv.conversation_status == "open"
        assert conv.ai_status == "active"
        
        msgs = Message.query.filter_by(conversation_id=conv.id).all()
        assert len(msgs) == 2
        assert msgs[0].sender_type == "customer"
        assert msgs[1].sender_type == "ai"

# Test 2 — Human Request
def test_human_request_escalation(app):
    with app.app_context():
        conv = _process_incoming_message(
            platform="telegram",
            platform_user_id="chat_12345",
            customer_name="Human Requester",
            content="عايز أكلم خدمة العملاء"
        )
        assert conv.conversation_status == "open"
        assert conv.ai_status == "human_handled"
        assert conv.requires_human is True

        msgs = Message.query.filter_by(conversation_id=conv.id).all()
        assert len(msgs) == 2
        assert msgs[1].content == HANDOFF_MESSAGE

        # Future customer messages should receive NO AI response
        _process_incoming_message(
            platform="telegram",
            platform_user_id="chat_12345",
            customer_name="Human Requester",
            content="ممكن ترد عليا سريعا؟"
        )
        msgs_after = Message.query.filter_by(conversation_id=conv.id).all()
        assert len(msgs_after) == 3 # No new AI message added
        assert msgs_after[2].sender_type == "customer"

# Test 3 — Agent Reply
def test_agent_reply(app, client):
    with app.app_context():
        cust = Customer(name="Agent Reply Cust", phone="+201003030303")
        db.session.add(cust)
        db.session.flush()
        identity = CustomerIdentity(customer_id=cust.id, platform="whatsapp", platform_user_id="+201003030303")
        conv = Conversation(customer_id=cust.id, platform="whatsapp", platform_conversation_id="+201003030303", ai_status="human_handled")
        db.session.add_all([identity, conv])
        db.session.commit()
        conv_id = conv.id

    # Agent logs in & replies
    login_res = client.post('/api/auth/login', json={"email": "agent1@nexorasolutions.com", "password": "password123"})
    token = login_res.get_json()["token"]

    reply_res = client.post('/api/messages', json={
        "conversation_id": conv_id,
        "content": "أهلاً بك، معك مهندس الدعم من NEXORA كيف يمكنني مساعدتك؟"
    }, headers={"Authorization": f"Bearer {token}"})

    assert reply_res.status_code == 201
    
    with app.app_context():
        conv_after = db.session.get(Conversation, conv_id)
        assert conv_after.ai_status == "human_handled"

# Test 4 — Human Re-enables AI
def test_human_reenables_ai(app, client):
    with app.app_context():
        cust = Customer(name="Reenable Cust", phone="+201004040404")
        db.session.add(cust)
        db.session.flush()
        identity = CustomerIdentity(customer_id=cust.id, platform="whatsapp", platform_user_id="+201004040404")
        conv = Conversation(customer_id=cust.id, platform="whatsapp", platform_conversation_id="+201004040404", ai_status="human_handled")
        db.session.add_all([identity, conv])
        db.session.commit()
        conv_id = conv.id

    login_res = client.post('/api/auth/login', json={"email": "agent1@nexorasolutions.com", "password": "password123"})
    token = login_res.get_json()["token"]

    # Click 🤖 تفعيل AI
    res = client.put(f'/api/conversations/{conv_id}/status', json={
        "ai_status": "active"
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200

    with app.app_context():
        conv_after = db.session.get(Conversation, conv_id)
        assert conv_after.ai_status == "active"
        assert conv_after.conversation_status == "open"

        # Next message is handled by AI
        _process_incoming_message(
            platform="whatsapp",
            platform_user_id="+201004040404",
            customer_name="Reenable Cust",
            content="عايز أعرف تفاصيل باقات تطوير المواقع وتكلفتها؟"
        )
        msgs = Message.query.filter_by(conversation_id=conv_id).all()
        assert msgs[-1].sender_type == "ai"

# Test 5 — Close + Reactivate AI
def test_close_and_reactivate_ai(app, client):
    with app.app_context():
        cust = Customer(name="Close & Reactivate Cust", phone="+201005050505")
        db.session.add(cust)
        db.session.flush()
        identity = CustomerIdentity(customer_id=cust.id, platform="whatsapp", platform_user_id="+201005050505")
        conv = Conversation(customer_id=cust.id, platform="whatsapp", platform_conversation_id="+201005050505", conversation_status="open", ai_status="human_handled")
        db.session.add_all([identity, conv])
        db.session.commit()
        conv_id = conv.id

    login_res = client.post('/api/auth/login', json={"email": "agent1@nexorasolutions.com", "password": "password123"})
    token = login_res.get_json()["token"]

    # Agent clicks: إغلاق المحادثة وإعادة تفعيل AI
    res = client.put(f'/api/conversations/{conv_id}/status', json={
        "conversation_status": "closed",
        "ai_status": "active"
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200

    with app.app_context():
        conv_after = db.session.get(Conversation, conv_id)
        assert conv_after.conversation_status == "closed"
        assert conv_after.ai_status == "active"

        # Customer sends a new message later
        _process_incoming_message(
            platform="whatsapp",
            platform_user_id="+201005050505",
            customer_name="Close & Reactivate Cust",
            content="السلام عليكم، هل باقة Starter تشمل الدومين والاستضافة؟"
        )
        conv_reopened = db.session.get(Conversation, conv_id)
        assert conv_reopened.conversation_status == "open"
        assert conv_reopened.ai_status == "active"
        msgs = Message.query.filter_by(conversation_id=conv_id).all()
        assert msgs[-1].sender_type == "ai"

# Test 6 — Close Without Reactivating AI
def test_close_without_reactivating_ai(app, client):
    with app.app_context():
        cust = Customer(name="Close Only Cust", phone="+201006060606")
        db.session.add(cust)
        db.session.flush()
        identity = CustomerIdentity(customer_id=cust.id, platform="whatsapp", platform_user_id="+201006060606")
        conv = Conversation(customer_id=cust.id, platform="whatsapp", platform_conversation_id="+201006060606", conversation_status="open", ai_status="human_handled")
        db.session.add_all([identity, conv])
        db.session.commit()
        conv_id = conv.id

    login_res = client.post('/api/auth/login', json={"email": "agent1@nexorasolutions.com", "password": "password123"})
    token = login_res.get_json()["token"]

    # Agent clicks: إغلاق المحادثة (only close, keep human_handled)
    res = client.put(f'/api/conversations/{conv_id}/status', json={
        "conversation_status": "closed"
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200

    with app.app_context():
        conv_after = db.session.get(Conversation, conv_id)
        assert conv_after.conversation_status == "closed"
        assert conv_after.ai_status == "human_handled"

        # Customer sends a new message
        _process_incoming_message(
            platform="whatsapp",
            platform_user_id="+201006060606",
            customer_name="Close Only Cust",
            content="ممكن متابعة حالة مشروعي والتنفيذ؟"
        )
        conv_reopened = db.session.get(Conversation, conv_id)
        assert conv_reopened.conversation_status == "open"
        assert conv_reopened.ai_status == "human_handled"
        msgs = Message.query.filter_by(conversation_id=conv_id).all()
        assert msgs[-1].sender_type == "customer" # NO AI response!

# Test 7 — Race Condition Protection
def test_race_condition_protection(app):
    with app.app_context():
        cust = Customer(name="Race Cust", phone="+201007070707")
        db.session.add(cust)
        db.session.flush()
        identity = CustomerIdentity(customer_id=cust.id, platform="whatsapp", platform_user_id="+201007070707")
        conv = Conversation(customer_id=cust.id, platform="whatsapp", platform_conversation_id="+201007070707", conversation_status="open", ai_status="active")
        db.session.add_all([identity, conv])
        db.session.commit()

        # Simulate agent takeover during generation
        conv.ai_status = "human_handled"
        db.session.commit()

        # Call generate_response
        reply = AIService.generate_response(conv.id, "السلام عليكم")
        assert reply is None # AI response blocked by Race Condition Guard!

