"""Purge junk tests from every rate list:
- ** prefixed names
- <Type> and empty
- price=0 + no children + no category (safely unbillable)
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests.models import (RateCategory, RateCategoryTest,
                                  Test, PanelParameter)

def run():
    app = create_app()
    with app.app_context():
        # parent ids (has children in panel_parameters)
        parent_ids = {r[0] for r in
                      db.session.query(PanelParameter.panel_id).distinct().all()}

        total_removed = 0
        for rc in RateCategory.query.all():
            # fetch all tests in this rate list
            rcts = RateCategoryTest.query.filter_by(rate_category_id=rc.id).all()
            removed = 0
            for rct in rcts:
                t = Test.query.get(rct.test_id)
                if not t:
                    db.session.delete(rct)
                    removed += 1
                    continue
                name = (t.name or '').strip()
                junk = (
                    name.startswith('**') or
                    name in ('<Type>', '',) or
                    (name.lower().startswith('type>'))
                )
                if junk and t.id not in parent_ids:
                    db.session.delete(rct)
                    removed += 1
            if removed:
                print(f"  {rc.name}: removed {removed}")
                total_removed += removed
        db.session.commit()
        print(f"\ntotal removed across all rate lists: {total_removed}")

        print("\nFinal counts:")
        for rc in RateCategory.query.all():
            n = RateCategoryTest.query.filter_by(rate_category_id=rc.id).count()
            print(f"  {rc.name}: {n}")

if __name__ == "__main__":
    run()
