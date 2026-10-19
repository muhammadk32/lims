"""Wipe RateCategoryTest/RateRate links for cat 1, then rebuild clean."""
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
        # 1) Nuke ALL existing RateCategoryTest + RateCategoryRate for cat 1
        cat = M.RateCategory.query.filter_by(name='Standard Rate List').first()
        if not cat:
            print("Standard Rate List not found"); return
        n_del = (M.RateCategoryTest.query
                 .filter_by(rate_category_id=cat.id).delete(synchronize_session=False))
        n_del_r = (M.RateCategoryRate.query
                   .filter_by(rate_category_id=cat.id).delete(synchronize_session=False))
        db.session.commit()
        print(f"deleted {n_del} test links, {n_del_r} rate rows from cat {cat.id}")

        # 2) Rebuild rate row
        db.session.add(M.RateCategoryRate(
            rate_category_id=cat.id,
            section_code=1,
            rate_percent=0,
            commission=0,
        ))
        db.session.flush()

        # 3) Rebuild test links — strictly active, non-child
        child_ids = {row[0] for row in
                     db.session.query(M.PanelParameter.test_id).distinct().all()}
        q = M.Test.query.filter(M.Test.is_active == True)  # noqa: E712
        if child_ids:
            q = q.filter(~M.Test.id.in_(child_ids))
        tests = q.order_by(M.Test.code.asc()).all()
        seen = set()
        added = 0
        for idx, t in enumerate(tests, start=1):
            if t.id in seen: continue
            seen.add(t.id)
            db.session.add(M.RateCategoryTest(
                rate_category_id=cat.id,
                test_id=t.id,
                sort_order=idx,
            ))
            added += 1
        db.session.commit()
        print(f"rebuilt: {added} tests linked to Standard Rate List")

        # 4) final verify
        print("verify rows:", M.RateCategoryTest.query.filter_by(rate_category_id=cat.id).count())
        print("verify distinct:",
              db.session.query(M.RateCategoryTest.test_id)
              .filter_by(rate_category_id=cat.id).distinct().count())

if __name__ == "__main__":
    run()
