from datetime import datetime, timezone
import json
from app.models import (
    Product, Customer, Order, OrderItem, StoreSettings, CompanySettings,
    SupportTicket, Conversation, InternalNote, ConversationAuditLog,
    PaymentReview, CustomerActivity, ServicePackage, Lead
)
from app.extensions import db
from app.services.socket_service import SocketService

NEXORA_PORTFOLIO_URL = "https://company-pi-two.vercel.app/"

# Structured verified portfolio knowledge source
NEXORA_PORTFOLIO_PROJECTS = [
    {
        "id": "travel-aura",
        "name": "ترافيل أورا للسياحة (Travel Aura)",
        "category": "السياحة والرحلات",
        "category_en": "Tourism & Travel",
        "description": "بوابة سياحية راقية تعرض أرقى الوجهات المتوسطية والاستوائية، مع مسار حجز واستفسار تفاعلي وتصوير فوتوغرافي استثنائي للرحلات.",
        "technologies": ["Next.js", "TypeScript", "Tailwind CSS"],
        "year": "2025",
        "public_url": NEXORA_PORTFOLIO_URL,
        "demo_url": f"{NEXORA_PORTFOLIO_URL}#work",
        "status": "Verified Showcase / Conceptual Demonstration",
        "source_url": NEXORA_PORTFOLIO_URL,
        "demonstrated_services": ["Web Development", "UI/UX Design", "Booking Flow"]
    },
    {
        "id": "la-casa",
        "name": "لاكازا للمأكولات الفاخرة (La Casa Fine Dining)",
        "category": "المطاعم والضيافة",
        "category_en": "Restaurants & Hospitality",
        "description": "تجربة رقمية سينمائية بالنمط الداكن لمطعم فاخر، تدمج منيو إلكتروني سريع عبر الـ QR، ومعرض أطباق احترافي، ونموذج حجز طاولات VIP.",
        "technologies": ["React", "Next.js", "Tailwind CSS"],
        "year": "2025",
        "public_url": NEXORA_PORTFOLIO_URL,
        "demo_url": f"{NEXORA_PORTFOLIO_URL}#work",
        "status": "Verified Showcase / Conceptual Demonstration",
        "source_url": NEXORA_PORTFOLIO_URL,
        "demonstrated_services": ["Web Development", "Interactive QR Menu", "Table Reservation"]
    },
    {
        "id": "vanta",
        "name": "ڤانتا للملابس العصرية (Vanta Streetwear)",
        "category": "أزياء وستريت وير",
        "category_en": "Fashion & Streetwear",
        "description": "منصة عرض أزياء عصرية بطابع أبيض وأسود جريء، تعتمد خطوطاً عريضة وتصويراً تحريرياً مميزاً، مع استعراض تفاعلي لأحدث الإصدارات وحقيبة تسوق تجريبية.",
        "technologies": ["Next.js", "TypeScript", "Tailwind CSS"],
        "year": "2025",
        "public_url": NEXORA_PORTFOLIO_URL,
        "demo_url": f"{NEXORA_PORTFOLIO_URL}#work",
        "status": "Verified Showcase / Conceptual Demonstration",
        "source_url": NEXORA_PORTFOLIO_URL,
        "demonstrated_services": ["E-Commerce UI", "Brand Experience", "Interactive Showcase"]
    },
    {
        "id": "aether-void",
        "name": "إيثر / ڤويد ٠٠ للأحذية (Aether Void 00)",
        "category": "أحذية مستقبلية ومنتجات مبتكرة",
        "category_en": "Futuristic Footwear",
        "description": "صفحة إطلاق مستقبلية لحذاء رياضي تجريبي، تعتمد النمط الداكن وإضاءات النيون السايان، مع استعراض المواصفات التقنية للمواد وتسجيل الحجز المسبق.",
        "technologies": ["Next.js", "TypeScript", "Tailwind CSS"],
        "year": "2025",
        "public_url": NEXORA_PORTFOLIO_URL,
        "demo_url": f"{NEXORA_PORTFOLIO_URL}#work",
        "status": "Verified Showcase / Conceptual Demonstration",
        "source_url": NEXORA_PORTFOLIO_URL,
        "demonstrated_services": ["Product Launch Landing Page", "Custom Motion & Neon Glow UI", "Pre-order Collection"]
    },
    {
        "id": "khaam-sinai-showcase",
        "name": "خام سينا — خيرات سيناء الطبيعية (Khaam Sinai Showcase)",
        "category": "المنتجات الطبيعية والمنصات المتكاملة",
        "category_en": "Brand Showcase Platform",
        "description": "منصة متكاملة لعلامة تجارية تحتفي بالهوية العربية الأصيلة مع كتالوج تفاعلي وطلب مباشر عبر واتساب.",
        "technologies": ["Next.js", "TypeScript", "Tailwind CSS"],
        "year": "2025",
        "public_url": NEXORA_PORTFOLIO_URL,
        "demo_url": f"{NEXORA_PORTFOLIO_URL}#work",
        "status": "Verified Showcase / Portfolio Demonstration",
        "source_url": NEXORA_PORTFOLIO_URL,
        "demonstrated_services": ["Interactive Catalog", "WhatsApp Direct Ordering Integration"]
    }
]


# ==========================================
# NEXORA Core AI Tools
# ==========================================

def get_portfolio_url():
    """Retrieve official NEXORA portfolio URL."""
    cs = CompanySettings.query.first()
    return cs.portfolio_url if (cs and cs.portfolio_url) else NEXORA_PORTFOLIO_URL


def get_portfolio_projects(category=None):
    """Retrieve structured verified portfolio projects."""
    if not category or category.lower() in ("all", "*", "الكل"):
        return NEXORA_PORTFOLIO_PROJECTS
    cat_lower = category.lower()
    return [
        p for p in NEXORA_PORTFOLIO_PROJECTS
        if cat_lower in p["category"].lower() or cat_lower in p["category_en"].lower()
    ]


def search_portfolio(category=None):
    """Retrieve structured verified portfolio projects with portfolio URL."""
    projects = get_portfolio_projects(category)
    return {
        "portfolio_url": get_portfolio_url(),
        "projects": projects
    }



def get_service_packages():
    """Retrieve all active NEXORA software service packages."""
    packages = ServicePackage.query.filter_by(is_active=True).order_by(ServicePackage.id.asc()).all()
    return [p.to_dict() for p in packages]


def get_service_package(slug):
    """Retrieve specific service package by slug."""
    pkg = ServicePackage.query.filter_by(slug=slug.lower()).first()
    return pkg.to_dict() if pkg else None


def get_company_info():
    """Retrieve NEXORA company information, official contacts, and working hours."""
    cs = CompanySettings.query.first()
    if cs:
        return cs.to_dict()
    st = StoreSettings.query.first()
    return st.to_dict() if st else {
        "company_name": "NEXORA Software Solutions",
        "tagline": "Ideas → Code → Impact",
        "phone": "+201556441133",
        "whatsapp": "+201556441133",
        "email": "contact@nexorasolutions.com",
        "address": "القاهرة، مصر",
        "portfolio_url": NEXORA_PORTFOLIO_URL
    }


def create_lead(customer_id=None, customer_name=None, contact_info=None,
                business_name=None, industry=None, requested_service='تطوير مواقع وبرمجيات',
                package_interest=None, project_description=None, budget=None,
                expected_timeline=None, lead_source='direct_chat', conversation_id=None):
    """Capture and record a qualified client project lead."""
    if conversation_id and not customer_id:
        conv = db.session.get(Conversation, conversation_id)
        if conv and conv.customer_id:
            customer_id = conv.customer_id

    if not contact_info and customer_id:
        cust = db.session.get(Customer, customer_id)
        if cust:
            contact_info = cust.phone or cust.email or f"Customer #{cust.id}"
            if not customer_name:
                customer_name = cust.name

    if not contact_info:
        contact_info = "محادثة عميل مباشرة"

    lead = Lead(
        customer_id=customer_id,
        customer_name=customer_name or "عميل مهتم",
        contact_info=contact_info,
        business_name=business_name,
        industry=industry,
        requested_service=requested_service,
        package_interest=package_interest,
        project_description=project_description,
        budget=budget,
        expected_timeline=expected_timeline,
        lead_source=lead_source,
        status='New'
    )
    db.session.add(lead)

    if customer_id:
        act = CustomerActivity(
            customer_id=customer_id,
            activity_type='new_lead',
            description=f"تم تسجيل طلب مشروع جديد: {requested_service}"
        )
        db.session.add(act)

    db.session.commit()
    return {"success": True, "lead": lead.to_dict()}


def get_customer_profile(customer_id):
    """Retrieve customer 360 profile by ID."""
    customer = db.session.get(Customer, customer_id)
    return customer.to_dict() if customer else None


def escalate_to_human(conversation_id, reason="customer_requested_human"):
    """Escalate conversation to human support staff, change ai_status to human_handled, add internal note & audit log."""
    conv = db.session.get(Conversation, conversation_id)
    if conv:
        prev_ai = conv.ai_status
        conv.ai_status = 'human_handled'
        conv.requires_human = True
        conv.human_handoff_at = datetime.now(timezone.utc)
        conv.priority = 'high'

        note = InternalNote(
            conversation_id=conversation_id,
            author_id=1,  # System
            content=f"🚨 تحويل تلقائي إلى فريق الدعم البشري بشركة NEXORA: {reason}"
        )
        db.session.add(note)

        audit = ConversationAuditLog(
            conversation_id=conversation_id,
            actor_type='system',
            actor_id='system',
            previous_ai_status=prev_ai,
            new_ai_status='human_handled',
            previous_conv_status=conv.conversation_status,
            new_conv_status=conv.conversation_status,
            reason=reason
        )
        db.session.add(audit)

        if conv.customer_id:
            act = CustomerActivity(
                customer_id=conv.customer_id,
                activity_type='request_human',
                description="طلب العميل التحدث مع فريق المبيعات والدعم الفني"
            )
            db.session.add(act)

        db.session.commit()

        SocketService.broadcast_ai_status_changed(conv, prev_ai, 'human_handled')
        SocketService.broadcast_human_handoff(conv, reason)
        SocketService.broadcast_conversation_update(conv)

        return {"success": True, "message": "تم تحويل المحادثة إلى ممثل خدمة عملاء NEXORA بنجاح."}
    return {"success": False, "error": "المحادثة غير موجودة"}


# ==========================================
# Legacy/Compatibility Functions
# ==========================================

def get_store_info():
    """Retrieve store info, policies, and contact details (Compatibility)."""
    return get_company_info()


def get_shipping_info():
    """Retrieve service delivery details (Compatibility)."""
    return {
        "shipping_policy": "خدمات برمجية ورقمية سحابية تُسلّم وتُنشر عبر الإنترنت.",
        "free_shipping_threshold": 0,
        "delivery_time": "يتم الاتفاق على موعد التسليم وجدول الإطلاق بحسب متطلبات المشروع."
    }


def get_payment_methods():
    """Retrieve available payment methods (Compatibility)."""
    return {
        "payment_methods": "التحويل البنكي، إنستا باي (InstaPay)، فودافون كاش، وبطاقات الدفع الإلكتروني المعتمدة."
    }


def get_products():
    """Retrieve active physical products (Excludes old business data)."""
    products = Product.query.filter_by(is_active=True).all()
    return [p.to_dict() for p in products]


def get_product(product_id):
    """Retrieve specific product by ID."""
    product = db.session.get(Product, product_id)
    return product.to_dict() if product else None


def get_product_link(product_id):
    """Get official URL."""
    return f"{NEXORA_PORTFOLIO_URL}#services"


def search_products(query):
    """Search products (Compatibility)."""
    if not query:
        return get_products()
    pattern = f"%{query}%"
    products = Product.query.filter(
        Product.is_active == True,
        db.or_(
            Product.name.ilike(pattern),
            Product.description.ilike(pattern),
            Product.category.ilike(pattern)
        )
    ).all()
    return [p.to_dict() for p in products]


def check_product_stock(product_id):
    """Check stock availability (Compatibility)."""
    return {"product_id": product_id, "stock": 999, "in_stock": True}


def get_customer_orders(customer_id):
    orders = Order.query.filter_by(customer_id=customer_id).all()
    return [o.to_dict() for o in orders]


def get_order(order_number):
    order = Order.query.filter_by(order_number=order_number).first()
    return order.to_dict() if order else None


def search_orders(query):
    pattern = f"%{query}%"
    orders = Order.query.filter(Order.order_number.ilike(pattern)).all()
    return [o.to_dict() for o in orders]


def create_order(customer_id, items, shipping_address=None, city="القاهرة", confirmed=True, conversation_id=None):
    """Legacy order creation wrapper."""
    return {"success": False, "error": "تم استبدال نظام الطلبات بنظام طلب المشروعات والعروض البرمجية."}


def create_payment_review(customer_id, order_id=None, conversation_id=None, screenshot_url=None, detected_amount=None, reference_number=None, ocr_data_json=None):
    """Legacy payment review."""
    review = PaymentReview(
        customer_id=customer_id,
        order_id=order_id,
        conversation_id=conversation_id,
        detected_amount=detected_amount,
        reference_number=reference_number,
        screenshot_url=screenshot_url,
        ocr_data_json=ocr_data_json,
        status='pending'
    )
    db.session.add(review)
    db.session.commit()
    return review.to_dict()


def get_or_create_order_draft(conversation_id):
    conv = db.session.get(Conversation, conversation_id)
    return conv.order_draft if conv else None


def update_order_draft(conversation_id, **kwargs):
    conv = db.session.get(Conversation, conversation_id)
    if conv:
        current = conv.order_draft or {}
        current.update(kwargs)
        conv.order_draft = current
        db.session.commit()
        return current
    return None


def clear_order_draft(conversation_id):
    conv = db.session.get(Conversation, conversation_id)
    if conv:
        conv.order_draft = None
        db.session.commit()
