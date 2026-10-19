"""Remove imported AdamLab rate categories; create one Standard Rate List
   populated with all active tests (excluding child-only)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests import models as M
from sqlalchemy import exists

def run():
    app = create_app()
    with app.app_context():
        # 1) delete all existing categories + their rates + test links
        n_cats = M.RateCategory.query.count()
        for c in M.RateCategory.query.all():
            db.session.delete(c)
        db.session.commit()
        print(f"deleted {n_cats} rate categories (cascades rates + test links)")

        # 2) create the standard category
        std = M.RateCategory(
            code=1,
            name="Standard Rate List",
            description="Default price list — all catalog tests",
            rate_type="rate",
            is_active=True,
        )
        db.session.add(std)
        db.session.flush()
        # default rate row: section 1, 0% rate, 0% commission
        db.session.add(M.RateCategoryRate(
            rate_category_id=std.id,
            section_code=1,
            rate_percent=0,
            commission=0,
        ))
        db.session.flush()

        # 3) link all active tests that are NOT child-only
        from modules.tests.models import PanelParameter
        child_ids = {row[0] for row in
                     db.session.query(PanelParameter.test_id).distinct().all()}
        q = M.Test.query.filter(M.Test.is_active == True)  # noqa: E712
        if child_ids:
            q = q.filter(~M.Test.id.in_(child_ids))
        tests = q.order_by(M.Test.code.asc()).all()
        for idx, t in enumerate(tests, start=1):
            db.session.add(M.RateCategoryTest(
                rate_category_id=std.id,
                test_id=t.id,
                sort_order=idx,
            ))
        db.session.commit()
        print(f"created 'Standard Rate List' (id={std.id}) with {len(tests)} tests")

        # 4) attach as default for every lab
        from modules.laboratories.models import Laboratory
        n_labs = 0
        for lab in Laboratory.query.all():
            if not lab.rate_category_id:
                lab.rate_category_id = std.id
                n_labs += 1
        db.session.commit()
        print(f"attached Standard Rate List to {n_labs} labs")

if __name__ == "__main__":
    run()
