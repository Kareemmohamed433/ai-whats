import os
import shutil
from datetime import datetime
from sqlalchemy import text
from app import create_app
from app.extensions import db
from app.utils.seed import seed_database
from app.models import Product, FAQ, Category, ServicePackage, CompanySettings, Lead


def run_migration():
    """
    Safe migration from Khaam Sinai to NEXORA Software Solutions.
    - Creates backup of the database
    - Ensures new tables and columns exist
    - Migrates settings and seeds NEXORA packages, FAQs, and quick replies
    - Deactivates old physical products and FAQs
    """
    app = create_app()
    with app.app_context():
        # 1. Backup local SQLite database if it exists
        db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        if "sqlite:///" in db_uri:
            db_path = db_uri.replace("sqlite:///", "")
            if os.path.exists(db_path):
                backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                try:
                    shutil.copy2(db_path, backup_path)
                    print(f"[OK] Local database backup created at: {backup_path}")
                except Exception as e:
                    print(f"[WARN] Could not create backup: {e}")

        # 2. Ensure schema tables and columns are created
        db.create_all()
        with db.engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE store_settings ADD COLUMN portfolio_url VARCHAR(255);"))
                conn.commit()
            except Exception:
                pass
        print("[OK] Schema tables and columns verified/created.")

        # 3. Deactivate old physical products and categories
        old_prods = Product.query.filter(
            Product.sku.ilike("KS-%") |
            Product.name.ilike("%زيت%") |
            Product.name.ilike("%عسل%") |
            Product.name.ilike("%مرمية%")
        ).all()
        deactivated_count = 0
        for p in old_prods:
            p.is_active = False
            deactivated_count += 1

        old_faqs = FAQ.query.filter(
            FAQ.question.ilike("%زيت%") |
            FAQ.question.ilike("%شحن%") |
            FAQ.answer.ilike("%زيت الزيتون%") |
            FAQ.answer.ilike("%خام سينا%")
        ).all()
        for f in old_faqs:
            f.is_active = False

        db.session.commit()
        print(f"[OK] Old physical products ({deactivated_count}) and FAQs deactivated from active queries.")

        # 4. Run idempotent seed to populate NEXORA data
        seed_database()
        print("[OK] NEXORA seed data applied successfully.")

        # 5. Verification summary
        active_pkgs = ServicePackage.query.filter_by(is_active=True).count()
        active_faqs = FAQ.query.filter_by(is_active=True).count()
        active_products = Product.query.filter_by(is_active=True).count()
        company = CompanySettings.query.first()

        print("\n--- Migration Verification Summary ---")
        print(f"Company: {company.company_name if company else 'N/A'}")
        print(f"Portfolio URL: {company.portfolio_url if company else 'N/A'}")
        print(f"Active Service Packages: {active_pkgs}")
        print(f"Active FAQs: {active_faqs}")
        print(f"Active Physical Products: {active_products}")
        assert active_products == 0, f"Error: {active_products} active old products still remain!"
        print("[SUCCESS] Migration to NEXORA Software Solutions completed successfully!")


if __name__ == '__main__':
    run_migration()
