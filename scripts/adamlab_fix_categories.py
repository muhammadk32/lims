"""Fix categories: use labdepartment as TestCategory. Relink tests via
labtestdetail.GroupID -> TestHead.DepartmentID -> labdepartment."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from app import create_app
from extensions import db
from modules.tests import models as M

DATA = os.path.join(HERE, "adamlab_import")
def load(n):
    with open(os.path.join(DATA, f"{n}.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def s(v):
    if v is None: return None
    v = str(v).strip()
    return v or None
def i(v):
    if v is None: return None
    try: return int(v)
    except (TypeError, ValueError): return None
def b_active(status):
    return (status or "A").upper() == "A"

def run():
    app = create_app()
    with app.app_context():
        tag = lambda code: f"dept:{code}"

        # --- 1) wipe prior adamlab-generated categories ---
        old = M.TestCategory.query.filter(M.TestCategory.description.like("adamlab:%")).all()
        for c in old:
            # unlink tests first
            M.Test.query.filter_by(category_id=c.id).update({"category_id": None})
            db.session.delete(c)
        db.session.commit()
        print(f"removed {len(old)} fake categories")

        # --- 2) create real categories from labdepartment ---
        depts = load("labdepartment")
        dept_by_code = {}
        created = updated = 0
        for d in depts:
            code = i(d.get("departmentcode"))
            name = s(d.get("departmentname"))
            if code is None or not name: continue
            if name in ("0",): continue  # skip garbage
            active = b_active(d.get("status"))
            cat = M.TestCategory.query.filter_by(description=tag(code)).first()
            if not cat:
                # reuse by name if present
                cat = M.TestCategory.query.filter_by(name=name).first()
                if not cat:
                    cat = M.TestCategory(name=name)
                    db.session.add(cat)
                    created += 1
                cat.description = tag(code)
            else:
                cat.name = name
                updated += 1
            db.session.flush()
            dept_by_code[code] = cat
        db.session.commit()
        print(f"categories: {created} new, {updated} updated, total {M.TestCategory.query.count()}")

        # --- 3) link every test ---
        heads = load("TestHead")
        head_to_dept = {}
        for h in heads:
            hid = i(h.get("ID"))
            did = i(h.get("DepartmentID"))
            if hid is not None and did is not None:
                head_to_dept[hid] = did

        lt = load("labtestdetail")
        linked = 0
        for r in lt:
            aid = i(r.get("testcode"))
            gid = i(r.get("GroupID"))
            if aid is None or gid is None: continue
            did = head_to_dept.get(gid)
            cat = dept_by_code.get(did)
            if not cat: continue
            t = M.Test.query.filter_by(adamlab_id=aid).first()
            if not t: continue
            if t.category_id != cat.id:
                t.category_id = cat.id
                linked += 1
        db.session.commit()
        print(f"tests linked: {linked}")

if __name__ == "__main__":
    run()