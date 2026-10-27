import os
from datetime import datetime, timedelta, timezone
from app.extensions import db
from app.models import (
    User, Customer, CustomerIdentity, Conversation, Message,
    Product, Category, Order, OrderItem, FAQ, KnowledgeBaseArticle,
    QuickReply, Integration, Tag, CompanySettings, StoreSettings, AISettings,
    ServicePackage, ServiceCategory, Lead
)
from app.services.ai_tools import NEXORA_PORTFOLIO_URL, NEXORA_PORTFOLIO_PROJECTS


def seed_database():
    """
    Idempotent seed and migration script for NEXORA Software Solutions.
    Safely creates or updates NEXORA business records without duplicating data.
    """
    env = os.getenv("FLASK_ENV", "development")

    # ==========================================
    # 1. Users & Roles
    # ==========================================
    default_users = [
        {"email": "admin@nexorasolutions.com", "name": "أحمد الشريف", "role": "admin", "status": "online"},
        {"email": "manager@nexorasolutions.com", "name": "سارة محمود", "role": "manager", "status": "online"},
        {"email": "agent1@nexorasolutions.com", "name": "محمد طارق", "role": "agent", "status": "online"},
        {"email": "agent2@nexorasolutions.com", "name": "ريم العبدالله", "role": "agent", "status": "away"}
    ]

    for u_data in default_users:
        user = User.query.filter_by(email=u_data["email"]).first()
        if not user:
            user = User(
                email=u_data["email"],
                name=u_data["name"],
                role=u_data["role"],
                status=u_data["status"]
            )
            # Use environment variable or default secure dev password
            dev_pass = os.getenv("DEV_DEFAULT_PASSWORD", "Nexora#Secure2026")
            user.set_password(dev_pass)
            db.session.add(user)
        else:
            # Update role and name if changed, without resetting existing password
            user.name = u_data["name"]
            user.role = u_data["role"]

    db.session.flush()

    # ==========================================
    # 2. Company & Store Settings
    # ==========================================
    company_set = CompanySettings.query.first()
    if not company_set:
        company_set = CompanySettings()
        db.session.add(company_set)

    company_set.company_name = "NEXORA Software Solutions"
    company_set.tagline = "Ideas → Code → Impact"
    company_set.phone = "+201556441133"
    company_set.whatsapp = "+201556441133"
    company_set.email = "contact@nexorasolutions.com"
    company_set.address = "القاهرة، مصر"
    company_set.portfolio_url = NEXORA_PORTFOLIO_URL
    company_set.facebook_url = "https://www.facebook.com/profile.php?id=61595024167397"
    company_set.instagram_url = "https://www.instagram.com/nexorasoftwarre/"
    company_set.telegram_endpoint = "https://ai-whats-production.up.railway.app/"
    company_set.services_summary = "تطوير المواقع والمنصات، حلول الذكاء الاصطناعي والشات بوت، أتمتة العمليات والربط البرمجي، وتطوير البرمجيات المخصصة."

    # Legacy store settings synchronization
    store_set = StoreSettings.query.first()
    if not store_set:
        store_set = StoreSettings()
        db.session.add(store_set)

    store_set.store_name = "NEXORA Software Solutions"
    store_set.phone = "+201556441133"
    store_set.whatsapp = "+201556441133"
    store_set.email = "contact@nexorasolutions.com"
    store_set.address = "القاهرة، مصر"
    store_set.portfolio_url = NEXORA_PORTFOLIO_URL
    store_set.shipping_policy = "خدمات برمجية ورقمية سحابية تُسلّم وتُنشر عبر الإنترنت."
    store_set.payment_methods = "التحويل البنكي، إنستا باي (InstaPay)، فودافون كاش، وبطاقات الدفع الإلكتروني المعتمدة."
    store_set.return_policy = "ضمان جودة البرمجيات ودعم فني وصيانة وفق اتفاقية مستوى الخدمة المعتمدة."

    # ==========================================
    # 3. AI Settings (No hardcoded credentials)
    # ==========================================
    ai_set = AISettings.query.first()
    if not ai_set:
        ai_set = AISettings()
        db.session.add(ai_set)

    env_ai_key = os.getenv("AI_API_KEY", "") or os.getenv("XAI_API_KEY", "")
    env_ai_model = os.getenv("AI_MODEL", "llama-3.3-70b-versatile")
    env_ai_base = os.getenv("AI_API_BASE_URL", "https://api.groq.com/openai/v1")

    ai_set.provider = "groq" if "groq" in env_ai_base else "openai"
    ai_set.api_key = env_ai_key
    ai_set.api_base_url = env_ai_base
    ai_set.model = env_ai_model
    ai_set.temperature = 0.3
    ai_set.max_tokens = 500
    ai_set.is_enabled = bool(env_ai_key)

    # ==========================================
    # 4. Service Packages (Starter, Business, Enterprise)
    # ==========================================
    packages_data = [
        {
            "slug": "starter",
            "name": "Starter",
            "name_ar": "باقة الانطلاق",
            "description": "مثالية للأفراد والأنشطة الناشئة التي تحتاج حضوراً رقمياً أنيقاً واحترافياً بأعلى سرعة.",
            "target_audience": "الشركات الناشئة، المستقلون، والأنشطة الصغيرة الراغبة في حضور رقمي سريع ومؤثر.",
            "indicative_price_min": 8000.0,
            "indicative_price_max": 12000.0,
            "indicative_price_text": "8,000 – 12,000 ج.م (تقدير استرشادي غير معتمد)",
            "currency": "EGP",
            "is_approved": False,  # Unapproved estimate
            "is_popular": False,
            "is_active": True,
            "support_period": "أسبوعين بعد الإطلاق",
            "features": [
                "صفحة هبوط رئيسية متكاملة وفائقة السرعة",
                "تصميم عصري متوافق 100% مع الهواتف الذكية",
                "ربط مباشر بزر ونموذج استفسارات واتساب",
                "تهيئة أساسية لمحركات البحث (SEO)",
                "مساعدة في ضبط الاستضافة وشهادة الأمان SSL",
                "دعم فني ومتابعة لمدة أسبوعين بعد الإطلاق"
            ]
        },
        {
            "slug": "business",
            "name": "Business",
            "name_ar": "باقة الأعمال",
            "description": "الخيار الأفضل للشركات والعلامات التجارية التي تحتاج موقعاً متكاملاً متعدد الأقسام ومجهزاً لزيادة المبيعات.",
            "target_audience": "الشركات المتوسطة والمتنامية التي تتطلب منصة متعددة الصفحات ومعرض أعمال احترافي.",
            "indicative_price_min": 20000.0,
            "indicative_price_max": 35000.0,
            "indicative_price_text": "20,000 – 35,000 ج.م (تقدير استرشادي غير معتمد)",
            "currency": "EGP",
            "is_approved": False,  # Unapproved estimate
            "is_popular": True,   # Suggested Most Popular
            "is_active": True,
            "support_period": "شهر كامل بعد الإطلاق",
            "features": [
                "موقع متكامل أو تطبيق ويب صغير حتى 5 صفحات مخصصة",
                "لوحة تحكم أو نظام إدارة محتوى مرن",
                "معرض أعمال تفاعلي أو كتالوج خدمات متقدم",
                "دعم لغتين (عربي وإنجليزي)",
                "ربط تحليلات جوجل وبيكسل منصات الإعلانات",
                "تهيئة متقدمة لمحركات البحث وسرعة تحميل قياسية",
                "دعم فني ومتابعة مستمرة لمدة شهر كامل"
            ]
        },
        {
            "slug": "enterprise",
            "name": "Enterprise",
            "name_ar": "الباقة المتقدمة",
            "description": "للأنظمة المخصصة، المنصات الرقمية، والربط البرمجي المعقد والذكاء الاصطناعي.",
            "target_audience": "الشركات والمؤسسات التي تحتاج برمجيات مخصصة، شات بوت ذكي، وأتمتة شاملة.",
            "indicative_price_min": None,
            "indicative_price_max": None,
            "indicative_price_text": "عرض سعر مخصص (Custom Quotation)",
            "currency": "EGP",
            "is_approved": False,
            "is_popular": False,
            "is_active": True,
            "support_period": "خطة صيانة ودعم مستمرة وفق الاتفاقية",
            "features": [
                "معمارية وتطوير منصة برمجية مخصصة بالكامل",
                "دمج شات بوت وحلول الذكاء الاصطناعي (AI Assistant / Agents)",
                "واجهات برمجية خلفية REST APIs وقواعد بيانات متقدمة",
                "أتمتة العمليات وربط Webhooks وأنظمة الـ CRM وبوابات الدفع",
                "أعلى معايير الأمان والتوسع والتحمل العالي (Scalability & Security)",
                "خطة دعم فني وتطوير دوري مستمر حسب العقد"
            ]
        }
    ]

    for p_info in packages_data:
        pkg = ServicePackage.query.filter_by(slug=p_info["slug"]).first()
        if not pkg:
            pkg = ServicePackage(slug=p_info["slug"])
            db.session.add(pkg)

        pkg.name = p_info["name"]
        pkg.name_ar = p_info["name_ar"]
        pkg.description = p_info["description"]
        pkg.target_audience = p_info["target_audience"]
        pkg.indicative_price_min = p_info["indicative_price_min"]
        pkg.indicative_price_max = p_info["indicative_price_max"]
        pkg.indicative_price_text = p_info["indicative_price_text"]
        pkg.currency = p_info["currency"]
        pkg.is_approved = p_info["is_approved"]
        pkg.is_popular = p_info["is_popular"]
        pkg.is_active = p_info["is_active"]
        pkg.support_period = p_info["support_period"]
        pkg.features = p_info["features"]

    # ==========================================
    # 4.1 Black and White Creative Service Categories
    # ==========================================
    categories_data = [
        {
            "slug": "graphic-design",
            "name": "Graphic Design",
            "name_ar": "تصميم الجرافيك",
            "description": "تصميم الهويات البصرية والشعارات، المطبوعات، تصاميم منصات التواصل، والتغليف الإبداعي.",
            "icon": "palette",
            "sort_order": 1
        },
        {
            "slug": "advertising-marketing",
            "name": "Advertising and Marketing",
            "name_ar": "الدعاية والتسويق",
            "description": "تخطيط وتصميم الحملات الإعلانية، التسويق عبر وسائل التواصل الاجتماعي، والمواد الدعائية.",
            "icon": "megaphone",
            "sort_order": 2
        },
        {
            "slug": "interior-decoration",
            "name": "Interior Decoration",
            "name_ar": "الديكور والتصميم الداخلي",
            "description": "التصميم الداخلي السكني والتجاري، النمذجة ثلاثية الأبعاد 3D والإظهار المعماري وتوزيع المساحات.",
            "icon": "home",
            "sort_order": 3
        }
    ]

    for cat_data in categories_data:
        cat = ServiceCategory.query.filter_by(slug=cat_data["slug"]).first()
        if not cat:
            cat = ServiceCategory(slug=cat_data["slug"])
            db.session.add(cat)
        cat.name = cat_data["name"]
        cat.name_ar = cat_data["name_ar"]
        cat.description = cat_data["description"]
        cat.icon = cat_data["icon"]
        cat.sort_order = cat_data["sort_order"]
        cat.is_active = True

    db.session.flush()

    # Deactivate any legacy physical products so they are excluded from active queries

    old_products = Product.query.filter(
        Product.sku.ilike("KS-%") |
        Product.name.ilike("%زيت%") |
        Product.name.ilike("%عسل%") |
        Product.name.ilike("%مرمية%")
    ).all()
    for op in old_products:
        op.is_active = False

    # ==========================================
    # 5. Quick Replies for NEXORA Software
    # ==========================================
    quick_replies_data = [
        {
            "shortcut": "/hello",
            "title": "ترحيب بالعميل",
            "category": "welcome",
            "response_text": "أهلاً بك في NEXORA Software Solutions 💻✨! يسعدنا مساعدتك في تطوير المواقع والمنصات، حلول الذكاء الاصطناعي، وأتمتة العمليات."
        },
        {
            "shortcut": "/services",
            "title": "خدماتنا البرمجية",
            "category": "services",
            "response_text": "نقدم في NEXORA خدمات تقنية متكاملة:\n1. تطوير المواقع والمنصات (Web Development)\n2. حلول الذكاء الاصطناعي والشات بوت (AI Solutions)\n3. أتمتة العمليات والربط البرمجي (Workflow Automation)\n4. تطوير البرمجيات المخصصة (Custom Software)\n5. حلول نمو الأعمال والتسويق الرقمي."
        },
        {
            "shortcut": "/portfolio",
            "title": "معرض الأعمال والبورتفوليو",
            "category": "portfolio",
            "response_text": f"طبعًا، تقدر تتفرج على بورتفوليو NEXORA وتشوف نماذج المشاريع والأعمال المعروضة عندنا من هنا:\n{NEXORA_PORTFOLIO_URL}\nولو مهتم بنوع معين من المشاريع زي المواقع أو حلول الذكاء الاصطناعي أو الأتمتة، قولي وأنا أساعدك."
        },
        {
            "shortcut": "/packages",
            "title": "شرح الباقات الثلاث",
            "category": "packages",
            "response_text": "نوفر 3 باقات مرنة لتناسب حجم ونمو مشروعك:\n• باقة الانطلاق (Starter): صفحة هبوط سريعة متوافقة مع الموبايل (تقدير استرشادي: 8,000 - 12,000 ج.م)\n• باقة الأعمال (Business - الأكثر طلباً): موقع متكامل حتى 5 صفحات ودعم لغتين (تقدير استرشادي: 20,000 - 35,000 ج.م)\n• الباقة المتقدمة (Enterprise): أنظمة مخصصة وشات بوت وأتمتة متقدمة (عرض سعر مخصص).\n* الأسعار استرشادية والعرض النهائي يتحدد بعد مراجعة المتطلبات."
        },
        {
            "shortcut": "/pricing",
            "title": "استفسار الأسعار والتكلفة",
            "category": "pricing",
            "response_text": "تكلفة المشروع تتحدد بدقة بناءً على الميزات ونطاق العمل المطلوب. الباقات الاسترشادية تبدأ من 8,000 ج.م لصفحة الهبوط (Starter) و20,000 ج.م للمواقع المتكاملة (Business)، والمشاريع المخصصة تُقدّم لها عروض أسعار تفصيلية بعد دراسة المتطلبات."
        },
        {
            "shortcut": "/requirements",
            "title": "جمع متطلبات المشروع",
            "category": "requirements",
            "response_text": "لمساعدتك في اختيار الحل الأنسب وتقديم عرض سعر دقيق، ممكن تشاركنا:\n1. طبيعة نشاطك أو مجالك التجاري\n2. الخدمة المطلوبة (موقع، شات بوت، أتمتة، نظام مخصص)\n3. الميزانية التقديرية المتاحة\n4. موعد الإطلاق المتوقع."
        },
        {
            "shortcut": "/ai_chatbot",
            "title": "شات بوت الذكاء الاصطناعي",
            "category": "ai",
            "response_text": "نطوّر شات بوت ذكي مخصص لمنصتك أو لواتساب، يقوم بالرد التلقائي الفوري، وجمع بيانات العملاء المؤهلين، وتحويل الاستفسارات المعقدة للدعم البشري بكل سلاسة."
        },
        {
            "shortcut": "/automation",
            "title": "أتمتة العمليات والربط",
            "category": "automation",
            "response_text": "نساعدك في ربط وتكامل أنظمة العمل مثل واتساب، Google Sheets، برامج الـ CRM، ومحركات n8n لتقليل المهام اليدوية المتكررة وتسريع الاستجابة للعملاء."
        },
        {
            "shortcut": "/lead",
            "title": "تأكيد تسجيل طلب العميل",
            "category": "lead",
            "response_text": "تم تسجيل بيانات ومتطلبات مشروعك بنجاح ✅! سيقوم أحد مهندسي واستشاريي NEXORA بالتواصل معك عبر الهاتف أو واتساب لمناقشة التفاصيل والخطوات التالية."
        },
        {
            "shortcut": "/human",
            "title": "تحويل لممثل خدمة العملاء",
            "category": "customer_service",
            "response_text": "أكيد، سيتم تحويل محادثتك الآن لأحد مسؤولي خدمة عملاء ودعم NEXORA لمتابعة استفسارك هاتفياً أو عبر الشات بالتفصيل."
        },
        {
            "shortcut": "/closing",
            "title": "إنهاء ومتابعة المحادثة",
            "category": "closing",
            "response_text": "سعداء جداً بتواصلك مع NEXORA Software Solutions! يمكنك دائماً زيارة بورتفوليو أعمالنا عبر https://company-pi-two.vercel.app/ أو مراسلتنا في أي وقت. يومك سعيد! 🚀"
        }
    ]

    # Deactivate or remove old oil/physical quick replies
    old_qr_shortcuts = ["/payment", "/order", "/shipping"]
    for o_sc in old_qr_shortcuts:
        old_q = QuickReply.query.filter_by(shortcut=o_sc).first()
        if old_q:
            old_q.is_enabled = False

    for qr_data in quick_replies_data:
        qr = QuickReply.query.filter_by(shortcut=qr_data["shortcut"]).first()
        if not qr:
            qr = QuickReply(shortcut=qr_data["shortcut"])
            db.session.add(qr)
        qr.title = qr_data["title"]
        qr.category = qr_data["category"]
        qr.response_text = qr_data["response_text"]
        qr.is_enabled = True

    # ==========================================
    # 6. FAQs for NEXORA Software
    # ==========================================
    faqs_data = [
        {
            "question": "ما هي الخدمات البرمجية التي تقدمها شركة NEXORA؟",
            "answer": "تقدم NEXORA خدمات تطوير المواقع والمنصات الرقمية، حلول الذكاء الاصطناعي والشات بوت الذكي، أتمتة العمليات والربط البرمجي (Workflow Automation)، وتطوير البرمجيات وأنظمة الويب المخصصة.",
            "category": "الخدمات"
        },
        {
            "question": "كم تكلفة تصميم وتطوير موقع إلكتروني؟",
            "answer": "تعتمد التكلفة على متطلبات وحجم الموقع. لدينا باقات استرشادية مقترحة: باقة Starter لصفحة الهبوط الواحدة (8,000 - 12,000 ج.م استرشادي)، وباقة Business للمواقع المتكاملة حتى 5 صفحات (20,000 - 35,000 ج.م استرشادي)، والأنظمة المعقدة تُقدّم لها عروض أسعار مخصصة. الأسعار النهائية تتحدد بعد مراجعة المتطلبات بدقة.",
            "category": "الأسعار والباقات"
        },
        {
            "question": "هل تقدمون خدمات شات بوت وحلول ذكاء اصطناعي؟",
            "answer": "نعم، نطور شات بوت ذكي متكامل للمواقع وتطبيقات الويب وواتساب، يعتمد على تقنيات النماذج اللغوية (LLM) وقواعد المعرفة (RAG) لأتمتة الردود على استفسارات العملاء وجمع بيانات العملاء المهتمين.",
            "category": "الذكاء الاصطناعي"
        },
        {
            "question": "أين يمكنني رؤية سابقة أعمال ومشاريع NEXORA؟",
            "answer": f"يمكنك تصفح معرض أعمالنا ومشاريعنا المعروضة عبر الرابط الرسمي للبورتفوليو: {NEXORA_PORTFOLIO_URL}",
            "category": "سابقة الأعمال"
        },
        {
            "question": "ما الفرق بين باقة Starter وباقة Business؟",
            "answer": "باقة Starter تركز على صفحة هبوط واحدة سريعة جداً للمشاريع الناشئة مع نموذج واتساب ودعم أسبوعين، بينما باقة Business تقدم موقعاً متكاملاً حتى 5 صفحات مع دعم لغتين عربي وإنجليزي ومعرض أعمال وربط تحليلات متقدمة ودعم فني لمدة شهر كامل.",
            "category": "الأسعار والباقات"
        },
        {
            "question": "هل المواقع التي تطورها NEXORA متوافقة مع الهواتف الذكية وسريعة؟",
            "answer": "نعم 100%، جميع مشاريعنا مبنية وفق معيار Mobile-First responsive وتستخدم أحدث التقنيات مثل Next.js و React لضمان سرعة تحميل فائقة وتجربة مستخدم استثنائية مع تهيئة كاملة لمحركات البحث (SEO).",
            "category": "التطوير والتقنية"
        },
        {
            "question": "هل تقدمون مساعدة في حجز النطاق (Domain) والاستضافة (Hosting)؟",
            "answer": "نعم، نساعد عملاءنا في اختيار وضبط الدومين، وربط السيرفرات السحابية الموثوقة، وتفعيل شهادات الأمان SSL مجاناً.",
            "category": "الدعم والاستضافة"
        },
        {
            "question": "هل يتوفر دعم فني بعد إطلاق المشروع؟",
            "answer": "بالتأكيد، تتضمن جميع باقاتنا فترة دعم فني ومتابعة مجانية بعد الإطلاق (أسبوعين لباقة Starter، وشهر لباقة Business، وخطة دعم وصيانة مستمرة للباقة المتقدمة Enterprise).",
            "category": "الدعم الفني"
        }
    ]

    # Deactivate old physical-product FAQs
    old_faqs = FAQ.query.filter(
        FAQ.question.ilike("%زيت%") |
        FAQ.question.ilike("%شحن%") |
        FAQ.answer.ilike("%زيت الزيتون%") |
        FAQ.answer.ilike("%خام سينا%")
    ).all()
    for of in old_faqs:
        of.is_active = False

    for f_info in faqs_data:
        faq = FAQ.query.filter_by(question=f_info["question"]).first()
        if not faq:
            faq = FAQ(question=f_info["question"], answer=f_info["answer"], category=f_info["category"])
            db.session.add(faq)
        else:
            faq.answer = f_info["answer"]
            faq.category = f_info["category"]
            faq.is_active = True

    # ==========================================
    # 7. Tags for Software Customer Service
    # ==========================================
    tags_data = [
        {"name": "تطوير مواقع (Web Dev)", "color": "#1E6BFF"},
        {"name": "حلول الذكاء الاصطناعي (AI)", "color": "#00C8FF"},
        {"name": "أتمتة العمليات (Automation)", "color": "#8B5CF6"},
        {"name": "طلب مشروع جديد (New Lead)", "color": "#10B981"},
        {"name": "استفسار أسعار (Pricing)", "color": "#F59E0B"},
        {"name": "استفسار بورتفوليو (Portfolio)", "color": "#3B82F6"},
        {"name": "تحويل لموظف (Human Handoff)", "color": "#EF4444"},
        {"name": "دعم فني (Tech Support)", "color": "#6366F1"}
    ]

    for t_info in tags_data:
        t = Tag.query.filter_by(name=t_info["name"]).first()
        if not t:
            t = Tag(name=t_info["name"], color=t_info["color"])
            db.session.add(t)
        else:
            t.color = t_info["color"]

    # ==========================================
    # 8. Integrations Truthful Status
    # ==========================================
    wa_token = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    ig_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    ai_key = os.getenv("AI_API_KEY", "")

    integrations_data = [
        {
            "provider": "whatsapp",
            "name": "WhatsApp Business Cloud API",
            "status": "connected" if wa_token and not wa_token.startswith("your_") else "pending_setup"
        },
        {
            "provider": "instagram",
            "name": "Instagram Direct Graph API",
            "status": "connected" if ig_token and not ig_token.startswith("your_") else "pending_setup"
        },
        {
            "provider": "telegram",
            "name": "Telegram Bot API",
            "status": "connected" if tg_token and not tg_token.startswith("your_") else "pending_setup"
        },
        {
            "provider": "ai_provider",
            "name": "OpenAI / Groq API",
            "status": "connected" if ai_key and not ai_key.startswith("your_") else "pending_setup"
        },
        {
            "provider": "tiktok",
            "name": "TikTok Business Messaging API",
            "status": "unavailable"  # Truthful status: API not enabled/available
        }
    ]

    for i_data in integrations_data:
        integ = Integration.query.filter_by(provider=i_data["provider"]).first()
        if not integ:
            integ = Integration(
                provider=i_data["provider"],
                name=i_data["name"],
                status=i_data["status"]
            )
            db.session.add(integ)
        else:
            integ.name = i_data["name"]
            integ.status = i_data["status"]

    # ==========================================
    # 9. Clean Demo Conversations & Leads (Development Only)
    # ==========================================
    # Remove old olive oil demo customer records if they exist
    old_demo_customers = Customer.query.filter(
        Customer.phone.in_(["+201011223344", "+201144556677", "+201277889900", "+201500112233"]) |
        Customer.email.in_(["amr@gmail.com", "nourhan@yahoo.com"])
    ).all()
    for odc in old_demo_customers:
        # Delete related conversations and messages
        for c in odc.conversations:
            Message.query.filter_by(conversation_id=c.id).delete()
            db.session.delete(c)
        # Delete related old demo orders
        Order.query.filter_by(customer_id=odc.id).delete()
        CustomerIdentity.query.filter_by(customer_id=odc.id).delete()
        db.session.delete(odc)

    # Insert realistic NEXORA demo client in development if no conversations exist
    if not Conversation.query.first():
        demo_client = Customer(
            name="م. طارق كمال (شركة الأفق للاستثمار العقاري)",
            phone="+201099887766",
            email="tarek@alofok-estates.com",
            notes="عميل مهتم بتطوير موقع تعريفي للشركة مع شات بوت واتساب للرد على استفسارات المشروعات."
        )
        db.session.add(demo_client)
        db.session.flush()

        ident = CustomerIdentity(
            customer_id=demo_client.id,
            platform="whatsapp",
            platform_user_id="+201099887766",
            username="tarek_alofok"
        )
        db.session.add(ident)
        db.session.flush()

        conv = Conversation(
            customer_id=demo_client.id,
            platform="whatsapp",
            platform_conversation_id="+201099887766",
            conversation_status="open",
            ai_status="active",
            priority="medium",
            unread_count=0
        )
        db.session.add(conv)
        db.session.flush()

        m1 = Message(
            conversation_id=conv.id,
            sender_type="customer",
            content="السلام عليكم، محتاجين نطور موقع للشركة العقارية وشات بوت يرد على العملاء على واتساب.",
            created_at=datetime.now(timezone.utc) - timedelta(minutes=10)
        )
        m2 = Message(
            conversation_id=conv.id,
            sender_type="ai",
            content="وعليكم السلام ورحمة الله وبركاته يا باشمهندس طارق! أهلاً بك في NEXORA Software Solutions. نقدر نساعدك في تطوير موقع راقي يعرض مشروعاتكم ووحداتكم، مع شات بوت ذكي يساعد في الرد على استفسارات العملاء وجمع بيانات المهتمين. ممكن أعرف هل محتاج موقع تعريفي فقط، ولا كمان لوحة تحكم لإدارة المشروعات والعملاء؟",
            created_at=datetime.now(timezone.utc) - timedelta(minutes=9)
        )
        db.session.add_all([m1, m2])

        # Demo project lead
        lead1 = Lead(
            customer_id=demo_client.id,
            customer_name=demo_client.name,
            contact_info=demo_client.phone,
            business_name="شركة الأفق للاستثمار العقاري",
            industry="عقارات وتطوير عقاري",
            requested_service="موقع إلكتروني + شات بوت ذكي",
            package_interest="Business",
            project_description="موقع متعدد الأقسام مع شات بوت واتساب مؤهل للرد على استفسارات المشروعات وجمع بيانات العملاء.",
            budget="20,000 - 35,000 ج.م",
            expected_timeline="شهر واحد",
            lead_source="whatsapp",
            status="Qualified"
        )
        db.session.add(lead1)

    db.session.commit()
    print("NEXORA Software Solutions database successfully seeded and updated!")
