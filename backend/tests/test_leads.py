import pytest
from app import create_app
from app.extensions import db
from app.models import User, Customer, Lead

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

        cust = Customer(name="Ahmed RealEstate", phone="+201011112222")
        db.session.add(cust)
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

def test_create_lead_success(client, auth_token):
    res = client.post('/api/leads', json={
        "contact_info": "+201011112222",
        "business_name": "Skyline Properties",
        "industry": "Real Estate",
        "requested_service": "Web Development + AI Chatbot",
        "package_interest": "Business",
        "budget": "25,000 - 30,000 EGP",
        "expected_timeline": "1 month",
        "lead_source": "whatsapp"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    lead = data["lead"]
    assert lead["business_name"] == "Skyline Properties"
    assert lead["status"] == "New"
    assert lead["package_interest"] == "Business"

def test_create_lead_validation_missing_contact(client, auth_token):
    res = client.post('/api/leads', json={
        "business_name": "No Contact Co."
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False
    assert "Contact information is required" in str(data["error"])

def test_update_lead_status(client, auth_token):
    # First create a lead
    create_res = client.post('/api/leads', json={
        "contact_info": "ceo@techcorp.io",
        "business_name": "TechCorp",
        "requested_service": "Custom ERP & Automation"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    lead_id = create_res.get_json()["lead"]["id"]

    # Transition to Qualified
    up_res = client.put(f'/api/leads/{lead_id}', json={
        "status": "Qualified",
        "notes": "Verified requirements with founder."
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert up_res.status_code == 200
    assert up_res.get_json()["lead"]["status"] == "Qualified"

    # Transition to Awaiting Human Review
    up_res2 = client.put(f'/api/leads/{lead_id}', json={
        "status": "Awaiting Human Review"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert up_res2.status_code == 200
    assert up_res2.get_json()["lead"]["status"] == "Awaiting Human Review"

    # Transition to Contacted
    up_res3 = client.put(f'/api/leads/{lead_id}', json={
        "status": "Contacted"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert up_res3.status_code == 200
    assert up_res3.get_json()["lead"]["status"] == "Contacted"

    # Transition to Closed
    up_res4 = client.put(f'/api/leads/{lead_id}', json={
        "status": "Closed"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert up_res4.status_code == 200
    assert up_res4.get_json()["lead"]["status"] == "Closed"

def test_update_lead_invalid_status(client, auth_token):
    create_res = client.post('/api/leads', json={
        "contact_info": "+20123456789",
        "requested_service": "Website"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    lead_id = create_res.get_json()["lead"]["id"]

    bad_res = client.put(f'/api/leads/{lead_id}', json={
        "status": "InvalidStatusXYZ"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert bad_res.status_code == 400

def test_list_leads_filtering(client, auth_token):
    # Fetch all leads
    res = client.get('/api/leads', headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert isinstance(data["leads"], list)
