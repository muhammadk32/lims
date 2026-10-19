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
        r_added = r_skip = 0
        for r in load("ratelistcategoryrate"):
            cc = i(r.get("companycode"))
            cat = cat_by_code.get(cc)
            if not cat:
                r_skip += 1; continue
            exists = M.RateCategoryRate.query.filter_by(
                rate_category_id=cat.id,
                section_code=i(r.get("sectioncode")),
            ).first()
            if exists:
                exists.rate_percent = fl(r.get("ratepercent"))
                exists.commission = fl(r.get("commission"))
            else:
                db.session.add(M.RateCategoryRate(
                    rate_category_id=cat.id,
                    company_code=None,
                    section_code=i(r.get("sectioncode")),
                    rate_percent=fl(r.get("ratepercent")),
                    commission=fl(r.get("commission")),
                ))
                r_added += 1
        db.session.commit()
        print(f"RateCategoryRate: {r_added} new, {r_skip} skipped")

        # --- tests in each rate category ---
        t_added = t_skip_test = t_skip_cat = t_dup = 0
        for r in load("ratelistcategorytestdetail"):
            cc = i(r.get("rlcatcode"))
            tc = i(r.get("testcode"))
            cat = cat_by_code.get(cc)
            test = test_by_aid.get(tc)
            if not cat:
                t_skip_cat += 1; continue
            if not test:
                t_skip_test += 1; continue
            exists = M.RateCategoryTest.query.filter_by(
                rate_category_id=cat.id, test_id=test.id).first()
            if exists:
                t_dup += 1; continue
            db.session.add(M.RateCategoryTest(
                rate_category_id=cat.id,
                test_id=test.id,
                sort_order=i(r.get("sortorder")) or 0,
            ))
            t_added += 1
        db.session.commit()
        print(f"RateCategoryTest: {t_added} new, {t_dup} dup, {t_skip_cat} skip cat, {t_skip_test} skip test")
        print(f"totals: RateCategoryRate={M.RateCategoryRate.query.count()}, RateCategoryTest={M.RateCategoryTest.query.count()}")

if __name__ == "__main__":
    run()
