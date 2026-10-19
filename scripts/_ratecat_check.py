import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from modules.tests import models as M
app = create_app()
with app.app_context():
    print("--- RateCategory ---")
    for c in M.RateCategory.query.order_by(M.RateCategory.code).all():
        n_rates = M.RateCategoryRate.query.filter_by(rate_category_id=c.id).count()
        n_tests = M.RateCategoryTest.query.filter_by(rate_category_id=c.id).count()
        print(f"  code={c.code} name={c.name!r} rates={n_rates} tests={n_tests}")
    print()
    print("sample rates:")
    for r in M.RateCategoryRate.query.limit(5).all():
        print(f"  cat={r.rate_category.name!r} section={r.section_code} pct={r.rate_percent} comm={r.commission}")
    print()
    print("sample linked tests:")
    for rt in M.RateCategoryTest.query.limit(5).all():
        print(f"  cat={rt.rate_category.name!r} test={rt.test.code} {rt.test.name!r}")
