"""Backfill Test.specimen_id from labtestdetail.Specimencode."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from app import create_app
from extensions import db
from modules.tests import models as M

DATA = os.path.join(HERE, "adamlab_import")
def load(n):
    with open(os.path.join(DATA, n+".json"),"r",encoding="utf-8") as f: return json.load(f)
def i(v):
    try: return int(v)
    except (TypeError, ValueError): return None

def run():
    app = create_app()
    with app.app_context():
        spec_by_code = {s.code: s for s in M.Specimen.query.all() if s.code is not None}
        lt = load("labtestdetail")
        linked = miss_spec = miss_test = already = 0
        for r in lt:
            aid = i(r.get("testcode"))
            scode = i(r.get("Specimencode"))
            if aid is None: continue
            t = M.Test.query.filter_by(adamlab_id=aid).first()
            if not t:
                miss_test += 1; continue
            if t.specimen_id:
                already += 1; continue
            if scode is None: continue
            s = spec_by_code.get(scode)
            if not s:
                miss_spec += 1; continue
            t.specimen_id = s.id
            linked += 1
        db.session.commit()
        print(f"linked: {linked}")
        print(f"already linked: {already}")
        print(f"missing specimen code: {miss_spec}")
        print(f"missing test: {miss_test}")
        total = M.Test.query.filter(M.Test.specimen_id.isnot(None)).count()
        print(f"total tests with specimen_id: {total}")

if __name__ == "__main__":
    run()
