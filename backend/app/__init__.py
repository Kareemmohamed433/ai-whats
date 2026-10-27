import os
from flask import Flask
from app.config import Config
from app.extensions import db, jwt, cors, socketio, migrate
from app.routes import register_routes
from app.utils.seed import seed_database
import app.models

def create_app(config_class=Config, test_config=None):
    app = Flask(__name__)
    app.config.from_object(config_class)
    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    socketio.init_app(app, cors_allowed_origins="*")
    migrate.init_app(app, db)

    # Register API routes
    register_routes(app)

    # Auto create tables & seed initial data in development/SQLite
    if not app.config.get("TESTING"):
        with app.app_context():
            try:
                db.create_all()
                # Ensure new columns exist in users table if DB exists
                with db.engine.connect() as conn:
                    from sqlalchemy import text
                    try:
                        conn.execute(text("ALTER TABLE users ADD COLUMN last_login_at DATETIME;"))
                        conn.commit()
                    except Exception:
                        pass
                    try:
                        conn.execute(text("ALTER TABLE users ADD COLUMN last_seen_at DATETIME;"))
                        conn.commit()
                    except Exception:
                        pass
                    try:
                        conn.execute(text("ALTER TABLE store_settings ADD COLUMN portfolio_url VARCHAR(255);"))
                        conn.commit()
                    except Exception:
                        pass
                    # Safe column additions for service_packages
                    for col_sql in [
                        "ALTER TABLE service_packages ADD COLUMN category_id INTEGER;",
                        "ALTER TABLE service_packages ADD COLUMN category_slug VARCHAR(100);",
                        "ALTER TABLE service_packages ADD COLUMN pricing_type VARCHAR(30) DEFAULT 'quotation_required';",
                        "ALTER TABLE service_packages ADD COLUMN fixed_price FLOAT;",
                        "ALTER TABLE service_packages ADD COLUMN starting_price FLOAT;",
                        "ALTER TABLE service_packages ADD COLUMN quotation_required BOOLEAN DEFAULT 0;",
                        "ALTER TABLE service_packages ADD COLUMN pricing_notes TEXT;",
                        "ALTER TABLE service_packages ADD COLUMN delivery_estimate VARCHAR(100);",
                        "ALTER TABLE service_packages ADD COLUMN requirements_text TEXT;",
                        "ALTER TABLE service_packages ADD COLUMN example_images_json TEXT;",
                        # Safe column additions for message_attachments
                        "ALTER TABLE message_attachments ADD COLUMN conversation_id INTEGER;",
                        "ALTER TABLE message_attachments ADD COLUMN storage_key VARCHAR(255);",
                        "ALTER TABLE message_attachments ADD COLUMN mime_type VARCHAR(100);",
                        "ALTER TABLE message_attachments ADD COLUMN direction VARCHAR(20) DEFAULT 'inbound';",
                        "ALTER TABLE message_attachments ADD COLUMN provider_media_id VARCHAR(150);",
                        "ALTER TABLE message_attachments ADD COLUMN status VARCHAR(20) DEFAULT 'completed';",
                        "ALTER TABLE message_attachments ADD COLUMN created_at DATETIME;"
                    ]:
                        try:
                            conn.execute(text(col_sql))
                            conn.commit()
                        except Exception:
                            pass

                seed_database()
            except Exception as e:
                print(f"DB Init Warning: {e}")

    return app
