"""Seed RateCategoryDeptRate for every (rate list, department)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests import models as M

def run():
    app = create_app()
    with app.app_context():
        cats = M.RateCategory.query.all()
        depts = M.TestCategory.query.order_by(M.TestCategory.name.asc()).all()
        n = 0
        for rc in cats:
            for d in depts:
                exists = M.RateCategoryDeptRate.query.filter_by(
                    rate_category_id=rc.id, department_id=d.id).first()
                if exists: continue
                db.session.add(M.RateCategoryDeptRate(
                    rate_category_id=rc.id, department_id=d.id,
                    discount_percent=0, commission_percent=0,
                ))
                n += 1
        db.session.commit()
        print(f"seeded {n} dept-rate rows")
        print(f"total now: {M.RateCategoryDeptRate.query.count()}")

if __name__ == "__main__":
    run()
