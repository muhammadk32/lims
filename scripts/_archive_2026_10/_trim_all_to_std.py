"""Trim every non-standard rate list to exactly match Standard's test set."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests.models import RateCategory, RateCategoryTest

def run():
    app = create_app()
    with app.app_context():
        std = RateCategory.query.filter_by(name='Standard Rate List').first()
        if not std:
            print("Standard missing"); return
        std_ids = {r[0] for r in db.session.query(RateCategoryTest.test_id)
                   .filter_by(rate_category_id=std.id).all()}
        print(f"Standard canonical: {len(std_ids)}")

        for cat in RateCategory.query.all():
            if cat.id == std.id: continue
            current = {r[0] for r in db.session.query(RateCategoryTest.test_id)
                       .filter_by(rate_category_id=cat.id).all()}
            extra = current - std_ids
            if extra:
                n = (RateCategoryTest.query
                     .filter_by(rate_category_id=cat.id)
                     .filter(RateCategoryTest.test_id.in_(extra))
                     .delete(synchronize_session=False))
                print(f"  {cat.name}: removed {n} extras")
            else:
                print(f"  {cat.name}: OK")
        db.session.commit()

        print("\nFinal:")
        for cat in RateCategory.query.all():
            n = RateCategoryTest.query.filter_by(rate_category_id=cat.id).count()
            print(f"  {cat.name}: {n}")

if __name__ == "__main__":
    run()
