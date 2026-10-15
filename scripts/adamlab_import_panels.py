"""Import testgroupdetail -> PanelParameter, and mark parents is_panel=True."""
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
def b_active(status):
    return (status or "A").upper() == "A"

def run():
    app = create_app()
    with app.app_context():
        tg = load("testgroupdetail")

        # build id maps once
        by_aid = {t.adamlab_id: t for t in M.Test.query.filter(M.Test.adamlab_id.isnot(None)).all()}

        panels_created = 0
        links_new = links_updated = 0
        skipped_missing = 0

        for r in tg:
            gcode = i(r.get("groupcode"))
            tcode = i(r.get("testcode"))
            if gcode is None or tcode is None: continue
            if not b_active(r.get("status")): continue

            parent = by_aid.get(gcode)
            child  = by_aid.get(tcode)
            if not parent or not child:
                skipped_missing += 1
                continue

            # mark parent as panel
            if not parent.is_panel:
                parent.is_panel = True
                panels_created += 1

            # prevent self-link
            if parent.id == child.id:
                continue

            pp = M.PanelParameter.query.filter_by(panel_id=parent.id, test_id=child.id).first()
            if pp:
                new_sort = i(r.get("sortorder")) or 0
                if pp.sort_order != new_sort:
                    pp.sort_order = new_sort
                    links_updated += 1
            else:
                db.session.add(M.PanelParameter(
                    panel_id=parent.id,
                    test_id=child.id,
                    sort_order=i(r.get("sortorder")) or 0,
                ))
                links_new += 1

        db.session.commit()
        print(f"panels flagged: {panels_created}")
        print(f"panel links: {links_new} new, {links_updated} updated, {skipped_missing} skipped (missing test)")

if __name__ == "__main__":
    run()
