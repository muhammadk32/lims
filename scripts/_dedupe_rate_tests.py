"""Dedupe rate_category_tests across all rate lists (SQLAlchemy 2)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests.models import RateCategory, RateCategoryTest
from sqlalchemy import text

def run():
    app = create_app()
    with app.app_context():
        dups = db.session.execute(text("""
            SELECT rate_category_id, test_id, COUNT(*) AS n, MIN(id) AS keep_id
            FROM rate_category_tests
            GROUP BY rate_category_id, test_id
            HAVING COUNT(*) > 1
        """)).fetchall()
        print(f"duplicates found: {len(dups)}")
        for rc_id, tid, n, keep_id in dups:
            db.session.execute(text("""
                DELETE FROM rate_category_tests
                WHERE rate_category_id=:rc AND test_id=:t AND id != :k
            """), {"rc": rc_id, "t": tid, "k": keep_id})
        db.session.commit()

        print("\nFinal counts:")
        for cat in RateCategory.query.all():
            n = RateCategoryTest.query.filter_by(rate_category_id=cat.id).count()
            print(f"  {cat.name}: {n}")

if __name__ == "__main__":
    run()
