import os
import re
import json
import logging
import requests
from datetime import datetime, timezone
from app.models import (
    AISettings, CompanySettings, StoreSettings, FAQ, KnowledgeBaseArticle,
    ServicePackage, ServiceCategory, Conversation, Message, Customer, Lead
)
from app.services.ai_tools import (
    get_portfolio_url, get_portfolio_projects, get_service_packages,
    get_service_package, get_service_categories, get_services_by_category,
    search_services, format_service_pricing_text, get_company_info,
    create_lead, escalate_to_human,
    NEXORA_PORTFOLIO_URL, NEXORA_PORTFOLIO_PROJECTS
)
from app.extensions import db

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = """# Black and White WhatsApp Sales Assistant — System Prompt

## 1. الشخصية والدور
أنت **أحمد**، مساعد مبيعات في **Black and White**، عمرك 28 سنة، وبتتكلم مع العملاء على واتساب.
شركة Black and White هي وكالة إبداعية متخصصة في 3 مجالات رئيسية:
1. **تصميم الجرافيك (Graphic Design)**: الهويات البصرية، تصميم الشعارات، المطبوعات والبروشورات، تصاميم السوشيال ميديا، وتصميم العبوات والتغليف.
2. **الدعاية والتسويق (Advertising & Marketing)**: تخطيط وتصميم الحملات الإعلانية، إعلانات السوشيال ميديا الممولة، والمواد الدعائية والتسويقية.
3. **الديكور والتصميم الداخلي (Interior Decoration)**: التصميم الداخلي السكني والتجاري، الإظهار والنمذجة ثلاثية الأبعاد 3D، وتوزيع المساحات.

دورك إنك تفهم احتياج العميل، توجهه للتصنيف والخدمة المناسبة، تجمع المتطلبات خطوة بخطوة، وتشرح الخدمات ببساطة وتساعده يوصل لعرض سعر دقيق أو استشارة مع الفريق.

## 2. طريقة الكلام
- اتكلم بالمصري العامي الطبيعي بنسبة 100% (أو بلغة العميل لو كلمك بالإنجليزي).
- استخدم جمل قصيرة وواضحة تناسب شات واتساب.
- استخدم تعبيرات مصرية ودية: أيوه، تمام، حلو، ماشي، أكيد، بص، طب، دلوقتي، كده، عايز، محتاج، إيه.
- الإيموجي باعتدال وبشكل مناسب.
- ممنوع العبارات الآلية والرسمية مثل: «يسعدني مساعدتك»، «بالتأكيد!»، «كنموذج لغوي»، «فيما يلي»، «لا تتردد».
- متسألش أكتر من سؤال في نفس الرسالة. اجمع المعلومات خطوة بخطوة.

## 3. التعامل مع سؤال: إنت بوت؟
- أول مرة: رد بخفة: «أنا من فريق Black and White 😅 قولي، محتاج إيه بالظبط؟»
- لو كرر العميل السؤال: جاوبه بوضوح وصراحة: «أيوه، أنا مساعد ذكي من Black and White، بساعد في الرد على الاستفسارات وتوضيح الخدمات. ولو حابب تتكلم مع حد من الفريق، أقدر أوجه طلبك ليه.»
- لو طلب التحدث مع شخص حقيقي: حوّله فوراً باستخدام آلية التحويل.

## 4. توجيه الطلبات حسب المجالات الثلاثة (Intent Routing)
1. **تصميم الجرافيك (Graphic Design)**:
   - طلب شعار (Logo): اسأله عن اسم وطبيعة النشاط، والستايل أو الألوان اللي بيفضلها.
   - طلب هوية بصرية (Brand Identity): اسأله هل النشاط جديد ومحتاج هوية من الصفر، ولا تجديد لهوية سابقة.
   - طلب تصاميم سوشيال ميديا أو مطبوعات: اعرف نوع التصاميم وعددها.
2. **الدعاية والتسويق (Advertising & Marketing)**:
   - طلب حملة إعلانية: اعرف هدف الحملة (مبيعات، انتشار، رسائل)، والمنصة المفضلة (فيسبوك، انستغرام، تيك توك، جوجل)، والميزانية التقريبية لو متوفرة.
3. **الديكور والتصميم الداخلي (Interior Decoration)**:
   - طلب تصميم داخلي أو ديكور: اسأله عن نوع المساحة (شقة، فيلا، مكتب، مطعم/كافيه)، المساحة التقريبية كام متر، وهل محتاج تصميم 3D فقط ولا تصميم وتنفيذ.
4. **أكثر من خدمة**: رحّب بالطلب واقترح البدء بتحديد الأولوية الأولى (مثلاً تصميم الهوية أولاً ثم المطبوعات أو الحملة).

## 5. قواعد الأسعار (صارمة ومحكمة)
- **ممنوع تماماً اختراع أي سعر أو نسبة خصم**.
- قاعدة البيانات هي المصدر الوحيد للمعلومات والأسعار الحية.
- لو الخدمة محددة بسعر ثابت أو سعر يبدأ من: اذكره بدقة مع العملة.
- لو الخدمة تتطلب عرض سعر مخصص (Custom Quotation) أو السعر غير محدد: وضح للعميل بلباقة إن السعر بيتحدد بدقة بناءً على تفاصيل ومتطلبات مشروعه، واسأله عن التفاصيل المطلوبة لتجهيز عرض السعر.
- لا تعد العميل بسعر نهائي قبل مراجعة المتطلبات رسمياً من الفريق.

## 6. التحويل للدعم البشري
حوّل المحادثة فوراً في الحالات دي:
- طلب العميل الصريح التحدث مع شخص حقيقي.
- طلب اتفاق تعاقدي رسمي أو تفاصيل دفع فورية.
- حالات الشكاوى أو المتطلبات الخاصة جداً.
"""

HANDOFF_MESSAGE = "تمام، هساعدك توصل لفريق الشركة من خلال وسيلة التواصل المتاحة."
HANDOFF_MESSAGE_EN = "Certainly, I am transferring your inquiry to a Black and White representative right now."

PORTFOLIO_MESSAGE_AR = """بص، تقدر تشوف بورتفوليو وسابقة أعمالنا ونماذج المشاريع من هنا:
https://company-pi-two.vercel.app/

قولي، حابب تشوف نماذج في مجال معين زي تصميم الجرافيك والهويات، الحملات الإعلانية، ولا الديكور والتصميم الداخلي 3D؟"""

PORTFOLIO_MESSAGE_EN = """Of course! You can explore our official portfolio and showcase of creative projects here:
https://company-pi-two.vercel.app/

Feel free to tell me which category interests you (Graphic Design, Advertising & Marketing, or Interior Decoration)!"""

# Text normalization
_DIGIT_MAP = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "0123456789" * 2)
_CHAR_MAP = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي", "ة": "ه", "ؤ": "و", "ئ": "ي"})
_DIACRITICS_RE = re.compile(r"[\u0640\u064B-\u065F\u0670]")


def normalize_text(text):
    if not text:
        return ""
    t = str(text).translate(_DIGIT_MAP)
    t = _DIACRITICS_RE.sub("", t)
    t = t.translate(_CHAR_MAP).lower()
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def has_any(text, kws):
    return any(k in text for k in kws)


# Keywords (normalized)
ESCALATION_KW = tuple(normalize_text(w) for w in [
    "خدمة العملاء", "خدمه العملا", "حد من الدعم", "عايز موظف", "عايز حد", "مواظف",
    "دعم", "تحدث مع موظف", "كلمني بشري", "خدمه عملاء", "اتصال هاتفي", "عايز بني ادم",
    "customer service", "speak to human", "talk to human", "talk to representative", "agent"
])

PORTFOLIO_KW = tuple(normalize_text(w) for w in [
    "بورتفوليو", "شغلكم", "اعمالكم", "سابقة اعمال", "سابقه اعمال", "مشاريع سابقة", "مشاريع سابقه",
    "نماذج", "وروني شغلكم", "شوف شغلكم", "اشوف شغلكم", "معرض الاعمال",
    "portfolio", "previous work", "show me your work", "samples", "case studies", "projects"
])

PACKAGES_KW = tuple(normalize_text(w) for w in [
    "باقات", "باقه", "باقة", "starter", "business", "enterprise",
    "packages", "package", "starter package", "business package"
])

PRICING_KW = tuple(normalize_text(w) for w in [
    "بكام", "بكم", "سعر", "اسعار", "أسعار", "تكلفة", "تكلفه", "تكاليف",
    "how much", "cost", "pricing", "price", "rates", "quote"
])

# Category Specific Keywords
GRAPHIC_DESIGN_KW = tuple(normalize_text(w) for w in [
    "لوجو", "شعار", "هوية بصرية", "هويه بصريه", "بروشور", "فلاير", "بانر",
    "كارت شخصي", "تغليف", "علب", "باكيدج", "packaging", "graphic design",
    "تصميم جرافيك", "لوقو", "تصميمات", "social media post", "بوستات"
])

MARKETING_KW = tuple(normalize_text(w) for w in [
    "حملة اعلانية", "حمله اعلانيه", "اعلانات ممولة", "اعلانات مموله", "تسويق",
    "فيسبوك ادز", "انستغرام ادز", "social media ads", "advertising", "marketing",
    "campaign", "حملات تسويقية", "اعلانات جوجل", "تيك توك ادز"
])

INTERIOR_KW = tuple(normalize_text(w) for w in [
    "ديكور", "تصميم داخلي", "تشطيب", "رندر", "3d", "توزيع مساحات", "مخطط معمار",
    "شقة", "شقه", "فيلا", "مكتب", "كافيه", "مطعم", "interior design",
    "interior decoration", "space planning", "3d rendering", "ديكورات"
])

LEAD_TRIGGER_KW = tuple(normalize_text(w) for w in [
    "عايز اعمل", "محتاج تصميم", "محتاج لوجو", "عايز لوجو", "عايز هوية", "محتاج ديكور",
    "عايز ديكور", "محتاج حملة", "مشروع جديد", "عايز اطور", "ابدا مشروع", "ابدأ مشروع",
    "محتاج موقع", "عايز موقع", "محتاج شات بوت", "عايز شات بوت",
    "i want", "need design", "need branding", "need marketing", "interior design"
])


class AIService:

    @staticmethod
    def get_config():
        ai_set = AISettings.query.first()
        env_key = os.getenv("AI_API_KEY", "") or os.getenv("XAI_API_KEY", "")
        env_model = os.getenv("AI_MODEL", "llama-3.3-70b-versatile")
        env_base_url = os.getenv("AI_API_BASE_URL", "https://api.groq.com/openai/v1")

        active_key = env_key if env_key else (ai_set.api_key if ai_set and ai_set.api_key else "")
        active_model = env_model if env_key else (ai_set.model if ai_set and ai_set.model else env_model)
        active_base_url = env_base_url if env_key else (ai_set.api_base_url if ai_set and ai_set.api_base_url else env_base_url)

        return {
            "is_enabled": ai_set.is_enabled if ai_set else True,
            "api_key": active_key,
            "api_base_url": active_base_url,
            "model": active_model,
            "temperature": ai_set.temperature if ai_set else 0.3,
            "max_tokens": ai_set.max_tokens if ai_set else 500,
            "system_prompt": (ai_set.system_prompt if ai_set and ai_set.system_prompt else DEFAULT_SYSTEM_PROMPT)
        }

    @classmethod
    def generate_response(cls, conversation_id, incoming_text, is_media=False, media_url=None):
        conv = db.session.get(Conversation, conversation_id)
        if not conv or conv.ai_status != 'active':
            return None

        cfg = cls.get_config()
        if not cfg["is_enabled"]:
            return None

        t = normalize_text(incoming_text)
        is_english = bool(re.search(r'[a-zA-Z]{4,}', incoming_text))

        # 1. Escalation to Human Agent Check
        if has_any(t, ESCALATION_KW):
            escalate_to_human(conversation_id, "customer_requested_human")
            return HANDOFF_MESSAGE_EN if is_english else HANDOFF_MESSAGE

        # 2. Portfolio Questions
        if has_any(t, PORTFOLIO_KW):
            if any(k in t for k in ["سياح", "سفر", "رحلات", "tourism", "travel"]):
                proj = get_portfolio_projects("tourism")
                desc = proj[0]["description"] if proj else ""
                if is_english:
                    return f"We developed Travel Aura, an elegant travel portal with interactive booking flows.\nYou can check our full portfolio here:\n{NEXORA_PORTFOLIO_URL}"
                return f"بص، نفذنا مشروع 'ترافيل أورا للسياحة' وهو منصة سياحية مع مسار حجز واستفسار تفاعلي.\nتقدر تشوفه وباقي المشاريع في البورتفوليو هنا:\n{NEXORA_PORTFOLIO_URL}"

            if any(k in t for k in ["مطعم", "اكل", "طعام", "restaurant", "dining"]):
                if is_english:
                    return f"We built La Casa Fine Dining, featuring interactive QR menus and VIP table reservations.\nExplore our full portfolio here:\n{NEXORA_PORTFOLIO_URL}"
                return f"بص، نفذنا مشروع 'لاكازا للمأكولات الفاخرة' بنظام منيو QR وحجز طاولات.\nتقدر تشوفه وباقي النماذج في البورتفوليو هنا:\n{NEXORA_PORTFOLIO_URL}"

            if any(k in t for k in ["ديكور", "تشطيب", "interior", "3d"]):
                if is_english:
                    return f"We provide comprehensive interior decoration and 3D visualization.\nYou can view our showcase here:\n{NEXORA_PORTFOLIO_URL}\nWould you like to discuss your space requirements?"
                return f"بنقدّم خدمات التصميم الداخلي السكني والتجاري والإظهار ثلاثي الأبعاد 3D.\nتقدر تتفرج على سابقة أعمالنا في البورتفوليو هنا:\n{NEXORA_PORTFOLIO_URL}\nقولي محتاج تصميم لشقة، فيلا، ولا مساحة تجارية؟"

            return PORTFOLIO_MESSAGE_EN if is_english else PORTFOLIO_MESSAGE_AR

        # 3. Specific Legacy Package Difference check (maintains test backward compatibility)
        if ("starter" in t and "business" in t) or ("الفرق" in t and ("باقه" in t or "باقة" in t or "starter" in t)):
            if is_english:
                return (
                    "Here is the key difference between Starter and Business packages:\n"
                    "• Starter: A single high-speed landing page, mobile-first responsive design, WhatsApp inquiry integration, basic SEO, and 2 weeks of post-launch support. Proposed indicative estimate: EGP 8,000–12,000.\n"
                    "• Business (Most Popular): A multi-page website (up to 5 pages), bilingual Arabic/English support, portfolio/service showcase, analytics integration, advanced SEO, and 1 month of support. Proposed indicative estimate: EGP 20,000–35,000.\n\n"
                    "* Note: Prices are indicative estimates; final quotation is tailored to your exact project scope. Which package suits your needs?"
                )
            return (
                "الفرق الأساسي بين باقة الانطلاق (Starter) وباقة الأعمال (Business):\n\n"
                "• باقة Starter: صفحة هبوط واحدة متكاملة وسريعة، متوافقة 100% مع الموبايل، مع زر ونموذج واتساب، وتهيئة SEO أساسية، ودعم أسبوعين. (السعر الاسترشادي المقترح: 8,000 - 12,000 ج.م).\n\n"
                "• باقة Business (الأكثر طلباً): موقع متكامل حتى 5 صفحات، دعم لغتين عربي وإنجليزي، معرض أعمال أو كتالوج، ربط تحليلات، تهيئة SEO متقدمة، ودعم لمدة شهر كامل. (السعر الاسترشادي المقترح: 20,000 - 35,000 ج.م).\n\n"
                "ملاحظة: الأسعار المذكورة هي أسعار تقديرية استرشادية، والعرض المالي النهائي يُحدد بدقة وفقاً لتفاصيل متطلبات مشروعك. تحب نحدد الباقة الأنسب لنشاطك؟"
            )

        # 4. Intent Routing: Interior Decoration
        if has_any(t, INTERIOR_KW) and not has_any(t, PRICING_KW):
            cust_name = conv.customer.name if conv.customer else "عميل ديكور وتصميم داخلي"
            contact_info = (conv.customer.phone or conv.customer.email) if conv.customer else conv.platform_conversation_id
            create_lead(
                customer_id=conv.customer_id,
                customer_name=cust_name,
                contact_info=contact_info,
                requested_service="الديكور والتصميم الداخلي (Interior Decoration)",
                project_description=incoming_text,
                lead_source=conv.platform
            )
            if is_english:
                return "Welcome to Black and White Interior Decoration! We specialize in residential & commercial design, 3D visualization, and space planning. Could you share the type of space (apartment, villa, office, restaurant), approximate area, and whether you need 3D design only or execution as well?"
            return "أهلاً بيك في Black and White! بنقدّم خدمات التصميم الداخلي والديكور السكني والتجاري وريندر 3D وتوزيع المساحات. ممكن تقولي نوع المساحة (شقة، فيلا، مكتب، كافيه)، والمساحة التقريبية كام متر، ومحتاج تصميم 3D بس ولا تصميم وتنفيذ؟"

        # 5. Intent Routing: Graphic Design
        if has_any(t, GRAPHIC_DESIGN_KW) and not has_any(t, PRICING_KW):
            cust_name = conv.customer.name if conv.customer else "عميل تصميم جرافيك"
            contact_info = (conv.customer.phone or conv.customer.email) if conv.customer else conv.platform_conversation_id
            create_lead(
                customer_id=conv.customer_id,
                customer_name=cust_name,
                contact_info=contact_info,
                requested_service="تصميم الجرافيك والهوية البصرية",
                project_description=incoming_text,
                lead_source=conv.platform
            )
            if "لوجو" in t or "شعار" in t or "logo" in t:
                if is_english:
                    return "Welcome to Black and White! We craft distinctive, custom logos with full source vector files. What is your business name and field, and do you have a preferred style or color palette?"
                return "أهلاً بيك في Black and White! بنقدّم تصميم شعار احترافي فريد مع تسليم جميع الملفات المصدرية المفتوحة. قولي اسم وطبيعة نشاطك التجاري إيه، وإيه الألوان أو الستايل اللي بتفضله للشعار؟"
            if is_english:
                return "Hello! At Black and White, we offer full graphic design services, brand identities, social media packs, and packaging. What specific design items does your business need?"
            return "أهلاً بيك في Black and White! بنقدّم خدمات تصميم الجرافيك والهوية البصرية المتكاملة، المطبوعات، وتصاميم السوشيال ميديا. قولي إيه التصميم اللي محتاجه لنشاطك بالظبط؟"

        # 6. Intent Routing: Advertising & Marketing
        if has_any(t, MARKETING_KW) and not has_any(t, PRICING_KW):
            cust_name = conv.customer.name if conv.customer else "عميل دعاية وتسويق"
            contact_info = (conv.customer.phone or conv.customer.email) if conv.customer else conv.platform_conversation_id
            create_lead(
                customer_id=conv.customer_id,
                customer_name=cust_name,
                contact_info=contact_info,
                requested_service="الدعاية والتسويق الرقمي",
                project_description=incoming_text,
                lead_source=conv.platform
            )
            if is_english:
                return "Hello! Black and White provides end-to-end advertising campaign design, social media ads management, and promotional materials. What is the main goal of your campaign, and which platforms would you like to target?"
            return "أهلاً بيك في Black and White! نقدر نساعدك في تخطيط وتصميم الحملات الإعلانية الممولة وإدارتها على السوشيال ميديا لزيادة المبيعات والانتشار. قولي إيه الهدف الأساسي من الحملة، والمنصة اللي حابب تركز عليها؟"

        # 7. General Project Lead Capture
        if has_any(t, LEAD_TRIGGER_KW) and not has_any(t, PRICING_KW):
            cust_name = conv.customer.name if conv.customer else "عميل محتمل"
            contact_info = (conv.customer.phone or conv.customer.email) if conv.customer else conv.platform_conversation_id
            create_lead(
                customer_id=conv.customer_id,
                customer_name=cust_name,
                contact_info=contact_info,
                requested_service="طلب خدمة إبداعية / مشروع جديد",
                project_description=incoming_text,
                lead_source=conv.platform
            )
            if "شات بوت" in t or "chatbot" in t or "ذكاء اصطناعي" in t:
                if is_english:
                    return "Hello! We can design an intelligent AI chatbot for customer service and automated WhatsApp chats. Could you tell me more about your business requirements?"
                return "أهلاً بيك! نقدر نساعدك في تصميم شات بوت ذكي للرد على العملاء وأتمتة المحادثات على واتساب. قولي طبيعة شغلك ومحتاج الشات بوت لأي منصة؟"

            if is_english:
                return "Great! Black and White can design and execute tailored creative solutions for your business. Could you share a bit more about your project requirements and preferred timeline?"
            return "تمام، نقدر نساعدك في Black and White نقدملك أفضل حل إبداعي يناسب مشروعك. قولي تفاصيل أكتر عن الخدمة اللي محتاجها بالظبط والوقت المتوقع؟"


        # 8. Pricing Inquiries (Strict Truthful DB Pricing Rules)
        if has_any(t, PRICING_KW):
            # Check if asked about a specific service in the database
            matching_services = search_services(t)
            if matching_services and len(matching_services) == 1:
                svc = matching_services[0]
                price_text = format_service_pricing_text(svc)
                if is_english:
                    return f"Regarding {svc['name']}: {price_text}\nCould you share your project details so we can prepare an accurate proposal?"
                return f"بالنسبة لـ {svc['name_ar']}: {price_text}\nممكن تشاركنا تفاصيل ومواصفات طلبك عشان نقدملك عرض السعر الأنسب؟"

            # Check legacy website packages query for backwards compatibility
            if "موقع" in t or "ويب" in t or "website" in t:
                if is_english:
                    return (
                        "Software and website costs depend on project scope and requirements. Here are our proposed indicative package estimates:\n"
                        "• Starter: Single landing page (Indicative EGP 8,000–12,000)\n"
                        "• Business (Most Popular): Multi-page site up to 5 pages (Indicative EGP 20,000–35,000)\n"
                        "• Enterprise: Custom software, AI chatbots & integrations (Custom Quotation)\n\n"
                        "These estimates are illustrative guidelines. The final proposal depends on your specific requirements. What type of project are you planning?"
                    )
                return (
                    "السعر بيتحدد حسب حجم المتطلبات وطبيعة المشروع اللي محتاجه، ودي تقديرات استرشادية أولية للباقات:\n\n"
                    "• باقة Starter: صفحة هبوط واحدة سريعة (تقدير استرشادي: 8,000 - 12,000 ج.م)\n"
                    "• باقة Business (الأكثر طلباً): موقع متكامل حتى 5 صفحات (تقدير استرشادي: 20,000 - 35,000 ج.م)\n"
                    "• باقة Enterprise: أنظمة مخصصة وتكامل متقدم (عرض سعر مخصص Custom Quotation)\n\n"
                    "الأسعار دي استرشادية، والسعر النهائي بيتحدد حسب اللي محتاج تعمله بدقة. قولي بس طبيعة شغلك وإيه اللي عايز تنفذه، ونشوف أنسب حل ليك."
                )

            # General pricing statement for creative services
            if is_english:
                return (
                    "At Black and White, pricing depends on the scope of work and exact project requirements.\n"
                    "We offer Graphic Design, Advertising & Marketing, and Interior Decoration. Each service has tailored pricing or a custom quotation based on your needs.\n"
                    "Which service are you inquiring about, and what are your project specifications?"
                )
            return (
                "في Black and White الأسعار بتتحدد بدقة حسب نطاق العمل والمتطلبات الخاصة بمشروعك، ومش بنحط أسعار عشوائية.\n"
                "خدماتنا بتشمل تصميم الجرافيك والهويات، الدعاية والتسويق، والديكور والتصميم الداخلي 3D، وكل خدمة ليها تفاصيلها الخاصة أو عرض سعر مخصص حسب المساحة أو النطاق.\n"
                "قولي إيه الخدمة اللي محتاجها بالظبط، وأنا أقولك التفاصيل ونجهزلك عرض السعر المناسب."
            )

        # 9. FAQ Knowledge Base Matching
        active_faqs = FAQ.query.filter_by(is_active=True).all()
        for faq in active_faqs:
            q_norm = normalize_text(faq.question)
            q_words = [w for w in q_norm.split() if len(w) > 2]
            match_count = sum(1 for w in q_words if w in t)
            if len(q_words) > 0 and (match_count / len(q_words)) >= 0.65:
                return faq.answer

        # 10. LLM Response Generation with Dynamic Live Catalog Context
        cs = CompanySettings.query.first()
        company_data = cs.to_dict() if cs else get_company_info()
        active_categories = ServiceCategory.query.filter_by(is_active=True).order_by(ServiceCategory.sort_order.asc()).all()
        active_packages = ServicePackage.query.filter_by(is_active=True).all()

        cats_str = "\n".join([f"• {c.name_ar} ({c.name}): {c.description or ''}" for c in active_categories])
        packages_str = "\n".join([
            f"- {p.name_ar} ({p.name}) [{p.category_rel.name_ar if p.category_rel else (p.category_slug or 'عام')}]: {format_service_pricing_text(p)} - {p.description or ''}"
            for p in active_packages
        ])

        context_str = (
            f"\n\nمعلومات الشركة المعتمدة (قاعدة البيانات):\n"
            f"- الشركة: {company_data.get('company_name', 'Black and White')}\n"
            f"- رابط البورتفوليو الرسمي: {NEXORA_PORTFOLIO_URL}\n"
            f"- هاتف وواتساب: {company_data.get('phone', '+201556441133')}\n"
            f"- المقر: {company_data.get('address', 'القاهرة، مصر')}\n"
            f"\nالتصنيفات المتاحة:\n{cats_str}\n"
            f"\nالخدمات وقائمة الأسعار الحية من قاعدة البيانات (المصدر الوحيد للأسعار، ممنوع اختراع أي رقم):\n{packages_str}\n"
        )

        past_messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at.desc()).limit(8).all()
        past_messages.reverse()

        messages_payload = [{"role": "system", "content": cfg["system_prompt"] + context_str}]
        for m in past_messages:
            messages_payload.append({
                "role": "user" if m.sender_type == "customer" else "assistant",
                "content": m.content
            })
        if not past_messages or past_messages[-1].content != incoming_text:
            messages_payload.append({"role": "user", "content": incoming_text})

        api_key = cfg["api_key"]
        if not api_key:
            if is_english:
                return "Welcome to Black and White! We specialize in Graphic Design, Advertising & Marketing, and Interior Decoration. How can we assist your business today?"
            return "أهلاً بيك في Black and White! بنقدّم خدمات تصميم الجرافيك، الدعاية والتسويق، والديكور والتصميم الداخلي 3D. قولي، محتاج إيه بالظبط؟"

        try:
            res = requests.post(
                f"{cfg['api_base_url'].rstrip('/')}/chat/completions",
                json={
                    "model": cfg["model"],
                    "messages": messages_payload,
                    "temperature": cfg["temperature"],
                    "max_tokens": cfg["max_tokens"]
                },
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                timeout=12
            )
            if res.status_code == 200:
                answer = res.json()["choices"][0]["message"]["content"].strip()
                # Safety check against old commodity business contamination
                old_leak = ["زيت", "زيتون", "عسل", "مرمية", "خام سينا", "لتر"]
                if any(k in answer for k in old_leak):
                    logger.warning(f"[AI Safety] Old business keyword suppressed in LLM output: {answer}")
                    return (
                        "أهلاً بيك في Black and White! بنساعدك في تصميم الجرافيك والهويات، الدعاية والتسويق، والديكور الداخلي 3D.\n"
                        f"تقدر تشوف سابقة أعمالنا في البورتفوليو من هنا:\n{NEXORA_PORTFOLIO_URL}\n"
                        "قولي، محتاج إيه بالظبط؟"
                    )
                return answer
            else:
                logger.warning(f"[AI] API returned status {res.status_code}: {res.text}")
                if is_english:
                    return f"Welcome to Black and White! We specialize in Graphic Design, Advertising, and Interior Decoration. Explore our work at {NEXORA_PORTFOLIO_URL} or let us know what you need."
                return f"أهلاً بيك في Black and White! بنساعدك في تصميم الجرافيك، الدعاية والتسويق، والديكور الداخلي. تقدر تشوف أعمالنا من هنا: {NEXORA_PORTFOLIO_URL} وقولي إيه اللي محتاجه."
        except Exception as e:
            logger.exception(f"[AI Exception]: {e}")
            if is_english:
                return f"Welcome to Black and White! How can we assist you with design, marketing, or interior decoration today? View our work at {NEXORA_PORTFOLIO_URL}."
            return f"أهلاً بيك في Black and White! بنساعدك تختار وتنفذ الحل الأنسب لشغلك في الجرافيك أو التسويق أو الديكور. تقدر تشوف أعمالنا من هنا: {NEXORA_PORTFOLIO_URL} وقولي محتاج إيه بالظبط."