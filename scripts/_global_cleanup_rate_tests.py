"""Global cleanup of rate_category_tests:
- remove rows whose test is a panel child
- remove duplicate rows per rate list
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests.models import (RateCategory, RateCategoryTest,
                                  PanelParameter)
from sqlalchemy import text

def run():
    app = create_app()
    with app.app_context():
        # 1) child-only rows
        child_ids = {r[0] for r in db.session.query(PanelParameter.test_id).distinct().all()}
        n_child = (RateCategoryTest.query
                   .filter(RateCategoryTest.test_id.in_(child_ids))
                   .delete(synchronize_session=False))
        print(f"removed {n_child} child-only test links")

        # 2) duplicates per rate list
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
