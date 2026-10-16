import os
import re
import json
import logging
import requests
from app.models import AISettings, StoreSettings, FAQ, KnowledgeBaseArticle, Product, Conversation, Message, Customer, Order, PaymentReview
from app.services.ai_tools import (
    get_products, get_product, get_product_link, search_products, check_product_stock,
    get_customer_profile, get_customer_orders, get_order, search_orders,
    get_store_info, get_shipping_info, get_payment_methods, create_order,
    create_payment_review, escalate_to_human, get_or_create_order_draft, update_order_draft, clear_order_draft
)
from app.extensions import db

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = """أنت مساعد خدمة العملاء الذكي لبراند "خام سينا" (Khams Sinaa) المتخصص في أجود منتجات زيت الزيتون السيناوي البكر الممتاز.

قواعد سلوك الـ AI الأساسية:
1. تحدث بتلقائية ومودة باللهجة المصرية، واختصر دون تكرار نفس الجمل الترحيبية.
2. استخدم اسم العميل فقط عندما يكون ذلك طبيعياً ومفيداً في سياق الحديث.
3. ممنوع نهائياً اختراع أسعار أو بيانات غير موجودة في النظام.
4. أجب على أسئلة الفوائد والمنتجات بوضوح قبل الشروع في إجراءات الطلب.
"""

HANDOFF_MESSAGE = "أكيد، هحوّلك دلوقتي لأحد أفراد خدمة العملاء لمتابعة طلبك."

# Arabic text normalization
_DIGIT_MAP = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "0123456789" * 2)
_CHAR_MAP = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي", "ة": "ه", "ؤ": "و", "ئ": "ي"})
_DIACRITICS_RE = re.compile(r"[\u0640\u064B-\u065F\u0670]")

def normalize_text(text):
    if not text: return ""
    t = str(text).translate(_DIGIT_MAP)
    t = _DIACRITICS_RE.sub("", t)
    t = t.translate(_CHAR_MAP).lower()
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"(\d)([^\W\d_])", r"\1 \2", t)
    t = re.sub(r"(?<!\S)ا\s+(?=لتر)", "1 ", t)
    return re.sub(r"\s+", " ", t).strip()

def has_any(text, kws):
    return any(k in text for k in kws)

# Keyword groups (normalized)
ESCALATION_KW = tuple(normalize_text(w) for w in ["خدمة العملاء", "خدمه العملا", "حد من الدعم", "عايز موظف", "عايز حد", "مواظف", "دعم"])
PAYMENT_PROOF_KW = tuple(normalize_text(w) for w in ["اثبات دفع", "صورة دفع", "وصل", "تحويل"])
ORDER_LOOKUP_KW = tuple(normalize_text(w) for w in ["رقم الطلب", "حالة الطلب", "طلب سابق"])
ORDER_INTENT_KW = tuple(normalize_text(w) for w in ["اعمل اوردر", "اعمل طلب", "اطلب", "اشتري", "عايز اوردر"])
CONFIRM_KW = tuple(normalize_text(w) for w in ["اكد", "ايوه", "ايوا", "موافق", "نفذ", "نعم", "yes"])
CANCEL_KW = tuple(normalize_text(w) for w in ["الغي", "كنسل", "لا", "cancel", "no"])

_QTY_UNITS = r"(?:عبوه|عبوات|زجاجه|قطعه|علبه|برطمان)"

class AIService:
    @staticmethod
    def get_config():
        ai_set = AISettings.query.first()
        env_key = os.getenv("AI_API_KEY", "") or os.getenv("XAI_API_KEY", "")
        env_model = os.getenv("AI_MODEL", "llama-3.3-70b-versatile")
        env_base_url = os.getenv("AI_API_BASE_URL", "https://api.groq.com/openai/v1")

        # Give absolute priority to Groq API Key from .env
        active_key = env_key if (env_key and env_key.startswith("gsk_")) else (ai_set.api_key if ai_set and ai_set.api_key else env_key)
        active_model = env_model if env_key else (ai_set.model if ai_set and ai_set.model else env_model)
        active_base_url = env_base_url if env_key else (ai_set.api_base_url if ai_set and ai_set.api_base_url else env_base_url)

        return {
            "is_enabled": True,
            "api_key": active_key,
            "api_base_url": active_base_url,
            "model": active_model,
            "temperature": 0.3,
            "max_tokens": 500,
            "system_prompt": (ai_set.system_prompt if ai_set and ai_set.system_prompt else DEFAULT_SYSTEM_PROMPT)
        }

    @classmethod
    def generate_response(cls, conversation_id, incoming_text, is_media=False, media_url=None):
        conv = Conversation.query.get(conversation_id)
        if not conv or conv.ai_status != 'active':
            return None

        cfg = cls.get_config()
        if not cfg["is_enabled"]:
            return None

        t = normalize_text(incoming_text)

        # 1. Escalation to Human Agent Check (FIXED)
        if has_any(t, ESCALATION_KW):
            escalate_to_human(conversation_id, "customer_requested_human")
            return HANDOFF_MESSAGE

        # 2. Payment Proof
        if is_media or has_any(t, PAYMENT_PROOF_KW):
            recent_order = Order.query.filter_by(customer_id=conv.customer_id).order_by(Order.created_at.desc()).first()
            create_payment_review(customer_id=conv.customer_id, order_id=recent_order.id if recent_order else None,
                                  conversation_id=conv.id, screenshot_url=media_url,
                                  detected_amount=recent_order.total_amount if recent_order else None)
            return cls._format_payment_confirmation(recent_order)

        # 3. Order Lookup
        order_num_match = re.search(r'KS-\d+', incoming_text.translate(_DIGIT_MAP), re.IGNORECASE)
        if order_num_match or has_any(t, ORDER_LOOKUP_KW):
            if order_num_match:
                ord_data = get_order(order_num_match.group(0).upper())
                if ord_data:
                    return f"أهلاً، طلبك رقم {ord_data['order_number']}: {ord_data['total_amount']} ج.م - {ord_data['order_status']}"
                return "لم أجد هذا الطلب"

        # 4. Order Flow Check (Only if strictly order placement/confirm/cancel)
        draft = get_or_create_order_draft(conv.id) or {}
        if draft.get("items") or has_any(t, ORDER_INTENT_KW) or has_any(t, CONFIRM_KW) or has_any(t, CANCEL_KW):
            reply = cls._order_flow(incoming_text, conv)
            if reply is not None:
                db.session.refresh(conv)
                if conv.ai_status != 'active':
                    return None
                return reply

        # 5. LLM Response Generation (Handles Benefits & General Questions)
        store_info = StoreSettings.query.first()
        products = Product.query.filter_by(is_active=True).all()
        products_ctx = [{"id": p.id, "name": p.name, "price": p.price, "packaging": p.packaging_type, "url": get_product_link(p.id)} for p in products]
        cust_profile = conv.customer.to_dict() if conv.customer else {}

        context_str = f"\n\nسياق العميل:\n- الاسم: {cust_profile.get('name')}\n- مسودة الطلب: {json.dumps(conv.order_draft, ensure_ascii=False)}\n\nالمنتجات والأسعار المتاحة بالمخزون:\n"
        for p in products_ctx:
            context_str += f"- {p['name']} ({p['packaging']}): {p['price']} ج.م\n"

        past_messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at.desc()).limit(10).all()
        past_messages.reverse()

        messages_payload = [{"role": "system", "content": cfg["system_prompt"] + context_str}]
        for m in past_messages:
            messages_payload.append({"role": "user" if m.sender_type == "customer" else "assistant", "content": m.content})
        if not past_messages or past_messages[-1].content != incoming_text:
            messages_payload.append({"role": "user", "content": incoming_text})

        api_key = cfg["api_key"]
        if not api_key:
            return "أهلاً بك في خام سينا 🌿! كيف يمكنني مساعدتك اليوم؟"

        try:
            res = requests.post(f"{cfg['api_base_url'].rstrip('/')}/chat/completions",
                                json={"model": cfg["model"], "messages": messages_payload, "temperature": cfg["temperature"], "max_tokens": cfg["max_tokens"]},
                                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, timeout=12)
            if res.status_code == 200:
                print("🟢 [Groq AI Success] Response generated by LLM.")
                return res.json()["choices"][0]["message"]["content"].strip()
            else:
                logger.warning(f"[AI] API returned {res.status_code}: {res.text}")
                return "أهلاً بك في خام سينا! يسعدنا إجابة كافة استفساراتك عن زيت الزيتون السيناوي 🌿."
        except Exception as e:
            logger.exception(f"[AI] Error: {e}")
            return "أهلاً بك في خام سينا! يسعدنا مساعدتك في اختيار المنتج المناسب 🌿."

    @staticmethod
    def _format_payment_confirmation(order):
        if not order:
            return "تم استلام إثبات الدفع. سيتم التحقق قريباً ✅"
        return f"تم استلام إيصال عملية الدفع للطلب رقم {order.id} بمبلغ {order.total_amount} ج.م بنجاح ✅"

    @classmethod
    def _order_flow(cls, text, conv):
        t = normalize_text(text)
        customer_name = conv.customer.name if conv.customer else ""
        draft = get_or_create_order_draft(conv.id) or {}
        products = Product.query.filter_by(is_active=True).all()

        def match_products(text_norm):
            matched = []
            for p in products:
                p_norm = normalize_text(f"{p.name} {p.packaging_type or ''}")
                if ('1 لتر' in text_norm or '1l' in text_norm) and ('1 لتر' in p_norm or '1' in p_norm):
                    matched.append(p)
                elif ('2 لتر' in text_norm or '2l' in text_norm) and ('2 لتر' in p_norm or '2' in p_norm):
                    matched.append(p)
            return matched

        has_items = bool(draft.get("items"))
        awaiting_address = has_items and not draft.get("shipping_address")
        awaiting_confirmation = has_items and draft.get("shipping_address") and not draft.get("confirmed")
        is_order_intent = has_any(t, ORDER_INTENT_KW)
        is_confirm = has_any(t, CONFIRM_KW)
        is_cancel = has_any(t, CANCEL_KW)

        if is_order_intent and not has_items:
            matched = match_products(t)
            if matched:
                items = [{"product_id": p.id, "quantity": 1, "name": p.name, "price": p.price} for p in matched]
                update_order_draft(conv.id, items=items, awaiting_confirmation=True)
                tot = sum(i["price"] * i["quantity"] for i in items)
                return f"تمام، ملخص الطلب:\n• 1 × {matched[0].name}\n• الإجمالي: {tot} ج.م\n\nمن فضلك ابعت لي العنوان لتأكيد الشحن 🌿."
            return "تحب تطلب عبوة 1 لتر أم 2 لتر زيت زيتون بكر ممتاز؟ 🌿"

        if awaiting_address:
            if is_cancel:
                clear_order_draft(conv.id)
                return "تمام، تم إلغاء مسودة الطلب 🌿"
            if t and not ('؟' in text or '?' in text):
                update_order_draft(conv.id, shipping_address=t)
                items = draft["items"]
                tot = sum(i["price"] * i["quantity"] for i in items)
                return f"تسلم! العنوان: {t}\nالإجمالي: {tot} ج.م.\n\nهل نعتمد ونؤكد الطلب؟ (قول أكد) 👇"

        if awaiting_confirmation and is_confirm:
            res = create_order(customer_id=conv.customer_id, items=draft["items"],
                               shipping_address=draft.get("shipping_address", ""), city="القاهرة",
                               confirmed=True, conversation_id=conv.id)
            if res.get("success"):
                clear_order_draft(conv.id)
                return f"تم تأكيد طلبك بنجاح 🌿!\nرقم الطلب: {res['order_number']}\nالإجمالي: {res['order']['total_amount']} ج.م\nسيتم التواصل معك هاتفياً 📞"

        return None