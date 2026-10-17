from app.routes.auth import auth_bp
from app.routes.users import users_bp, agents_bp
from app.routes.customers import customers_bp
from app.routes.conversations import conversations_bp
from app.routes.messages import messages_bp
from app.routes.products import products_bp
from app.routes.service_packages import service_packages_bp
from app.routes.leads import leads_bp
from app.routes.orders import orders_bp
from app.routes.knowledge import knowledge_bp
from app.routes.analytics import analytics_bp
from app.routes.payment_reviews import payment_reviews_bp
from app.routes.quick_replies import quick_replies_bp
from app.routes.integrations import integrations_bp
from app.routes.settings import settings_bp
from app.routes.webhooks import webhooks_bp, telegram_api_bp
from app.routes.push_notifications import notifications_bp, push_alias_bp


def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(agents_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(conversations_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(service_packages_bp)
    app.register_blueprint(leads_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(payment_reviews_bp)
    app.register_blueprint(quick_replies_bp)
    app.register_blueprint(integrations_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(webhooks_bp)
    app.register_blueprint(telegram_api_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(push_alias_bp)
