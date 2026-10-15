"""Import subdepartmenttestdetail -> SubDepartmentTest."""
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
        # map sub_department.code -> id
        sub_by_code = {s.code: s.id for s in M.SubDepartment.query.all() if s.code is not None}
        # map test.adamlab_id -> id
        test_by_aid = {t.adamlab_id: t.id for t in M.Test.query.filter(M.Test.adamlab_id.isnot(None)).all()}

        rows = load("subdepartmenttestdetail")
        added = skipped_sub = skipped_test = dup = 0
        for r in rows:
            scode = i(r.get("subdepartmentcode"))
            tcode = i(r.get("testcode"))
            sort = i(r.get("sortorder")) or 0
            sub_id = sub_by_code.get(scode)
            test_id = test_by_aid.get(tcode)
            if not sub_id:
                skipped_sub += 1; continue
            if not test_id:
                skipped_test += 1; continue
            exists = M.SubDepartmentTest.query.filter_by(sub_department_id=sub_id, test_id=test_id).first()
            if exists:
                dup += 1; continue
            db.session.add(M.SubDepartmentTest(
                sub_department_id=sub_id,
                test_id=test_id,
                sort_order=sort,
            ))
            added += 1
        db.session.commit()
        print(f"added: {added}")
        print(f"duplicates: {dup}")
        print(f"skipped missing sub-dept: {skipped_sub}")
        print(f"skipped missing test: {skipped_test}")
        print(f"total SubDepartmentTest rows now: {M.SubDepartmentTest.query.count()}")

if __name__ == "__main__":
    run()
