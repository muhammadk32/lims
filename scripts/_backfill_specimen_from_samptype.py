"""Backfill Test.specimen_id by matching sample_type to Specimen.name (fuzzy)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests.models import Test, Specimen

def norm(s):
    if not s: return ''
    return s.lower().replace('_',' ').replace('-',' ').strip()

def run():
    app = create_app()
    with app.app_context():
        specs = [(s.id, norm(s.name)) for s in Specimen.query.all()]
        n_matched = 0
        for t in Test.query.filter(Test.specimen_id.is_(None)).all():
            st = norm(t.sample_type)
            if not st: continue
            # exact match first
            for sid, sname in specs:
                if sname == st:
                    t.specimen_id = sid
                    n_matched += 1
                    break
            else:
                # partial: specimen name contained in sample_type
                for sid, sname in specs:
                    if sname and sname in st:
                        t.specimen_id = sid
                        n_matched += 1
                        break
        db.session.commit()
        print(f"backfilled {n_matched} specimen links")

if __name__ == "__main__":
    run()
