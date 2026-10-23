"""Purge ALL ** junk from rate lists regardless of children."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests.models import (RateCategory, RateCategoryTest, Test)

def run():
    app = create_app()
    with app.app_context():
        total_removed = 0
        for rc in RateCategory.query.all():
            rcts = RateCategoryTest.query.filter_by(rate_category_id=rc.id).all()
            removed = 0
            for rct in rcts:
                t = Test.query.get(rct.test_id)
                if not t: 
                    continue
                name = (t.name or '').strip()
                if name.startswith('**') or name in ('<Type>', ''):
                    db.session.delete(rct)
                    removed += 1
            if removed:
                print(f"  {rc.name}: removed {removed}")
                total_removed += removed
        db.session.commit()
        print(f"\ntotal removed: {total_removed}")

        print("\nFinal counts:")
        for rc in RateCategory.query.all():
            n = RateCategoryTest.query.filter_by(rate_category_id=rc.id).count()
            print(f"  {rc.name}: {n}")

if __name__ == "__main__":
    run()
