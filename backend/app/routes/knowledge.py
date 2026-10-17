from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import FAQ, KnowledgeBaseArticle
from app.extensions import db

knowledge_bp = Blueprint('knowledge', __name__, url_prefix='/api/knowledge')


# FAQs
@knowledge_bp.route('/faqs', methods=['GET'])
def get_faqs():
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    query = FAQ.query
    if active_only:
        query = query.filter_by(is_active=True)
    faqs = query.order_by(FAQ.id.asc()).all()
    return jsonify({
        "success": True,
        "faqs": [f.to_dict() for f in faqs]
    })


@knowledge_bp.route('/faqs', methods=['POST'])
@jwt_required()
def create_faq():
    data = request.get_json() or {}
    q = data.get('question', '').strip()
    a = data.get('answer', '').strip()
    cat = data.get('category', 'أسئلة شائعة')

    if not q or not a:
        return jsonify({"success": False, "error": {"code": "INVALID_FIELDS", "message": "السؤال والإجابة مطلوبة."}}), 400

    faq = FAQ(question=q, answer=a, category=cat, is_active=data.get('is_active', True))
    db.session.add(faq)
    db.session.commit()

    return jsonify({"success": True, "faq": faq.to_dict()}), 201


@knowledge_bp.route('/faqs/<int:faq_id>', methods=['PUT'])
@jwt_required()
def update_faq(faq_id):
    faq = db.session.get(FAQ, faq_id)
    if not faq:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "السؤال غير موجود"}}), 404

    data = request.get_json() or {}
    if 'question' in data:
        faq.question = data['question']
    if 'answer' in data:
        faq.answer = data['answer']
    if 'category' in data:
        faq.category = data['category']
    if 'is_active' in data:
        faq.is_active = bool(data['is_active'])

    db.session.commit()
    return jsonify({"success": True, "faq": faq.to_dict()})


@knowledge_bp.route('/faqs/<int:faq_id>', methods=['DELETE'])
@jwt_required()
def delete_faq(faq_id):
    faq = db.session.get(FAQ, faq_id)
    if not faq:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "السؤال غير موجود"}}), 404

    db.session.delete(faq)
    db.session.commit()
    return jsonify({"success": True, "message": "تم حذف السؤال الشائع بنجاح."})


# KB Articles
@knowledge_bp.route('/articles', methods=['GET'])
def get_articles():
    published_only = request.args.get('published_only', 'true').lower() == 'true'
    query = KnowledgeBaseArticle.query
    if published_only:
        query = query.filter_by(is_published=True)
    articles = query.order_by(KnowledgeBaseArticle.id.asc()).all()
    return jsonify({
        "success": True,
        "articles": [art.to_dict() for art in articles]
    })


@knowledge_bp.route('/articles', methods=['POST'])
@jwt_required()
def create_article():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()

    if not title or not content:
        return jsonify({"success": False, "error": {"code": "INVALID_FIELDS", "message": "العنوان والمحتوى مطلوبان."}}), 400

    article = KnowledgeBaseArticle(
        title=title,
        content=content,
        category=data.get('category', 'عام'),
        is_published=data.get('is_published', True)
    )
    db.session.add(article)
    db.session.commit()

    return jsonify({"success": True, "article": article.to_dict()}), 201


@knowledge_bp.route('/articles/<int:article_id>', methods=['PUT'])
@jwt_required()
def update_article(article_id):
    article = db.session.get(KnowledgeBaseArticle, article_id)
    if not article:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المقالة غير موجودة"}}), 404

    data = request.get_json() or {}
    if 'title' in data:
        article.title = data['title']
    if 'content' in data:
        article.content = data['content']
    if 'category' in data:
        article.category = data['category']
    if 'is_published' in data:
        article.is_published = bool(data['is_published'])

    db.session.commit()
    return jsonify({"success": True, "article": article.to_dict()})


@knowledge_bp.route('/articles/<int:article_id>', methods=['DELETE'])
@jwt_required()
def delete_article(article_id):
    article = db.session.get(KnowledgeBaseArticle, article_id)
    if not article:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "المقالة غير موجودة"}}), 404

    db.session.delete(article)
    db.session.commit()
    return jsonify({"success": True, "message": "تم حذف المقالة بنجاح."})
