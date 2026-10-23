"""Import packagetestdetail → PanelParameter (additive, dedupe-safe)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests.models import Test, PanelParameter
from sqlalchemy import text

DATA = os.path.join(HERE, "adamlab_import")
def load(n):
    with open(os.path.join(DATA, f"{n}.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def run():
    app = create_app()
    with app.app_context():
        pkg = load("packagetestdetail")
        by_aid = {t.adamlab_id: t for t in Test.query.filter(Test.adamlab_id.isnot(None)).all()}

        added = skipped = 0
        packages_touched = set()
        for r in pkg:
            pcode = r.get("packagecode")
            tcode = r.get("testcode")
            status = (r.get("status") or "A").upper()
            if status != "A": continue

            parent = by_aid.get(pcode)
            child = by_aid.get(tcode)
            if not parent or not child: 
                skipped += 1
                continue

            # mark parent as panel
            if not parent.is_panel:
                parent.is_panel = True

            # insert PanelParameter if not exists
            exists = PanelParameter.query.filter_by(
                panel_id=parent.id, test_id=child.id).first()
            if exists:
                continue
            db.session.add(PanelParameter(
                panel_id=parent.id,
                test_id=child.id,
                sort_order=r.get("sortorder") or 0,
            ))
            added += 1
            packages_touched.add(pcode)

        db.session.commit()
        print(f"added {added} package links across {len(packages_touched)} packages")
        print(f"skipped {skipped} (missing tests)")

        # verify
        for pc in sorted(packages_touched):
            parent = by_aid.get(pc)
            if parent:
                n = PanelParameter.query.filter_by(panel_id=parent.id).count()
                print(f"  {parent.code} {parent.name[:40]:40} → {n} children")

if __name__ == "__main__":
    run()
