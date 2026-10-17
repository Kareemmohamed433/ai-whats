import pytest
from app import create_app
from app.extensions import db
from app.models import User, ServicePackage, FAQ, QuickReply, Product, CompanySettings
from app.utils.seed import seed_database

@pytest.fixture
def app():
    app = create_app(test_config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

def test_seed_database_fresh(app):
    with app.app_context():
        seed_database()

        # Check Users
        users = User.query.all()
        assert len(users) == 4
        emails = [u.email for u in users]
        assert "admin@nexorasolutions.com" in emails
        assert "manager@nexorasolutions.com" in emails
        assert "agent1@nexorasolutions.com" in emails
        assert "agent2@nexorasolutions.com" in emails

        # Check Service Packages
        pkgs = ServicePackage.query.all()
        assert len(pkgs) == 3
        slugs = [p.slug for p in pkgs]
        assert "starter" in slugs
        assert "business" in slugs
        assert "enterprise" in slugs

        # Check indicative price unapproved
        for p in pkgs:
            assert p.is_approved is False

        # Check FAQs
        faqs = FAQ.query.filter_by(is_active=True).all()
        assert len(faqs) == 8

        # Check Quick Replies
        qrs = QuickReply.query.filter_by(is_enabled=True).all()
        assert len(qrs) == 11
        shortcuts = [q.shortcut for q in qrs]
        assert "/portfolio" in shortcuts
        assert "/services" in shortcuts
        assert "/pricing" in shortcuts
        assert "/packages" in shortcuts

        # Check Company Settings
        settings = CompanySettings.query.first()
        assert settings is not None
        assert settings.company_name == "NEXORA Software Solutions"
        assert settings.portfolio_url == "https://company-pi-two.vercel.app/"

def test_seed_database_idempotent(app):
    with app.app_context():
        # First run
        seed_database()
        user_count_1 = User.query.count()
        pkg_count_1 = ServicePackage.query.count()
        faq_count_1 = FAQ.query.count()
        qr_count_1 = QuickReply.query.count()

        # Second run immediately
        seed_database()
        user_count_2 = User.query.count()
        pkg_count_2 = ServicePackage.query.count()
        faq_count_2 = FAQ.query.count()
        qr_count_2 = QuickReply.query.count()

        # Assert no duplicates were created
        assert user_count_1 == user_count_2 == 4
        assert pkg_count_1 == pkg_count_2 == 3
        assert faq_count_1 == faq_count_2 == 8
        assert qr_count_1 == qr_count_2 == 11

def test_legacy_products_deactivated_in_seed(app):
    with app.app_context():
        # Inject old physical product
        old_prod = Product(
            name="زيت زيتون بكر ممتاز 1 لتر",
            sku="LEGACY-OIL-1L",
            price=300.0,
            stock=10,
            is_active=True
        )
        db.session.add(old_prod)
        db.session.commit()

        # Run seed
        seed_database()

        # Verify old product is now deactivated
        refreshed = db.session.get(Product, old_prod.id)
        assert refreshed.is_active is False
