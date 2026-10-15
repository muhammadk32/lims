"""Import AdamLab TestHead -> TestCategory, and link tests by GroupID."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from app import create_app
from extensions import db
from modules.tests import models as M

DATA = os.path.join(HERE, "adamlab_import")

def load(name):
    with open(os.path.join(DATA, f"{name}.json"), "r", encoding="utf-8") as f:
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
        heads = load("TestHead")
        # 1) create categories keyed by adamlab head id
        #    We store adamlab id inside TestCategory.description as "adamlab:<id>"
        #    so we can find them later without a schema change.
        tag = lambda hid: f"adamlab:{hid}"
        created = linked = 0
        for h in heads:
            hid = i(h.get("ID"))
            if hid is None: continue
            name = s(h.get("Name")) or f"Head {hid}"
            # find by description tag (survives renames)
            cat = M.TestCategory.query.filter_by(description=tag(hid)).first()
            if not cat:
                # also try by name if description match failed (avoid dupes)
                cat = M.TestCategory.query.filter_by(name=name).first()
                if not cat:
                    cat = M.TestCategory(name=name)
                    db.session.add(cat)
                cat.description = tag(hid)
            cat.name = name
            db.session.flush()

        db.session.commit()
        print(f"categories: {M.TestCategory.query.count()} total")

        # 2) link tests: labtestdetail.GroupID -> TestHead.ID -> category
        head_map = {i(h.get("ID")): h for h in heads if i(h.get("ID")) is not None}
        lt = load("labtestdetail")
        linked = 0
        for r in lt:
            aid = i(r.get("testcode"))
            gid = i(r.get("GroupID"))
            if aid is None or gid is None: continue
            head = head_map.get(gid)
            if not head: continue
            hid = i(head.get("ID"))
            cat = M.TestCategory.query.filter_by(description=tag(hid)).first()
            if not cat: continue
            t = M.Test.query.filter_by(adamlab_id=aid).first()
            if not t: continue
            if t.category_id != cat.id:
                t.category_id = cat.id
                linked += 1
        db.session.commit()
        print(f"tests linked to categories: {linked}")

if __name__ == "__main__":
    run()