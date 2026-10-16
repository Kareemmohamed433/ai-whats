from datetime import datetime, timedelta
from app.extensions import db
from app.models import (
    User, Customer, CustomerIdentity, Conversation, Message,
    Product, Category, Order, OrderItem, FAQ, KnowledgeBaseArticle,
    QuickReply, Integration, Tag, StoreSettings, AISettings
)
import os

def seed_database():
    """Seed initial production data for Khams Sinaa brand."""
    # 1. Users
    if not User.query.first():
        admin = User(email="admin@khams-sinaa.eg", name="أحمد الشريف", role="admin", status="online")
        admin.set_password("admin123")

        manager = User(email="manager@khams-sinaa.eg", name="سارة محمود", role="manager", status="online")
        manager.set_password("manager123")

        agent1 = User(email="agent1@khams-sinaa.eg", name="محمد طارق", role="agent", status="online")
        agent1.set_password("agent123")

        agent2 = User(email="agent2@khams-sinaa.eg", name="ريم العبدالله", role="agent", status="away")
        agent2.set_password("agent123")

        db.session.add_all([admin, manager, agent1, agent2])
        db.session.flush()

    # Quick Replies Seed
    if not QuickReply.query.first():
        qr1 = QuickReply(title="ترحيب بالعميل", shortcut="/hello", category="welcome", response_text="أهلاً بك في خام سينا 🌿! يسعدنا مساعدتك في اختيار أجود منتجات زيت الزيتون البكر الممتاز.")
        qr2 = QuickReply(title="إثبات الدفع", shortcut="/payment", category="payment", response_text="تم استلام صورة إثبات الدفع، وسيتم مراجعتها من فريق خدمة العملاء وتأكيد العملية قريبًا.")
        qr3 = QuickReply(title="متابعة الشحنة", shortcut="/order", category="order", response_text="جاري متابعة طلبك مع شركة الشحن وسنوافيك بالتحديثات فوراً 🚚.")
        qr4 = QuickReply(title="سياسة الشحن", shortcut="/shipping", category="shipping", response_text="نوصل لجميع محافظات مصر خلال 2-4 أيام عمل. الشحن مجاني للطلبات فوق 500 ج.م!")
        qr5 = QuickReply(title="تحويل لموظف", shortcut="/human", category="customer_service", response_text="سيتم تحويل محادثتك لأحد أفراد فريق خدمة العملاء لمتابعة استفسارك بالتفصيل.")
        qr6 = QuickReply(title="إغلاق المحادثة", shortcut="/closing", category="closing", response_text="شكراً لتواصلك مع خام سينا! نتمنى لك يوماً سعيداً 🌿.")
        db.session.add_all([qr1, qr2, qr3, qr4, qr5, qr6])

    # 2. Store Settings
    if not StoreSettings.query.first():
        store = StoreSettings(
            store_name="خام سينا - Khams Sinaa",
            phone="+201001234567",
            whatsapp="+201001234567",
            email="support@khams-sinaa.eg",
            address="العريش - محافظة شمال سيناء / المقر الرئيسي: القاهرة، مصر",
            shipping_policy="نوصل لكافة المحافظات خلال 2 إلى 4 أيام عمل بحفظ خاص للمنتجات الطبيعية.",
            free_shipping_threshold=500.0,
            payment_methods="الدفع عند الاستلام، إنستا باي (InstaPay)، فودافون كاش، بطاقات الائتمان",
            return_policy="إمكانية الاستبدال والاسترجاع خلال 14 يوماً من الاستلام بشرط احتفاظ المنتج بغلافه الأصلي."
        )
        db.session.add(store)

    # 3. AI Settings
    ai_set = AISettings.query.first()
    if not ai_set:
        ai_set = AISettings(
            provider="groq",
            api_key=os.getenv("AI_API_KEY", "a7cf8f22-0653-4500-a4fc-b93b5ba64ba7"),
            api_base_url="https://api.groq.com/openai/v1",
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=500,
            is_enabled=True
        )
        db.session.add(ai_set)
    else:
        ai_set.api_key = os.getenv("AI_API_KEY", "a7cf8f22-0653-4500-a4fc-b93b5ba64ba7")

    # 4. Categories & Products
    if not Category.query.first():
        cat_oil = Category(name="زيت زيتون سيناوي", slug="olive-oil", description="زيت زيتون بكر ممتاز معصور على البارد من مزارع العريش والشيخ زويد.")
        cat_honey = Category(name="عسل طبيعي", slug="natural-honey", description="عسل جبلي وعسل سدر سيناوي طبيعي 100%.")
        cat_herbs = Category(name="أعشاب ونباتات طبيعية", slug="herbs", description="مرمية سيناوية، حبق، وزعتر جبلي طبيعي.")
        cat_dates = Category(name="تمور سيناوية الممتازة", slug="dates", description="تمور سيناوية فاخرة جافة ورطبة.")

        db.session.add_all([cat_oil, cat_honey, cat_herbs, cat_dates])
        db.session.flush()

        p1 = Product(
            name="زيت زيتون بكر ممتاز - عبوة 1 لتر",
            sku="KS-OIL-1L",
            category_id=cat_oil.id,
            category="زيت زيتون سيناوي",
            description="زيت زيتون سيناوي بكر ممتاز معصور على البارد، حموضة أقل من 0.8%، طعم ونكهة ممتازة.",
            price=280.0,
            original_price=320.0,
            discount=12.5,
            stock=150,
            packaging_type="عبوة زجاجية داكنة 1 لتر",
            image_url="https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&auto=format&fit=crop&q=80",
            specifications="عصرة أولى على البارد - نسبة حموضة < 0.8% - خالي من أية إضافات"
        )
        p2 = Product(
            name="زيت زيتون بكر ممتاز - عبوة 2 لتر",
            sku="KS-OIL-2L",
            category_id=cat_oil.id,
            category="زيت زيتون سيناوي",
            description="توفير العائلة: عبوة 2 لتر من أجود زيت زيتون بكر سيناوي صافي 100%.",
            price=530.0,
            original_price=600.0,
            discount=11.6,
            stock=90,
            packaging_type="جالون زجاجي/معدني 2 لتر",
            image_url="https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&auto=format&fit=crop&q=80",
            specifications="عصرة أولى على البارد - معصورة حديثاً"
        )
        p3 = Product(
            name="عسل سدر سيناوي جبلي - 500 جرام",
            sku="KS-HONEY-SDR500",
            category_id=cat_honey.id,
            category="عسل طبيعي",
            description="عسل سدر طبيعي 100% مستخرج من مناحل جنوب وشمال سيناء الطبيعية.",
            price=420.0,
            original_price=480.0,
            discount=12.5,
            stock=45,
            packaging_type="برطمان زجاجي فاخر 500 جرام",
            image_url="https://images.unsplash.com/photo-1587049352847-81a56d773cae?w=500&auto=format&fit=crop&q=80",
            specifications="عسل سدر نقي 100% خالي من السكر المضاف"
        )
        p4 = Product(
            name="مرمية سيناوية جبلية فاخرة - 250 جرام",
            sku="KS-HERB-MARW250",
            category_id=cat_herbs.id,
            category="أعشاب ونباتات طبيعية",
            description="أوراق المرمية السيناوية الطبيعية المقطوفة يدوياً من جبال سيناء.",
            price=95.0,
            original_price=120.0,
            discount=20.8,
            stock=200,
            packaging_type="كيس حراري محكم الإغلاق 250 جرام",
            image_url="https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=500&auto=format&fit=crop&q=80",
            specifications="أعشاب طبيعية جبلية 100%"
        )

        db.session.add_all([p1, p2, p3, p4])

    # 5. FAQs
    if not FAQ.query.first():
        faqs = [
            FAQ(question="ما هي أسعار زيت الزيتون في خام سينا؟", answer="نوفر عبوة 1 لتر بسعر 280 ج.م، وعبوة 2 لتر بسعر 530 ج.م. جميعها عصره أولى على البارد."),
            FAQ(question="كم استغرق الشحن والتوصيل؟", answer="يصلكم الطلب خلال 2 إلى 4 أيام عمل لجميع محافظات جمهورية مصر العربية."),
            FAQ(question="هل الشحن مجاني؟", answer="نعم! الشحن مجاني تماماً لأي طلب بقيمة 500 جنيه مصري أو أكثر."),
            FAQ(question="ما هي طرق الدفع المتاحة؟", answer="يمكنكم الدفع عند الاستلام، أو عبر إنستا باي (InstaPay)، أو محفظة فودافون كاش، أو الفيزا.")
        ]
        db.session.add_all(faqs)

    # 6. Tags
    if not Tag.query.first():
        tags = [
            Tag(name="عميل مميز", color="#10B981"),
            Tag(name="طلب جديد", color="#3B82F6"),
            Tag(name="استفسار أسعار", color="#8B5CF6"),
            Tag(name="شكوى شحن", color="#EF4444")
        ]
        db.session.add_all(tags)

    # 7. Customers & Conversations Seed Data
    if not Customer.query.first():
        c1 = Customer(name="مهندس عمرو فاروق", phone="+201011223344", email="amr@gmail.com", notes="عميل دائم يطلب جالون 2 لتر شهرياً.")
        c2 = Customer(name="د. نورهان الكردي", phone="+201144556677", email="nourhan@yahoo.com", notes="مهتمة بأعشاب المرمية والعسل الجبلي.")
        c3 = Customer(name="خالد الصاوي", phone="+201277889900", notes="عميل إنستغرام متكرر الشراء.")
        c4 = Customer(name="إبراهيم مصطفى", phone="+201500112233", notes="عميل تيليجرام.")

        db.session.add_all([c1, c2, c3, c4])
        db.session.flush()

        # Identities
        i1 = CustomerIdentity(customer_id=c1.id, platform="whatsapp", platform_user_id="+201011223344", username="amr_farouk")
        i2 = CustomerIdentity(customer_id=c2.id, platform="whatsapp", platform_user_id="+201144556677", username="nourhan_k")
        i3 = CustomerIdentity(customer_id=c3.id, platform="instagram", platform_user_id="ig_khaled_99", username="@khaled_elsawy")
        i4 = CustomerIdentity(customer_id=c4.id, platform="telegram", platform_user_id="tg_ibrahim_44", username="@ibrahim_m")

        db.session.add_all([i1, i2, i3, i4])
        db.session.flush()

        # Conversations
        conv1 = Conversation(customer_id=c1.id, platform="whatsapp", platform_conversation_id="+201011223344", assigned_agent_id=3, ai_enabled=True, status="open", unread_count=1)
        conv2 = Conversation(customer_id=c2.id, platform="whatsapp", platform_conversation_id="+201144556677", assigned_agent_id=4, ai_enabled=False, status="waiting", unread_count=0)
        conv3 = Conversation(customer_id=c3.id, platform="instagram", platform_conversation_id="ig_khaled_99", assigned_agent_id=3, ai_enabled=True, status="open", unread_count=2)
        conv4 = Conversation(customer_id=c4.id, platform="telegram", platform_conversation_id="tg_ibrahim_44", assigned_agent_id=None, ai_enabled=True, status="resolved", unread_count=0)

        db.session.add_all([conv1, conv2, conv3, conv4])
        db.session.flush()

        # Messages
        m1 = Message(conversation_id=conv1.id, sender_type="customer", content="السلام عليكم، محتاج أعرف أسعار زيت الزيتون عالي الجودة وحجم العبوات؟", created_at=datetime.utcnow() - timedelta(minutes=15))
        m2 = Message(conversation_id=conv1.id, sender_type="ai", content="وعليكم السلام ورحمة الله وبركاته 🌿 أهلاً بك في خام سينا! لدينا زيت زيتون سيناوي بكر ممتاز معصور على البارد:\n• عبوة 1 لتر: 280 ج.م\n• عبوة 2 لتر (عائلية): 530 ج.م\n\nالشحن مجاني للطلبات فوق 500 ج.م. هل تود تأكيد طلب عبوة 2 لتر الآن؟", created_at=datetime.utcnow() - timedelta(minutes=14))
        m3 = Message(conversation_id=conv1.id, sender_type="customer", content="ممتاز جداً، ابعتلي عبوة 2 لتر على العنوان: المعادي ش 9 بناء 14", created_at=datetime.utcnow() - timedelta(minutes=5))

        m4 = Message(conversation_id=conv2.id, sender_type="customer", content="لو سمحت الشحنة تأخرت يوم، ممكن متابعة؟ رقم الطلب KS-17280011", created_at=datetime.utcnow() - timedelta(hours=2))
        m5 = Message(conversation_id=conv2.id, sender_type="agent", content="أهلاً د. نورهان، قمت بمراجعة شركة الشحن والشحنة مع المندوب وفي الطريق لحضرتك خلال ساعتين بالكتير. اعتذارنا عن التأخير البسيط! 🚚", created_at=datetime.utcnow() - timedelta(hours=1))

        db.session.add_all([m1, m2, m3, m4, m5])

        # Sample Order
        ord1 = Order(
            order_number="KS-17280011",
            customer_id=c2.id,
            total_amount=515.0,
            payment_method="cash_on_delivery",
            payment_status="paid",
            order_status="shipped",
            shipping_address="مصر الجديدة - القاهرة",
            tracking_number="EG-EXPRESS-998822"
        )
        db.session.add(ord1)

    # 8. Integrations initial status
    if not Integration.query.first():
        int_wa = Integration(provider="whatsapp", name="WhatsApp Business Cloud API", status="connected")
        int_ig = Integration(provider="instagram", name="Instagram Direct Graph API", status="connected")
        int_tg = Integration(provider="telegram", name="Telegram Bot API", status="connected")
        int_tt = Integration(provider="tiktok", name="TikTok Business Messaging API", status="unavailable")
        int_ai = Integration(provider="ai_provider", name="OpenAI / Groq API", status="connected")

        db.session.add_all([int_wa, int_ig, int_tg, int_tt, int_ai])

    db.session.commit()
    print("Khams Sinaa database successfully seeded!")
