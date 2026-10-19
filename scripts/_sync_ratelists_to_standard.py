"""Make every lab rate list mirror Standard exactly (785 tests)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests.models import RateCategory, RateCategoryTest

def run():
    app = create_app()
    with app.app_context():
        std = RateCategory.query.filter_by(is_standard=True).first() \
              or RateCategory.query.filter_by(name='Standard Rate List').first()
        if not std:
            print("Standard Rate List not found"); return

        std_ids = {r[0] for r in db.session.query(RateCategoryTest.test_id)
                   .filter_by(rate_category_id=std.id).all()}
        print(f"Standard has {len(std_ids)} tests")

        for cat in RateCategory.query.all():
            if cat.id == std.id: continue
            current = {r[0] for r in db.session.query(RateCategoryTest.test_id)
                       .filter_by(rate_category_id=cat.id).all()}
            extra = current - std_ids
            missing = std_ids - current
            if not extra and not missing:
                print(f"  {cat.name}: OK ({len(current)})")
                continue
            # remove extra
            if extra:
                n = (RateCategoryTest.query
                     .filter_by(rate_category_id=cat.id)
                     .filter(RateCategoryTest.test_id.in_(extra))
                     .delete(synchronize_session=False))
                print(f"  {cat.name}: removed {n} extra")
            # add missing
            if missing:
                so = (RateCategoryTest.query.filter_by(rate_category_id=cat.id).count() + 1)
                for tid in missing:
                    db.session.add(RateCategoryTest(
                        rate_category_id=cat.id, test_id=tid, sort_order=so))
                    so += 1
                print(f"  {cat.name}: added {len(missing)} missing")
        db.session.commit()

        print("\nFinal counts:")
        for cat in RateCategory.query.all():
            n = RateCategoryTest.query.filter_by(rate_category_id=cat.id).count()
            print(f"  {cat.name}: {n}")

if __name__ == "__main__":
    run()
