from app.models import (
    Product, Customer, Order, OrderItem, StoreSettings, SupportTicket, 
    Conversation, InternalNote, ConversationAuditLog, PaymentReview, 
    CustomerActivity
)
from app.extensions import db
from app.services.socket_service import SocketService
from datetime import datetime

STORE_BASE_URL = "https://khamsina-web-1e03dce1.hosted.cumin.dev"

def get_products():
    """Retrieve all active products in the store."""
    products = Product.query.filter_by(is_active=True).all()
    return [p.to_dict() for p in products]

def get_product(product_id):
    """Retrieve specific product by ID."""
    product = Product.query.get(product_id)
    return product.to_dict() if product else None

def get_product_link(product_id):
    """Get official product URL for storefront."""
    product = Product.query.get(product_id)
    if product:
        return f"{STORE_BASE_URL}/products/{product.id}"
    return f"{STORE_BASE_URL}/products"

def search_products(query):
    """Search products by name, description, or category."""
    if not query:
        return get_products()
    pattern = f"%{query}%"
    products = Product.query.filter(
        db.or_(
            Product.name.ilike(pattern),
            Product.description.ilike(pattern),
            Product.category.ilike(pattern)
        )
    ).all()
    return [p.to_dict() for p in products]

def check_product_stock(product_id):
    """Check stock availability for a product."""
    product = Product.query.get(product_id)
    if not product:
        return {"error": "المنتج غير موجود"}
    return {
        "product_id": product.id,
        "name": product.name,
        "stock": product.stock,
        "in_stock": product.stock > 0
    }

def get_store_info():
    """Retrieve store info, policies, and contact details."""
    settings = StoreSettings.query.first()
    return settings.to_dict() if settings else {}

def get_shipping_info():
    """Retrieve shipping policy details."""
    settings = StoreSettings.query.first()
    if settings:
        return {
            "shipping_policy": settings.shipping_policy,
            "free_shipping_threshold": settings.free_shipping_threshold,
            "delivery_time": "2-4 أيام عمل لجميع المحافظات"
        }
    return {
        "shipping_policy": "شحن لجميع المحافظات",
        "free_shipping_threshold": 500,
        "delivery_time": "2-4 أيام عمل"
    }

def get_payment_methods():
    """Retrieve available payment methods."""
    settings = StoreSettings.query.first()
    if settings:
        return {
            "payment_methods": settings.payment_methods,
            "instapay_details": "InstaPay: 01000000000",
            "vodafone_cash_details": "Vodafone Cash: 01000000000"
        }
    return {
        "payment_methods": "الدفع عند الاستلام، InstaPay، فودافون كاش",
        "instapay_details": "InstaPay: 01000000000",
        "vodafone_cash_details": "Vodafone Cash: 01000000000"
    }

def get_customer_profile(customer_id):
    """Retrieve customer 360 profile by ID."""
    customer = Customer.query.get(customer_id)
    return customer.to_dict() if customer else None

def get_customer_context(customer_id):
    """Retrieve full commercial context for AI decision making."""
    customer = Customer.query.get(customer_id)
    if not customer:
        return {}
    
    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).all()
    reviews = PaymentReview.query.filter_by(customer_id=customer_id).order_by(PaymentReview.created_at.desc()).all()

    return {
        "customer_id": customer.id,
        "name": customer.name,
        "phone": customer.phone,
        "email": customer.email,
        "total_orders": len(orders),
        "last_order": orders[0].to_dict() if orders else None,
        "pending_payment_reviews": [r.to_dict() for r in reviews if r.status == 'pending']
    }

def get_customer_orders(customer_id):
    """Retrieve all orders placed by a customer."""
    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).all()
    return [o.to_dict() for o in orders]

def get_order(order_id):
    """Retrieve order details by order ID or order number."""
    if str(order_id).isdigit():
        order = Order.query.get(int(order_id))
    else:
        order = Order.query.filter_by(order_number=str(order_id)).first()
    return order.to_dict() if order else None

def search_orders(query):
    """Search orders by query string."""
    pattern = f"%{query}%"
    orders = Order.query.filter(
        db.or_(
            Order.order_number.ilike(pattern),
            Order.shipping_address.ilike(pattern),
            Order.city.ilike(pattern)
        )
    ).all()
    return [o.to_dict() for o in orders]

def get_customer_order(order_id):
    """Retrieve order details."""
    return get_order(order_id)

def get_or_create_order_draft(conversation_id):
    """Retrieve or create transient order draft for a conversation."""
    conv = Conversation.query.get(conversation_id)
    if not conv:
        return None
    draft = conv.order_draft
    if not draft:
        draft = {
            "items": [],
            "shipping_address": None,
            "city": "القاهرة",
            "payment_method": "cash_on_delivery",
            "awaiting_confirmation": False,
            "confirmed": False
        }
        conv.order_draft = draft
        db.session.commit()
    return draft

def update_order_draft(conversation_id, items=None, shipping_address=None, city=None, payment_method=None, awaiting_confirmation=None, confirmed=None):
    """Update order draft details."""
    conv = Conversation.query.get(conversation_id)
    if not conv:
        return None
    draft = conv.order_draft or {
        "items": [],
        "shipping_address": None,
        "city": "القاهرة",
        "payment_method": "cash_on_delivery",
        "awaiting_confirmation": False,
        "confirmed": False
    }
    if items is not None:
        draft["items"] = items
    if shipping_address is not None:
        draft["shipping_address"] = shipping_address
    if city is not None:
        draft["city"] = city
    if payment_method is not None:
        draft["payment_method"] = payment_method
    if awaiting_confirmation is not None:
        draft["awaiting_confirmation"] = awaiting_confirmation
    if confirmed is not None:
        draft["confirmed"] = confirmed

    conv.order_draft = draft
    db.session.commit()
    return draft

def clear_order_draft(conversation_id):
    """Clear order draft from conversation."""
    conv = Conversation.query.get(conversation_id)
    if conv:
        conv.order_draft = None
        db.session.commit()

def create_order(customer_id, items, shipping_address="", city="القاهرة", payment_method="cash_on_delivery", confirmed=False, conversation_id=None):
    """Create a new customer order directly from AI chat with strict Backend Validation Guard (Requirement #10)."""
    customer = Customer.query.get(customer_id)
    if not customer:
        return {"success": False, "error": "العميل غير موجود في النظام"}

    if not items or not isinstance(items, list) or len(items) == 0:
        return {"success": False, "error": "يجب تحديد المنتجات والكميات المطلوبة بشكل صريح أولاً"}

    # Requirement #10: Backend Guard Check for explicit final confirmation
    if not confirmed:
        # If conversation_id is provided, check if draft is confirmed
        if conversation_id:
            conv = Conversation.query.get(conversation_id)
            draft = conv.order_draft if conv else None
            if not draft or not draft.get('confirmed'):
                return {"success": False, "error": "لا يمكن إنشاء الطلب دون تأكيد صريح ونهائي من العميل."}
        else:
            return {"success": False, "error": "لا يمكن إنشاء الطلب دون تأكيد صريح ونهائي من العميل."}

    # Validate items against Database (Backend Source of Truth)
    validated_items = []
    total_amount = 0.0
    for item in items:
        product_id = item.get('product_id')
        qty = int(item.get('quantity', 0))
        if not product_id or qty <= 0:
            continue
        product = Product.query.get(product_id)
        if not product or not product.is_active:
            return {"success": False, "error": f"المنتج المعرف {product_id} غير متوفر حالياً"}
        
        unit_p = product.price
        tot_p = unit_p * qty
        total_amount += tot_p
        validated_items.append({
            "product": product,
            "quantity": qty,
            "unit_price": unit_p,
            "total_price": tot_p
        })

    if not validated_items:
        return {"success": False, "error": "لم يتم العثور على منتجات صالحة في الطلب"}

    order_num = f"KS-{int(datetime.utcnow().timestamp())}"

    order = Order(
        order_number=order_num,
        customer_id=customer_id,
        total_amount=total_amount,
        payment_method=payment_method,
        payment_status='pending',
        order_status='pending',
        shipping_address=shipping_address or customer.phone or "سيتم التأكيد هاتفياً",
        city=city
    )
    db.session.add(order)
    db.session.flush()

    for vi in validated_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=vi["product"].id,
            quantity=vi["quantity"],
            unit_price=vi["unit_price"],
            total_price=vi["total_price"]
        )
        db.session.add(order_item)
        vi["product"].stock = max(0, vi["product"].stock - vi["quantity"])

    # Clear order draft if conversation_id was provided
    if conversation_id:
        clear_order_draft(conversation_id)

    # Log Customer Activity
    act = CustomerActivity(
        customer_id=customer_id,
        activity_type='create_order',
        description=f"تم إنشاء طلب رقم {order_num} بقيمة {total_amount} ج.م بنجاح"
    )
    db.session.add(act)
    db.session.commit()

    # Socket notification
    SocketService.broadcast_order_created(order)

    return {
        "success": True,
        "order_number": order_num,
        "order": order.to_dict()
    }

def add_order_item(order_id, product_id, quantity=1):
    """Add item to existing order."""
    order = Order.query.get(order_id)
    product = Product.query.get(product_id)
    if not order or not product:
        return {"success": False, "error": "الطلب أو المنتج غير موجود"}

    unit_p = product.price
    tot_p = unit_p * int(quantity)

    item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=quantity,
        unit_price=unit_p,
        total_price=tot_p
    )
    db.session.add(item)
    order.total_amount += tot_p
    db.session.commit()
    return {"success": True, "order": order.to_dict()}

def update_order(order_id, order_status=None, payment_status=None):
    """Update order status."""
    order = Order.query.get(order_id)
    if not order:
        return {"success": False, "error": "الطلب غير موجود"}

    if order_status:
        order.order_status = order_status
    if payment_status:
        order.payment_status = payment_status

    db.session.commit()
    SocketService.broadcast_order_updated(order)
    return {"success": True, "order": order.to_dict()}

def create_payment_review(customer_id, order_id=None, conversation_id=None, screenshot_url=None, detected_amount=None, reference_number=None, ocr_data_json=None):
    """Create a pending payment review for human inspection."""
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

    act = CustomerActivity(
        customer_id=customer_id,
        activity_type='send_payment',
        description=f"تم إرسال إثبات دفع جديد بانتظار مراجعة الدعم الفني"
    )
    db.session.add(act)
    db.session.commit()

    SocketService.broadcast_payment_review_created(review)
    return review.to_dict()

def escalate_to_human(conversation_id, reason="customer_requested_human"):
    """Escalate conversation to human support staff, change ai_status to human_handled, add internal note & audit log."""
    conv = Conversation.query.get(conversation_id)
    if conv:
        prev_ai = conv.ai_status
        conv.ai_status = 'human_handled'
        conv.requires_human = True
        conv.human_handoff_at = datetime.utcnow()
        conv.priority = 'high'
        
        note = InternalNote(
            conversation_id=conversation_id,
            author_id=1, # System
            content=f"🚨 تحويل تلقائي إلى موظف الدعم: {reason}"
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

        act = CustomerActivity(
            customer_id=conv.customer_id,
            activity_type='request_human',
            description="طلب العميل التحدث مع موظف خدمة العملاء"
        )
        db.session.add(act)
        db.session.commit()

        SocketService.broadcast_ai_status_changed(conv, prev_ai, 'human_handled')
        SocketService.broadcast_human_handoff(conv, reason)
        SocketService.broadcast_conversation_update(conv)

        return {"success": True, "message": "تم تحويل المحادثة إلى الدعم البشري بنجاح."}
    return {"success": False, "error": "المحادثة غير موجودة"}
