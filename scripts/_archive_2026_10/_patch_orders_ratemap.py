"""Add build_lab_rate_map() + wire into new_order route."""
import io, os

path = os.path.join("modules", "orders", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

nl = "\r\n" if "\r\n" in src else "\n"

helper = (
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

# insert helper before def new_order()
anchor = "def new_order():"
if "def build_lab_rate_map" not in src:
    idx = src.find(anchor)
    if idx > 0:
        # walk back to start of line above
        line_start = src.rfind(nl, 0, idx) + len(nl)
        src = src[:line_start] + helper + src[line_start:]
        print("helper inserted")
    else:
        print("new_order not found")
else:
    print("helper already present")

# wire rate_map into the render_template call
old_render = "    return render_template(" + nl + "        'orders/new.html'," + nl + "        config=get_form_config(),"
new_render = "    return render_template(" + nl + "        'orders/new.html'," + nl + "        rate_map=build_lab_rate_map()," + nl + "        config=get_form_config(),"
if old_render in src:
    src = src.replace(old_render, new_render, 1)
    print("route wired")
else:
    print("render anchor MISS")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
