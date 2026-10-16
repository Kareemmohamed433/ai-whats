import pytest
from app import create_app
from app.extensions import db
from app.models import Product

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        p = Product(name="زيت زيتون 1 لتر", sku="TEST-1L", price=280.0, stock=50)
        db.session.add(p)
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_products(client):
    res = client.get('/api/products')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["products"]) >= 1
