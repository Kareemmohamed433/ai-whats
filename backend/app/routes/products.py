from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import Product, Category
from app.extensions import db

products_bp = Blueprint('products', __name__, url_prefix='/api/products')

@products_bp.route('', methods=['GET'])
def get_products():
    category = request.args.get('category')
    search = request.args.get('search', '').strip()
    active_only = request.args.get('active_only', 'false').lower() == 'true'

    query = Product.query

    if active_only:
        query = query.filter_by(is_active=True)

    if category:
        query = query.filter_by(category=category)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Product.name.ilike(pattern),
                Product.description.ilike(pattern),
                Product.sku.ilike(pattern)
            )
        )

    products = query.order_by(Product.id.asc()).all()
    categories = Category.query.all()

    return jsonify({
        "success": True,
        "products": [p.to_dict() for p in products],
        "categories": [c.to_dict() for c in categories]
    })

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product_detail(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المنتج غير موجود"}}), 404
    return jsonify({"success": True, "product": product.to_dict()})

@products_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    sku = data.get('sku', '').strip()
    price = data.get('price')

    if not name or not sku or price is None:
        return jsonify({"success": False, "error": {"code": "INVALID_FIELDS", "message": "اسم المنتج، كود SKU والسعر مطلوبة."}}), 400

    existing = Product.query.filter_by(sku=sku).first()
    if existing:
        return jsonify({"success": False, "error": {"code": "SKU_EXISTS", "message": "كود SKU مستخدم بالفعل."}}), 400

    product = Product(
        name=name,
        sku=sku,
        category=data.get('category', 'عام'),
        description=data.get('description'),
        price=float(price),
        original_price=float(data.get('original_price')) if data.get('original_price') else float(price),
        discount=float(data.get('discount', 0.0)),
        stock=int(data.get('stock', 0)),
        packaging_type=data.get('packaging_type', 'عبوة زجاجية'),
        image_url=data.get('image_url'),
        is_active=bool(data.get('is_active', True)),
        specifications=data.get('specifications')
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({"success": True, "product": product.to_dict()}), 201

@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المنتج غير موجود"}}), 404

    data = request.get_json() or {}
    if 'name' in data:
        product.name = data['name']
    if 'category' in data:
        product.category = data['category']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = float(data['price'])
    if 'original_price' in data:
        product.original_price = float(data['original_price'])
    if 'discount' in data:
        product.discount = float(data['discount'])
    if 'stock' in data:
        product.stock = int(data['stock'])
    if 'packaging_type' in data:
        product.packaging_type = data['packaging_type']
    if 'image_url' in data:
        product.image_url = data['image_url']
    if 'is_active' in data:
        product.is_active = bool(data['is_active'])
    if 'specifications' in data:
        product.specifications = data['specifications']

    db.session.commit()
    return jsonify({"success": True, "product": product.to_dict()})

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المنتج غير موجود"}}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"success": True, "message": "تم حذف المنتج بنجاح."})
