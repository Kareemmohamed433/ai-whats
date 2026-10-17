import pytest
from app import create_app
from app.extensions import db
from app.models import Customer, Conversation, Message, AISettings, ServicePackage, CompanySettings
from app.services.ai_service import AIService, HANDOFF_MESSAGE
from app.services.ai_tools import (
    search_portfolio,
    get_service_packages,
    get_company_info,
    create_lead,
    escalate_to_human
)

@pytest.fixture
def app():
    app = create_app(test_config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()

        ai_set = AISettings(
            provider="openai",
            model="gpt-4o-mini",
            api_key="", # Test local rule/tool fallback
            is_enabled=True
        )
        comp = CompanySettings(
            company_name="NEXORA Software Solutions",
            tagline="Ideas → Code → Impact",
            portfolio_url="https://company-pi-two.vercel.app/",
            email="contact@nexorasolutions.com",
            phone="+20 155 644 1133"
        )
        p1 = ServicePackage(
            slug="starter",
            name="Starter Package",
            name_ar="باقة البداية (Starter)",
            indicative_price_text="8,000 - 12,000 EGP",
            is_approved=False,
            is_active=True
        )
        p2 = ServicePackage(
            slug="business",
            name="Business Package",
            name_ar="باقة الأعمال (Business)",
            indicative_price_text="20,000 - 35,000 EGP",
            is_approved=False,
            is_popular=True,
            is_active=True
        )
        db.session.add_all([ai_set, comp, p1, p2])

        cust = Customer(name="Tarek Tech", phone="+201099887766")
        db.session.add(cust)
        db.session.flush()

        conv = Conversation(
            customer_id=cust.id,
            platform="whatsapp",
            platform_conversation_id="+201099887766",
            ai_status="active"
        )
        db.session.add(conv)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

def test_portfolio_inquiry_arabic(app):
    with app.app_context():
        conv = Conversation.query.first()
        reply = AIService.generate_response(conv.id, "ممكن أشوف شغلكم وسوابق الأعمال؟")
        assert reply is not None
        assert "https://company-pi-two.vercel.app/" in reply
        assert "بورتفوليو" in reply or "نماذج" in reply

def test_portfolio_inquiry_english(app):
    with app.app_context():
        conv = Conversation.query.first()
        reply = AIService.generate_response(conv.id, "Can I see your portfolio and previous work?")
        assert reply is not None
        assert "https://company-pi-two.vercel.app/" in reply
        assert "portfolio" in reply.lower() or "showcase" in reply.lower()

def test_pricing_inquiry_indicative_notice(app):
    with app.app_context():
        conv = Conversation.query.first()
        reply = AIService.generate_response(conv.id, "بكام تصميم موقع عندكم؟")
        assert reply is not None
        assert "8,000" in reply or "20,000" in reply or "تقديرية" in reply or "عرض سعر" in reply
        # Must clearly indicate that pricing depends on project requirements
        assert "متطلبات" in reply or "تقديرية" in reply or "نطاق" in reply

def test_ai_solutions_inquiry(app):
    with app.app_context():
        conv = Conversation.query.first()
        reply = AIService.generate_response(conv.id, "عايز شات بوت ذكي للرد على العملاء على واتساب")
        assert reply is not None
        assert "شات بوت" in reply or "ذكاء اصطناعي" in reply or "واتساب" in reply

def test_human_escalation_detection(app):
    with app.app_context():
        conv = Conversation.query.first()
        reply = AIService.generate_response(conv.id, "عايز أكلم خدمة العملاء أو حد بشري")
        assert reply == HANDOFF_MESSAGE
        # Verify conversation state was updated to human_handled
        refreshed_conv = db.session.get(Conversation, conv.id)
        assert refreshed_conv.ai_status == "human_handled"

def test_no_old_business_leakage(app):
    with app.app_context():
        conv = Conversation.query.first()
        test_prompts = [
            "إيه المنتجات اللي عندكم؟",
            "بكام التوصيل والشحن؟",
            "عايز أشتري زيت زيتون وعسل",
            "عندكم حجم 1 لتر و2 لتر؟"
        ]
        forbidden_keywords = [
            "زيت زيتون", "خام سينا", "شحن مجاني", "عسل جبلي",
            "شحن للمحافظات", "لتر", "مليلتر"
        ]
        for prompt in test_prompts:
            reply = AIService.generate_response(conv.id, prompt)
            assert reply is not None
            for kw in forbidden_keywords:
                assert kw not in reply, f"Old business keyword '{kw}' leaked in response to '{prompt}': {reply}"

def test_ai_tools_search_portfolio(app):
    with app.app_context():
        results = search_portfolio(category="all")
        assert "company-pi-two.vercel.app" in results["portfolio_url"]
        assert len(results["projects"]) > 0
        names = [p["name"] for p in results["projects"]]
        assert any("Travel Aura" in name for name in names) or any("La Casa" in name for name in names)

def test_ai_tools_get_service_packages(app):
    with app.app_context():
        packages = get_service_packages()
        assert len(packages) >= 2
        slugs = [p["slug"] for p in packages]
        assert "starter" in slugs
        assert "business" in slugs

def test_ai_tools_create_lead(app):
    with app.app_context():
        conv = Conversation.query.first()
        res = create_lead(
            conversation_id=conv.id,
            contact_info="+201099887766",
            business_name="Al-Nour Real Estate",
            requested_service="Website + Chatbot",
            budget="25,000 EGP"
        )
        assert res["success"] is True
        assert res["lead"]["business_name"] == "Al-Nour Real Estate"
