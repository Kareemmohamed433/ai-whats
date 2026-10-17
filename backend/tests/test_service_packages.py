import pytest
from app import create_app
from app.extensions import db
from app.models import User, ServicePackage

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

        p1 = ServicePackage(
            slug="starter",
            name="Starter Package",
            name_ar="باقة البداية (Starter)",
            description="مثالية للشركات الناشئة والمشاريع الصغيرة",
            target_audience="Startups, freelancers, small businesses",
            indicative_price_min=8000,
            indicative_price_max=12000,
            indicative_price_text="8,000 - 12,000 EGP",
            currency="EGP",
            support_period="أسبوعين من الدعم الفني بعد الإطلاق",
            is_approved=False,
            is_popular=False,
            is_active=True
        )
        p2 = ServicePackage(
            slug="business",
            name="Business Package",
            name_ar="باقة الأعمال (Business)",
            description="الباقة الأكثر طلباً للشركات في مرحلة النمو",
            target_audience="Growing businesses needing complete online presence",
            indicative_price_min=20000,
            indicative_price_max=35000,
            indicative_price_text="20,000 - 35,000 EGP",
            currency="EGP",
            support_period="شهر كامل من الدعم والصيانة المجانية",
            is_approved=False,
            is_popular=True,
            is_active=True
        )
        p3 = ServicePackage(
            slug="enterprise",
            name="Enterprise & Custom Solutions",
            name_ar="باقة الشركات والحلول المخصصة (Enterprise)",
            description="حلول مخصصة للشركات الكبيرة ذات الاحتياجات المعقدة",
            target_audience="Enterprises requiring custom software, advanced AI, integrations",
            indicative_price_min=None,
            indicative_price_max=None,
            indicative_price_text="عرض سعر مخصص (Custom Quotation)",
            currency="EGP",
            support_period="دعم وأولوية صيانة مستمرة حسب الاتفاق",
            is_approved=False,
            is_popular=False,
            is_active=True
        )
        db.session.add_all([p1, p2, p3])
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

def test_list_service_packages(client):
    res = client.get('/api/packages')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["packages"]) == 3
    
    slugs = [p["slug"] for p in data["packages"]]
    assert "starter" in slugs
    assert "business" in slugs
    assert "enterprise" in slugs

    # Verify Business is popular
    biz = next(p for p in data["packages"] if p["slug"] == "business")
    assert biz["is_popular"] is True
    assert biz["indicative_price_min"] == 20000
    assert biz["indicative_price_max"] == 35000
    assert biz["is_approved"] is False

def test_get_single_package(client):
    res = client.get('/api/packages/starter')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["package"]["name"] == "Starter Package"
    assert data["package"]["indicative_price_min"] == 8000

def test_get_nonexistent_package(client):
    res = client.get('/api/packages/nonexistent')
    assert res.status_code == 404

def test_update_package_admin(client, auth_token):
    res = client.put('/api/packages/starter', json={
        "is_approved": True,
        "indicative_price_text": "10,000 - 14,000 EGP",
        "features": ["صفحة هبوط احترافية متجاوبة", "ربط واتساب مباشر"]
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["package"]["is_approved"] is True
    assert data["package"]["indicative_price_text"] == "10,000 - 14,000 EGP"
    assert len(data["package"]["features"]) == 2

def test_create_custom_package(client, auth_token):
    res = client.post('/api/packages', json={
        "name": "AI Automation Addon",
        "slug": "ai-automation-addon",
        "name_ar": "باقة أتمتة الذكاء الاصطناعي",
        "indicative_price_text": "5,000 - 10,000 EGP",
        "currency": "EGP",
        "features": ["ربط n8n", "تكامل CRM"]
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert data["package"]["slug"] == "ai-automation-addon"
