from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import ServicePackage, ServiceCategory
from app.extensions import db

service_packages_bp = Blueprint('service_packages', __name__, url_prefix='/api/packages')


# ==========================================
# Category Helpers & Endpoints
# ==========================================

def _find_category(identifier):
    if str(identifier).isdigit():
        cat = db.session.get(ServiceCategory, int(identifier))
        if cat:
            return cat
    return ServiceCategory.query.filter_by(slug=str(identifier).lower()).first()


@service_packages_bp.route('/categories', methods=['GET'])
def get_categories():
    """List service categories (e.g., Graphic Design, Advertising, Interior Decoration)."""
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    include_services = request.args.get('include_services', 'false').lower() == 'true'

    query = ServiceCategory.query
    if active_only:
        query = query.filter_by(is_active=True)

    categories = query.order_by(ServiceCategory.sort_order.asc(), ServiceCategory.id.asc()).all()
    return jsonify({
        "success": True,
        "categories": [c.to_dict(include_services=include_services) for c in categories]
    })


@service_packages_bp.route('/categories/<identifier>', methods=['GET'])
def get_category_detail(identifier):
    category = _find_category(identifier)
    if not category:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "تصنيف الخدمة غير موجود"}}), 404
    return jsonify({"success": True, "category": category.to_dict(include_services=True)})


@service_packages_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    name_ar = data.get('name_ar', '').strip()
    slug = data.get('slug', '').strip().lower()

    if not name or not name_ar or not slug:
        return jsonify({"success": False, "error": {"code": "INVALID_FIELDS", "message": "اسم التصنيف بالعربية والإنجليزية والرابط التعريفي مطلوبة."}}), 400

    existing = ServiceCategory.query.filter_by(slug=slug).first()
    if existing:
        return jsonify({"success": False, "error": {"code": "SLUG_EXISTS", "message": "الرابط التعريفي للتصنيف مستخدم مسبقاً."}}), 400

    cat = ServiceCategory(
        name=name,
        name_ar=name_ar,
        slug=slug,
        description=data.get('description'),
        icon=data.get('icon', 'palette'),
        sort_order=int(data.get('sort_order', 0)),
        is_active=bool(data.get('is_active', True))
    )
    db.session.add(cat)
    db.session.commit()
    return jsonify({"success": True, "category": cat.to_dict()}), 201


@service_packages_bp.route('/categories/<identifier>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_category(identifier):
    category = _find_category(identifier)
    if not category:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "تصنيف الخدمة غير موجود"}}), 404

    data = request.get_json() or {}
    if 'name' in data:
        category.name = data['name'].strip()
    if 'name_ar' in data:
        category.name_ar = data['name_ar'].strip()
    if 'slug' in data:
        new_slug = data['slug'].strip().lower()
        if new_slug != category.slug:
            existing = ServiceCategory.query.filter_by(slug=new_slug).first()
            if existing:
                return jsonify({"success": False, "error": {"code": "SLUG_EXISTS", "message": "الرابط التعريفي مستخدم مسبقاً."}}), 400
            category.slug = new_slug
    if 'description' in data:
        category.description = data['description']
    if 'icon' in data:
        category.icon = data['icon']
    if 'sort_order' in data:
        category.sort_order = int(data['sort_order'])
    if 'is_active' in data:
        category.is_active = bool(data['is_active'])

    db.session.commit()
    return jsonify({"success": True, "category": category.to_dict()})


@service_packages_bp.route('/categories/<identifier>', methods=['DELETE'])
@jwt_required()
def delete_category(identifier):
    category = _find_category(identifier)
    if not category:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "تصنيف الخدمة غير موجود"}}), 404

    db.session.delete(category)
    db.session.commit()
    return jsonify({"success": True, "message": "تم حذف تصنيف الخدمة بنجاح."})


# ==========================================
# Service Packages / Services Endpoints
# ==========================================

def _find_package(identifier):
    if str(identifier).isdigit():
        pkg = db.session.get(ServicePackage, int(identifier))
        if pkg:
            return pkg
    return ServicePackage.query.filter_by(slug=str(identifier).lower()).first()


@service_packages_bp.route('', methods=['GET'])
def get_packages():
    """List services / packages with optional filtering by category or active status."""
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    category_param = request.args.get('category')
    search = request.args.get('search', '').strip()

    query = ServicePackage.query
    if active_only:
        query = query.filter_by(is_active=True)

    if category_param:
        if str(category_param).isdigit():
            query = query.filter(ServicePackage.category_id == int(category_param))
        else:
            cat = ServiceCategory.query.filter_by(slug=category_param.lower()).first()
            if cat:
                query = query.filter((ServicePackage.category_id == cat.id) | (ServicePackage.category_slug == cat.slug))
            else:
                query = query.filter(ServicePackage.category_slug == category_param.lower())

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                ServicePackage.name.ilike(pattern),
                ServicePackage.name_ar.ilike(pattern),
                ServicePackage.description.ilike(pattern)
            )
        )

    packages = query.order_by(ServicePackage.id.asc()).all()
    return jsonify({
        "success": True,
        "packages": [p.to_dict() for p in packages]
    })


@service_packages_bp.route('/<identifier>', methods=['GET'])
@service_packages_bp.route('/slug/<identifier>', methods=['GET'])
def get_package_detail(identifier):
    package = _find_package(identifier)
    if not package:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "باقة الخدمة غير موجودة"}}), 404
    return jsonify({"success": True, "package": package.to_dict()})


@service_packages_bp.route('', methods=['POST'])
@jwt_required()
def create_package():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    name_ar = data.get('name_ar', '').strip()
    slug = data.get('slug', '').strip().lower()

    if not name or not name_ar or not slug:
        return jsonify({"success": False, "error": {"code": "INVALID_FIELDS", "message": "اسم الباقة والاسم بالعربي والرابط التعريفي مطلوبة."}}), 400

    existing = ServicePackage.query.filter_by(slug=slug).first()
    if existing:
        return jsonify({"success": False, "error": {"code": "SLUG_EXISTS", "message": "الرابط التعريفي للباقة مستخدم مسبقاً."}}), 400

    category_id = data.get('category_id')
    category_slug = data.get('category_slug')
    if category_id and not category_slug:
        cat = db.session.get(ServiceCategory, int(category_id))
        if cat:
            category_slug = cat.slug
    elif category_slug and not category_id:
        cat = ServiceCategory.query.filter_by(slug=category_slug.lower()).first()
        if cat:
            category_id = cat.id

    pricing_type = data.get('pricing_type', 'quotation_required')
    fixed_price = float(data.get('fixed_price')) if data.get('fixed_price') not in (None, '') else None
    starting_price = float(data.get('starting_price')) if data.get('starting_price') not in (None, '') else None
    indicative_price_min = float(data.get('indicative_price_min')) if data.get('indicative_price_min') not in (None, '') else None
    indicative_price_max = float(data.get('indicative_price_max')) if data.get('indicative_price_max') not in (None, '') else None
    quotation_required = bool(data.get('quotation_required', False) or pricing_type == 'quotation_required')

    pkg = ServicePackage(
        category_id=category_id,
        category_slug=category_slug,
        name=name,
        name_ar=name_ar,
        slug=slug,
        description=data.get('description'),
        target_audience=data.get('target_audience'),
        pricing_type=pricing_type,
        fixed_price=fixed_price,
        starting_price=starting_price,
        indicative_price_min=indicative_price_min,
        indicative_price_max=indicative_price_max,
        indicative_price_text=data.get('indicative_price_text'),
        quotation_required=quotation_required,
        pricing_notes=data.get('pricing_notes'),
        delivery_estimate=data.get('delivery_estimate'),
        requirements_text=data.get('requirements_text'),
        currency=data.get('currency', 'EGP'),
        is_approved=bool(data.get('is_approved', False)),
        is_popular=bool(data.get('is_popular', False)),
        is_active=bool(data.get('is_active', True)),
        support_period=data.get('support_period')
    )
    if 'features' in data:
        pkg.features = data['features']
    if 'example_images' in data:
        pkg.example_images = data['example_images']

    db.session.add(pkg)
    db.session.commit()
    return jsonify({"success": True, "package": pkg.to_dict()}), 201


@service_packages_bp.route('/<identifier>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_package(identifier):
    package = _find_package(identifier)
    if not package:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "باقة الخدمة غير موجودة"}}), 404

    data = request.get_json() or {}
    if 'name' in data:
        package.name = data['name'].strip()
    if 'name_ar' in data:
        package.name_ar = data['name_ar'].strip()
    if 'slug' in data:
        new_slug = data['slug'].strip().lower()
        if new_slug != package.slug:
            existing = ServicePackage.query.filter_by(slug=new_slug).first()
            if existing:
                return jsonify({"success": False, "error": {"code": "SLUG_EXISTS", "message": "الرابط التعريفي مستخدم مسبقاً."}}), 400
            package.slug = new_slug
    if 'category_id' in data:
        package.category_id = int(data['category_id']) if data['category_id'] else None
        if package.category_id:
            cat = db.session.get(ServiceCategory, package.category_id)
            if cat:
                package.category_slug = cat.slug
    if 'category_slug' in data:
        package.category_slug = data['category_slug']
    if 'description' in data:
        package.description = data['description']
    if 'target_audience' in data:
        package.target_audience = data['target_audience']
    if 'pricing_type' in data:
        package.pricing_type = data['pricing_type']
    if 'fixed_price' in data:
        package.fixed_price = float(data['fixed_price']) if data['fixed_price'] not in (None, '') else None
    if 'starting_price' in data:
        package.starting_price = float(data['starting_price']) if data['starting_price'] not in (None, '') else None
    if 'indicative_price_min' in data:
        package.indicative_price_min = float(data['indicative_price_min']) if data['indicative_price_min'] not in (None, '') else None
    if 'indicative_price_max' in data:
        package.indicative_price_max = float(data['indicative_price_max']) if data['indicative_price_max'] not in (None, '') else None
    if 'indicative_price_text' in data:
        package.indicative_price_text = data['indicative_price_text']
    if 'quotation_required' in data:
        package.quotation_required = bool(data['quotation_required'])
    if 'pricing_notes' in data:
        package.pricing_notes = data['pricing_notes']
    if 'delivery_estimate' in data:
        package.delivery_estimate = data['delivery_estimate']
    if 'requirements_text' in data:
        package.requirements_text = data['requirements_text']
    if 'currency' in data:
        package.currency = data['currency']
    if 'is_approved' in data:
        package.is_approved = bool(data['is_approved'])
    if 'is_popular' in data:
        package.is_popular = bool(data['is_popular'])
    if 'is_active' in data:
        package.is_active = bool(data['is_active'])
    if 'support_period' in data:
        package.support_period = data['support_period']
    if 'features' in data:
        package.features = data['features']
    if 'example_images' in data:
        package.example_images = data['example_images']

    db.session.commit()
    return jsonify({"success": True, "package": package.to_dict()})


@service_packages_bp.route('/<identifier>', methods=['DELETE'])
@jwt_required()
def delete_package(identifier):
    package = _find_package(identifier)
    if not package:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "باقة الخدمة غير موجودة"}}), 404

    db.session.delete(package)
    db.session.commit()
    return jsonify({"success": True, "message": "تم حذف باقة الخدمة بنجاح."})
