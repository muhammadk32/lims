"""One-shot: make every non-standard rate list identical to Standard."""
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
        std = RateCategory.query.filter_by(name='Standard Rate List').first()
        if not std:
            print("Standard missing"); return

        # canonical set: Standard's tests, excluding panel children
        child_ids = {r[0] for r in db.session.query(PanelParameter.test_id).distinct().all()}
        std_ids = {r[0] for r in db.session.query(RateCategoryTest.test_id)
                   .filter_by(rate_category_id=std.id).all()} - child_ids
        print(f"canonical set: {len(std_ids)}")

        # drop child-only from Standard too
        if child_ids:
            n = (RateCategoryTest.query.filter_by(rate_category_id=std.id)
                 .filter(RateCategoryTest.test_id.in_(child_ids))
                 .delete(synchronize_session=False))
            if n: print(f"Standard: removed {n} child-only")

        # for every other list: wipe + rebuild to canonical
        for cat in RateCategory.query.all():
            if cat.id == std.id: continue
            RateCategoryTest.query.filter_by(rate_category_id=cat.id).delete(synchronize_session=False)
            for i, tid in enumerate(sorted(std_ids), start=1):
                db.session.add(RateCategoryTest(
                    rate_category_id=cat.id, test_id=tid, sort_order=i))
            print(f"  {cat.name}: rebuilt → {len(std_ids)}")
        db.session.commit()

        print("\nFinal counts:")
        for cat in RateCategory.query.all():
            n = RateCategoryTest.query.filter_by(rate_category_id=cat.id).count()
            print(f"  {cat.name}: {n}")

if __name__ == "__main__":
    run()
