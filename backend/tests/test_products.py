import pytest
from app import create_app
from app.extensions import db
from app.models import Product, ServicePackage

@pytest.fixture
def app():
    app = create_app(test_config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        # Inactive old-business product should NOT be returned by active queries
        old_p = Product(name="زيت زيتون قديم", sku="OLD-1L", price=280.0, stock=0, is_active=False)
        # Active service package
        pkg = ServicePackage(
            slug="starter",
            name="Starter Package",
            name_ar="باقة البداية (Starter)",
            indicative_price_min=8000,
            indicative_price_max=12000,
            indicative_price_text="8,000 - 12,000 EGP",
            is_approved=False,
            is_active=True
        )
        db.session.add_all([old_p, pkg])
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_products_excludes_inactive(client):
    res = client.get('/api/products')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    # Inactive legacy product is excluded
    assert len(data["products"]) == 0

def test_get_service_packages(client):
    res = client.get('/api/packages')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["packages"]) == 1
    assert data["packages"][0]["slug"] == "starter"
    assert data["packages"][0]["is_approved"] is False

