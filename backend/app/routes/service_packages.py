from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import ServicePackage
from app.extensions import db

service_packages_bp = Blueprint('service_packages', __name__, url_prefix='/api/packages')


@service_packages_bp.route('', methods=['GET'])
def get_packages():
    """List service packages (Starter, Business, Enterprise)."""
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    query = ServicePackage.query
    if active_only:
        query = query.filter_by(is_active=True)

    packages = query.order_by(ServicePackage.id.asc()).all()
    return jsonify({
        "success": True,
        "packages": [p.to_dict() for p in packages]
    })


def _find_package(identifier):
    if str(identifier).isdigit():
        pkg = db.session.get(ServicePackage, int(identifier))
        if pkg:
            return pkg
    return ServicePackage.query.filter_by(slug=str(identifier).lower()).first()


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

    pkg = ServicePackage(
        name=name,
        name_ar=name_ar,
        slug=slug,
        description=data.get('description'),
        target_audience=data.get('target_audience'),
        indicative_price_min=float(data.get('indicative_price_min')) if data.get('indicative_price_min') is not None else None,
        indicative_price_max=float(data.get('indicative_price_max')) if data.get('indicative_price_max') is not None else None,
        indicative_price_text=data.get('indicative_price_text'),
        currency=data.get('currency', 'EGP'),
        is_approved=bool(data.get('is_approved', False)),
        is_popular=bool(data.get('is_popular', False)),
        is_active=bool(data.get('is_active', True)),
        support_period=data.get('support_period')
    )
    if 'features' in data:
        pkg.features = data['features']

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
    if 'description' in data:
        package.description = data['description']
    if 'target_audience' in data:
        package.target_audience = data['target_audience']
    if 'indicative_price_min' in data:
        package.indicative_price_min = float(data['indicative_price_min']) if data['indicative_price_min'] is not None else None
    if 'indicative_price_max' in data:
        package.indicative_price_max = float(data['indicative_price_max']) if data['indicative_price_max'] is not None else None
    if 'indicative_price_text' in data:
        package.indicative_price_text = data['indicative_price_text']
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
