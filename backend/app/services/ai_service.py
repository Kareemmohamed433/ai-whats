import os
import re
import json
import logging
import requests
from datetime import datetime, timezone
from app.models import (
    AISettings, CompanySettings, StoreSettings, FAQ, KnowledgeBaseArticle,
    ServicePackage, Conversation, Message, Customer, Lead
)
from app.services.ai_tools import (
    get_portfolio_url, get_portfolio_projects, get_service_packages,
    get_service_package, get_company_info, create_lead, escalate_to_human,
    NEXORA_PORTFOLIO_URL, NEXORA_PORTFOLIO_PROJECTS
)
from app.extensions import db

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = """أنت مساعد خدمة العملاء الذكي لشركة NEXORA Software Solutions المتخصصة في تطوير البرمجيات، المواقع الإلكترونية، حلول الذكاء الاصطناعي، والأتمتة الذكية.
شعار الشركة: Ideas → Code → Impact (من الفكرة إلى الكود، ومن الكود إلى التأثير).

رابط بورتفوليو وأعمال الشركة الرسمي:
https://company-pi-two.vercel.app/

وسائل التواصل الرسمية للشركة:
- هاتف / واتساب: +201556441133
- البريد الإلكتروني: contact@nexorasolutions.com
- المقر: القاهرة، مصر
- ساعات العمل: الأحد إلى الخميس من 9:00 ص حتى 6:00 م (توقيت القاهرة)

مجالات وخدمات NEXORA:
1. تطوير المواقع والمنصات (Web Development): مواقع احترافية للشركات، صفحات هبوط، مواقع متعددة الصفحات، تصميم UI/UX فائق الجودة، سرعة فائقة، متوافقة مع الموبايل، وتهيئة SEO.
2. حلول الذكاء الاصطناعي (AI Solutions): شات بوت ذكي للمحادثات، مساعد خدمة عملاء للمواقع وواتساب، معالجة المستندات، وأنظمة RAG الذكية.
3. أتمتة العمليات (Workflow Automation): ربط واتساب، دمج أنظمة CRM وإدارة العملاء، أتمتة مهام n8n والـ Webhooks وGoogle Sheets.
4. تطوير البرمجيات المخصصة (Custom Software): أنظمة ويب مخصصة، لوحات تحكم، واجهات برمجية REST APIs، وقواعد بيانات آمنة.
5. حلول نمو الأعمال (Business Growth): صفحات حملات تسويقية، تتبع التحليلات، وتحسين مسار تحويل العملاء.

باقات الخدمات الثلاث المتاحة:
1. باقة الانطلاق (Starter): تناسب الشركات الناشئة والأفراد. صفحة هبوط واحدة سريعة، تصميم متجاوب، ربط نموذج واتساب، SEO أساسي، استضافة وSSL، ودعم فني لمدة أسبوعين. (السعر التقديري الاسترشادي المقترح: 8,000 - 12,000 ج.م - غير معتمد ورسمي، السعر النهائي يتحدد بدقة بحسب المتطلبات).
2. باقة الأعمال (Business) - الأكثر طلباً: موقع متكامل حتى 5 صفحات، دعم لغتين عربي وإنجليزي، معرض أعمال أو خدمات، ربط تحليلات، SEO متقدم، ودعم فني لمدة شهر. (السعر التقديري الاسترشادي المقترح: 20,000 - 35,000 ج.م - غير معتمد ورسمي، السعر النهائي يتحدد بدقة بحسب المتطلبات).
3. الباقة المتقدمة (Enterprise): أنظمة برمجية مخصصة بالكامل، شات بوت ذكاء اصطناعي، أتمتة عمليات وربط CRM، أمان عالي، وخطة صيانة ودعم مستمر. (السعر: عرض سعر مخصص حسب المتطلبات Custom Quotation).

قواعد السلوك الأساسية:
1. تحدث بأسلوب مهني وودود (باللهجة المصرية اللبقة عند التحدث بالعربية، أو باللغة الإنجليزية إذا كان العميل يتحدث بالإنجليزية).
2. عند السؤال عن سابقة الأعمال أو البورتفوليو أو مشاريع سابقة، قدّم رابط البورتفوليو الرسمي فوراً: https://company-pi-two.vercel.app/
3. عند السؤال عن الأسعار، وضّح أن الأسعار المذكورة هي تقديرات استرشادية أولية، وأن التسعير النهائي يعتمد تماماً على نطاق ومتطلبات المشروع المحددة بعد دراستها.
4. ممنوع نهائياً اختراع عملاء أو أسعار رسمية مؤكدة أو خصومات وهمية أو مشاريع غير موجودة في المعرض.
5. إذا طلب العميل التواصل مع موظف أو خدمة العملاء، رحب بذلك وسيتم تحويل المحادثة لفريق المهندسين.
6. اجمع متطلبات العميل تدريجياً وبذكاء: طبيعة النشاط، الخدمة المطلوبة، الميزانية التقريبية، والجدول الزمني المتوقع.
7. لا تتحدث مطلقاً عن منتجات مادية أو زيوت أو أعشاب أو شحن محافظات، لأن NEXORA شركة برمجيات وتكنولوجيا.
"""

HANDOFF_MESSAGE = "أكيد، هحوّلك دلوقتي لأحد مهندسي وفريق خدمة عملاء NEXORA لمتابعة استفسارك بالتفصيل."
HANDOFF_MESSAGE_EN = "Certainly, I am transferring your inquiry to a NEXORA software solutions representative right now."

PORTFOLIO_MESSAGE_AR = """طبعًا، تقدر تتفرج على بورتفوليو NEXORA وتشوف نماذج المشاريع والأعمال المعروضة عندنا من هنا:
https://company-pi-two.vercel.app/

ولو مهتم بنوع معين من المشاريع، زي المواقع الإلكترونية أو حلول الذكاء الاصطناعي أو الأتمتة، قولي محتاج تشوف إيه وأنا أساعدك."""

PORTFOLIO_MESSAGE_EN = """Of course! You can explore NEXORA's official portfolio and showcase of projects here:
https://company-pi-two.vercel.app/

Feel free to tell me what type of project you're interested in (websites, AI chatbots, or automation workflows) so I can help you further!"""

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
    "دعم", "تحدث مع موظف", "كلمني بشري", "خدمه عملاء", "اتصال هاتفي",
    "customer service", "speak to human", "talk to human", "talk to representative", "agent"
])

PORTFOLIO_KW = tuple(normalize_text(w) for w in [
    "بورتفوليو", "شغلكم", "اعمالكم", "سابقة اعمال", "سابقه اعمال", "مشاريع سابقة", "مشاريع سابقه",
    "نماذج", "وروني مواقع", "شوف شغلكم", "اشوف شغلكم", "مشاريع ai", "شغل الشات بوت",
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

LEAD_TRIGGER_KW = tuple(normalize_text(w) for w in [
    "عايز اعمل", "محتاج موقع", "محتاج شات بوت", "عايز شات بوت", "محتاج نظام", "عايز سيستم",
    "مشروع جديد", "عايز اطور", "ابدا مشروع", "ابدأ مشروع", "نظام crm",
    "i want a website", "need a chatbot", "need automation", "build a website", "start a project"
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
            # Check if specific project type was asked (e.g., tourism, food, fashion)
            if any(k in t for k in ["سياح", "سفر", "رحلات", "tourism", "travel"]):
                proj = get_portfolio_projects("tourism")
                desc = proj[0]["description"] if proj else ""
                if is_english:
                    return f"We developed Travel Aura, an elegant travel portal with interactive booking flows.\nYou can check our full portfolio here:\n{NEXORA_PORTFOLIO_URL}"
                return f"طبعًا، نفذنا مشروع 'ترافيل أورا للسياحة' وهي منصة سياحية راقية مع مسار حجز واستفسار تفاعلي.\nتقدر تتفرج عليها وعلى باقي مشاريعنا في البورتفوليو هنا:\n{NEXORA_PORTFOLIO_URL}"

            if any(k in t for k in ["مطعم", "اكل", "طعام", "restaurant", "dining"]):
                if is_english:
                    return f"We built La Casa Fine Dining, featuring interactive QR menus and VIP table reservations.\nExplore our full portfolio here:\n{NEXORA_PORTFOLIO_URL}"
                return f"طبعًا، نفذنا مشروع 'لاكازا للمأكولات الفاخرة' بنمط داكن أنيق ونظام منيو QR وحجز طاولات VIP.\nتقدر تشوفه في البورتفوليو هنا:\n{NEXORA_PORTFOLIO_URL}"

            if any(k in t for k in ["شات بوت", "ذكاء اصطناعي", "ai", "chatbot"]):
                if is_english:
                    return f"Yes, we build intelligent AI customer service assistants and workflow bots.\nCheck our demonstrated capabilities and portfolio here:\n{NEXORA_PORTFOLIO_URL}\nWould you like to discuss requirements for your own AI chatbot?"
                return f"نعم بكل تأكيد، بنطوّر شات بوت ذكي وحلول ذكاء اصطناعي وأتمتة مخصصة لخدمة العملاء على واتساب والويب.\nتقدر تتصفح أعمالنا وقدراتنا من هنا:\n{NEXORA_PORTFOLIO_URL}\nتحب تقولي فكرة الشات بوت اللي محتاجه ونبدأ نناقش تفاصيله؟"

            return PORTFOLIO_MESSAGE_EN if is_english else PORTFOLIO_MESSAGE_AR

        # 3. Difference between Starter and Business
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

        # 4. Lead Intent / Project Inquiry progressive capture
        if has_any(t, LEAD_TRIGGER_KW):
            # Capture lead record
            cust_name = conv.customer.name if conv.customer else "عميل محتمل"
            contact_info = (conv.customer.phone or conv.customer.email) if conv.customer else conv.platform_conversation_id
            create_lead(
                customer_id=conv.customer_id,
                customer_name=cust_name,
                contact_info=contact_info,
                requested_service="طلب موقع / شات بوت برمجي",
                project_description=incoming_text,
                lead_source=conv.platform
            )

            if "عقار" in t or "real estate" in t:
                if is_english:
                    return "Welcome! We can develop a custom real estate website showcasing your properties, along with an AI assistant to qualify buyer inquiries. Would you need an informative website only, or also an administrative dashboard to manage listings and leads?"
                return "أهلًا بحضرتك، نقدر نساعدك في تطوير موقع عقاري احترافي يعرض مشروعاتك ووحداتك، مع شات بوت ذكي يساعد في الرد على العملاء وجمع بيانات المهتمين. ممكن أعرف هل محتاج موقع تعريفي فقط، ولا كمان لوحة تحكم لإدارة المشروعات والعملاء؟"

            if "شات بوت" in t or "chatbot" in t:
                if is_english:
                    return "Hello! We can design an intelligent AI chatbot for customer service and automated chats. Could you tell me more about your business, and whether you need the bot for FAQs only, or also for lead capture and CRM integrations?"
                return "أهلًا بحضرتك، نقدر نساعدك في تصميم شات بوت ذكي للرد على استفسارات العملاء وأتمتة المحادثات. ممكن أعرف طبيعة نشاطك، وهل محتاج البوت يجاوب عن الأسئلة المتكررة بس، ولا كمان يجمع بيانات العملاء ويرتبط بأنظمة تانية؟"

            if is_english:
                return "Great! NEXORA can design and build modern software tailored to your goals. Could you share a bit more about your industry, expected timeline, and any specific features you need?"
            return "تمام، يسعدنا في NEXORA مساعدتك في بناء وتطوير مشروعك البرمجي بأعلى معايير الجودة. ممكن تشاركني تفاصيل أكتر عن طبيعة نشاطك وأهم الميزات المطلوبة في المشروع؟"

        # 5. General Pricing Questions
        if has_any(t, PRICING_KW):
            if is_english:
                return (
                    "At NEXORA, software and website costs depend on project scope and requirements. Here are our proposed indicative package estimates:\n"
                    "• Starter: Single landing page (Indicative EGP 8,000–12,000)\n"
                    "• Business (Most Popular): Multi-page site up to 5 pages (Indicative EGP 20,000–35,000)\n"
                    "• Enterprise: Custom software, AI chatbots & integrations (Custom Quotation)\n\n"
                    "These estimates are illustrative guidelines. The final proposal depends on your specific requirements. What type of project are you planning?"
                )
            return (
                "تكلفة المواقع والحلول البرمجية في NEXORA تتحدد وفقاً لحجم المتطلبات والميزات المطلوبة. وإليك نطاق الباقات الاسترشادية المقترحة:\n\n"
                "• باقة الانطلاق (Starter): صفحة هبوط واحدة سريعة (تقدير استرشادي: 8,000 - 12,000 ج.م)\n"
                "• باقة الأعمال (Business - الأكثر طلباً): موقع متكامل حتى 5 صفحات (تقدير استرشادي: 20,000 - 35,000 ج.م)\n"
                "• الباقة المتقدمة (Enterprise): أنظمة مخصصة وشات بوت وربط معقد (عرض سعر مخصص Custom Quotation)\n\n"
                "الأسعار المذكورة استرشادية، والعرض النهائي يتم تحديده بدقة بعد معرفة تفاصيل مشروعك. ممكن تشاركني فكرة مشروعك عشان أحددلك التكلفة الأنسب؟"
            )

        # 6. FAQ Knowledge Base Matching
        active_faqs = FAQ.query.filter_by(is_active=True).all()
        for faq in active_faqs:
            q_norm = normalize_text(faq.question)
            # Match if high overlap
            q_words = [w for w in q_norm.split() if len(w) > 2]
            match_count = sum(1 for w in q_words if w in t)
            if len(q_words) > 0 and (match_count / len(q_words)) >= 0.65:
                return faq.answer

        # 7. LLM Response Generation with NEXORA Context
        cs = CompanySettings.query.first()
        company_data = cs.to_dict() if cs else get_company_info()
        packages = ServicePackage.query.filter_by(is_active=True).all()
        packages_str = "\n".join([f"- {p.name_ar} ({p.name}): {p.indicative_price_text or 'عرض سعر مخصص'} - {p.description}" for p in packages])

        context_str = (
            f"\n\nمعلومات الشركة المعتمدة:\n"
            f"- الشركة: {company_data.get('company_name', 'NEXORA Software Solutions')}\n"
            f"- رابط البورتفوليو الرسمي: {NEXORA_PORTFOLIO_URL}\n"
            f"- هاتف وواتساب: {company_data.get('phone', '+201556441133')}\n"
            f"- البريد الإلكتروني: {company_data.get('email', 'contact@nexorasolutions.com')}\n"
            f"- المقر: {company_data.get('address', 'القاهرة، مصر')}\n"
            f"\nباقات الخدمات المتاحة:\n{packages_str}\n"
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
                return "Welcome to NEXORA Software Solutions! We build modern websites, AI solutions, and smart automation systems. How can we help your business today?"
            return "أهلاً بك في NEXORA Software Solutions! بنساعدك في تطوير المواقع العصرية، حلول الذكاء الاصطناعي، وأنظمة الأتمتة الذكية. إزاي نقدر نساعدك النهاردة؟"

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
                # Safety check against old business contamination
                old_leak = ["زيت", "زيتون", "عسل", "مرمية", "خام سينا", "لتر"]
                if any(k in answer for k in old_leak):
                    logger.warning(f"[AI Safety] Old business keyword suppressed in LLM output: {answer}")
                    return (
                        "أهلاً بك في NEXORA Software Solutions! نحن متخصصون في تطوير المواقع وحلول الذكاء الاصطناعي والأتمتة الذكية.\n"
                        f"يمكنك الاطلاع على معرض أعمالنا الرسمي من هنا:\n{NEXORA_PORTFOLIO_URL}\n"
                        "كيف يمكننا مساعدة مشروعك اليوم؟"
                    )
                return answer
            else:
                logger.warning(f"[AI] API returned status {res.status_code}: {res.text}")
                if is_english:
                    return f"Welcome to NEXORA! We specialize in modern web development, AI chatbots, and process automation. Visit our portfolio at {NEXORA_PORTFOLIO_URL} or let us know what you need."
                return f"أهلاً بك في NEXORA! نحن متخصصون في تطوير المواقع والحلول الذكية وأنظمة الأتمتة. يمكنك استكشاف أعمالنا عبر: {NEXORA_PORTFOLIO_URL} وتحديد الخدمة المناسبة لك."
        except Exception as e:
            logger.exception(f"[AI Exception]: {e}")
            if is_english:
                return f"Welcome to NEXORA! How can we assist you with web development or AI automation today? You can view our work at {NEXORA_PORTFOLIO_URL}."
            return f"أهلاً بك في NEXORA! يسعدنا مساعدتك في اختيار وتطوير الحل البرمجي الأنسب لمشروعك. تقدر تشوف أعمالنا من هنا: {NEXORA_PORTFOLIO_URL}."