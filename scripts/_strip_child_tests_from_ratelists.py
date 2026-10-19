"""Strip child-only tests from all rate lists."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests import models as M

def run():
    app = create_app()
    with app.app_context():
        # IDs of tests that are children of any panel
        child_ids = {r[0] for r in
                     db.session.query(M.PanelParameter.test_id).distinct().all()}
        print(f"child-only test ids: {len(child_ids)}")

        # delete links pointing at child tests, per rate category
        total_deleted = 0
        for rc in M.RateCategory.query.all():
            n = (M.RateCategoryTest.query
                 .filter_by(rate_category_id=rc.id)
                 .filter(M.RateCategoryTest.test_id.in_(child_ids))
                 .delete(synchronize_session=False))
            print(f"  {rc.name}: removed {n} child links")
            total_deleted += n
        db.session.commit()

        # final counts
        print("\nFinal counts:")
        for rc in M.RateCategory.query.all():
            n = M.RateCategoryTest.query.filter_by(rate_category_id=rc.id).count()
            print(f"  {rc.name}: {n}")

if __name__ == "__main__":
    run()
