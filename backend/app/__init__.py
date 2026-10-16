import os
from flask import Flask
from app.config import Config
from app.extensions import db, jwt, cors, socketio, migrate
from app.routes import register_routes
from app.utils.seed import seed_database

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    socketio.init_app(app, cors_allowed_origins="*")
    migrate.init_app(app, db)

    # Register API routes
    register_routes(app)

    # Auto create tables & seed initial data in development/SQLite
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
            seed_database()
        except Exception as e:
            print(f"DB Init Warning: {e}")

    return app
