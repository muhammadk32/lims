"""Exclude child-only tests from rate list export."""
import io, os
path = os.path.join("modules", "tests", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# find the loop in rate_list_export_preview
old = (
"        q = (RateCategoryTest.query" + nl +
"             .filter_by(rate_category_id=cat.id)" + nl +
"             .order_by(RateCategoryTest.sort_order.asc()))" + nl +
"        for rct in q.all():" + nl +
"            t = Test.query.get(rct.test_id)" + nl +
"            if not t: continue"
)
new = (
"        # child-only test ids (excluded from printing)" + nl +
"        from modules.tests.models import PanelParameter" + nl +
"        child_ids = {r[0] for r in db.session.query(PanelParameter.test_id).distinct().all()}" + nl +
"        q = (RateCategoryTest.query" + nl +
"             .filter_by(rate_category_id=cat.id)" + nl +
"             .order_by(RateCategoryTest.sort_order.asc()))" + nl +
"        for rct in q.all():" + nl +
"            t = Test.query.get(rct.test_id)" + nl +
"            if not t: continue" + nl +
"            # skip child-only tests (analytes inside a parent — never orderable)" + nl +
"            if t.id in child_ids: continue"
)

if old in src and "child-only test ids (excluded" not in src:
    src = src.replace(old, new, 1)
    print("child-only excluded from export")
else:
    print("anchor MISS or already patched")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
