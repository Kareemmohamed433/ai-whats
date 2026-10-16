from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User
from app.extensions import db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({
            "success": False,
            "error": {"code": "INVALID_REQUEST", "message": "البريد الإلكتروني وكلمة المرور مطلوبة."}
        }), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({
            "success": False,
            "error": {"code": "AUTH_FAILED", "message": "بيانات الدخول غير صحيحة."}
        }), 401

    token = create_access_token(identity=str(user.id))
    now = datetime.utcnow()
    user.status = 'online'
    user.last_login_at = now
    user.last_seen_at = now
    db.session.commit()

    return jsonify({
        "success": True,
        "token": token,
        "user": user.to_dict()
    })

@auth_bp.route('/heartbeat', methods=['POST', 'PUT'])
@jwt_required()
def heartbeat():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if user:
        user.last_seen_at = datetime.utcnow()
        if user.status == 'offline':
            user.status = 'online'
        db.session.commit()
        return jsonify({"success": True, "status": user.status, "last_seen_at": user.last_seen_at.isoformat()})
    return jsonify({"success": False, "error": {"code": "USER_NOT_FOUND", "message": "المستخدم غير موجود."}}), 404

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({
            "success": False,
            "error": {"code": "USER_NOT_FOUND", "message": "المستخدم غير موجود."}
        }), 404

    user.last_seen_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "success": True,
        "user": user.to_dict()
    })

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if user:
        user.status = 'offline'
        db.session.commit()

    return jsonify({"success": True, "message": "تم تسجيل الخروج بنجاح."})
