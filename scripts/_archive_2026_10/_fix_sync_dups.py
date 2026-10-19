"""Guard sync_lab_rate_list against dup inserts (unique constraint aware)."""
import io, os
path = os.path.join("modules", "laboratories", "services.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

old = (
"    from modules.tests.models import PanelParameter" + nl +
"    # ids of tests that are children of any panel — exclude" + nl +
"    child_ids = {r[0] for r in db.session.query(PanelParameter.test_id).distinct().all()}" + nl +
"    seen = set()" + nl +
"    sort_i = 0" + nl +
"    for lt in RateCategoryTest.query.filter_by(rate_category_id=std.id).order_by(RateCategoryTest.sort_order).all():" + nl +
"        if lt.test_id in seen:" + nl +
"            continue" + nl +
"        if lt.test_id in child_ids:" + nl +
"            continue" + nl +
"        seen.add(lt.test_id)" + nl +
"        sort_i += 1" + nl +
"        db.session.add(RateCategoryTest(" + nl +
"            rate_category_id=new_cat.id," + nl +
"            test_id=lt.test_id," + nl +
"            sort_order=sort_i," + nl +
"        ))"
)

new = (
"    from modules.tests.models import PanelParameter, Test" + nl +
"    # ids of tests that are children of any panel — exclude" + nl +
"    child_ids = {r[0] for r in db.session.query(PanelParameter.test_id).distinct().all()}" + nl +
"    # build canonical set: only active, non-child tests from Standard (deduped)" + nl +
"    raw_ids = [r[0] for r in db.session.query(RateCategoryTest.test_id)" + nl +
"               .filter_by(rate_category_id=std.id)" + nl +
"               .order_by(RateCategoryTest.sort_order.asc()).all()]" + nl +
"    active_ids = {r[0] for r in db.session.query(Test.id)" + nl +
"                  .filter(Test.is_active == True).all()}" + nl +
"    seen = set()" + nl +
"    sort_i = 0" + nl +
"    for tid in raw_ids:" + nl +
"        if tid in seen or tid in child_ids or tid not in active_ids:" + nl +
"            continue" + nl +
"        seen.add(tid)" + nl +
"        sort_i += 1" + nl +
"        db.session.add(RateCategoryTest(" + nl +
"            rate_category_id=new_cat.id," + nl +
"            test_id=tid," + nl +
"            sort_order=sort_i," + nl +
"        ))"
)

if old in src:
    src = src.replace(old, new, 1)
    print("sync helper: dedupe + active-only")
else:
    print("anchor MISS")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
