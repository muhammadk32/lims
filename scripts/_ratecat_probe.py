"""Import ratelistcategoryrate + ratelistcategorytestdetail."""
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
def fl(v):
    try: return float(v)
    except (TypeError, ValueError): return None

def run():
    app = create_app()
    with app.app_context():
        cat_by_code = {c.code: c for c in M.RateCategory.query.all() if c.code is not None}
        test_by_aid = {t.adamlab_id: t for t in M.Test.query.filter(M.Test.adamlab_id.isnot(None)).all()}

        # --- rates ---
        rcr = load("ratelistcategoryrate")
        r_added = r_skip_cat = 0
        for r in rcr:
            cc = i(r.get("companycode"))
            # in AdamLab companycode is actually the rate category's own code (rlcatcode)
            # per field-name it's "companycode" but AdamLab reused it for category
            pass
        # The columns: companycode, sectioncode, ratepercent, recordnumber, commission, flag
        # We'll interpret: ratecategory via companycode? Check the actual JSON keys.
        print("ratelistcategoryrate keys:", list(rcr[0].keys()) if rcr else "empty")
        print("sample row:", rcr[0] if rcr else None)

        rct = load("ratelistcategorytestdetail")
        print("ratelistcategorytestdetail keys:", list(rct[0].keys()) if rct else "empty")
        print("sample row:", rct[0] if rct else None)

if __name__ == "__main__":
    run()
