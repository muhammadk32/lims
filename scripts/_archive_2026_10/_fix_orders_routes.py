"""Fix decorator misplacement: move build_lab_rate_map above the @route decorators."""
import io, os

path = os.path.join("modules", "orders", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# The broken block:
broken = (
"# ============================================================" + nl +
"@orders_bp.route('/new', methods=['GET', 'POST'])" + nl +
"@login_required" + nl +
"@permission_required('create_order')" + nl +
nl +
"def build_lab_rate_map():" + nl +
"    \"\"\"Return {lab_id_str: {test_id_str: discount_pct}} for all labs with rate lists.\"\"\"" + nl +
"    from modules.tests.models import RateCategoryTest, RateCategoryDeptRate, Test" + nl +
"    from modules.laboratories.models import Laboratory" + nl +
nl +
"    labs = Laboratory.query.filter(Laboratory.rate_category_id.isnot(None)).all()" + nl +
"    if not labs:" + nl +
"        return {}" + nl +
nl +
"    rc_ids = {lab.rate_category_id for lab in labs}" + nl +
nl +
"    dept_cache = {}" + nl +
"    test_cache = {}" + nl +
"    for rc in rc_ids:" + nl +
"        dept_cache[rc] = {r.department_id: float(r.discount_percent or 0)" + nl +
"                          for r in RateCategoryDeptRate.query.filter_by(rate_category_id=rc).all()}" + nl +
"        test_cache[rc] = {r.test_id: float(r.discount_percent)" + nl +
"                          for r in RateCategoryTest.query.filter_by(rate_category_id=rc).all()" + nl +
"                          if r.discount_percent is not None}" + nl +
nl +
"    test_dept = {t.id: t.category_id" + nl +
"                 for t in Test.query.filter(Test.category_id.isnot(None)).all()}" + nl +
nl +
"    result = {}" + nl +
"    for lab in labs:" + nl +
"        rc = lab.rate_category_id" + nl +
"        dept_map = dept_cache.get(rc, {})" + nl +
"        test_map = test_cache.get(rc, {})" + nl +
"        per_test = {}" + nl +
"        for tid, dept_id in test_dept.items():" + nl +
"            pct = test_map[tid] if tid in test_map else dept_map.get(dept_id, 0.0)" + nl +
"            if pct and pct > 0:" + nl +
"                per_test[str(tid)] = pct" + nl +
"        result[str(lab.id)] = per_test" + nl +
"    return result" + nl +
nl
)

fixed = (
"# ============================================================" + nl +
"@orders_bp.route('/new', methods=['GET', 'POST'])" + nl +
"@login_required" + nl +
"@permission_required('create_order')" + nl +
"def new_order():" + nl
)

# Extract the build_lab_rate_map function text
build_start = src.find("def build_lab_rate_map():")
build_end = src.find("def new_order():")
if build_start < 0 or build_end < 0:
    print("build/new not found")
else:
    build_body = src[build_start:build_end].rstrip() + nl + nl
    # Remove broken block (decorators + build body)
    if broken in src:
        src = src.replace(broken, fixed, 1)
        print("decorators restored to new_order")
    else:
        print("BROKEN block not matched — trying line-based removal")
        # Fallback: remove everything from "# ====" line above @orders_bp.route('/new') to build_body end
        # Not implemented, needs exact match

    # Insert build_lab_rate_map before the (now-fixed) decorator line
    insert_anchor = "# ============================================================" + nl + "@orders_bp.route('/new', methods=['GET', 'POST'])"
    insert_pos = src.find(insert_anchor)
    if insert_pos > 0:
        # Walk back to find the '# ---- Helpers ----' marker to insert after _get_order_or_404
        marker = "def _get_order_or_404(order_id):" + nl + "    order = Order.query.get(order_id)" + nl + "    if not order:" + nl + "        abort(404)" + nl + "    return order" + nl
        if marker in src:
            src = src.replace(marker, marker + nl + build_body, 1)
            print("build_lab_rate_map moved to helper section")
        else:
            print("_get_order_or_404 marker not found")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
