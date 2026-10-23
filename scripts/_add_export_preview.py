"""Add rate-list export preview page (filters + rendered table)."""
import io, os
path = os.path.join("modules", "tests", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

if "def rate_list_export_preview" not in src:
    route = (
nl + nl +
"@tests_bp.route('/rate-lists/<int:cat_id>/export', methods=['GET'])" + nl +
"@login_required" + nl +
"@permission_required('manage_tests')" + nl +
"def rate_list_export_preview(cat_id):" + nl +
"    from .models import (RateCategory, RateCategoryTest, RateCategoryDeptRate," + nl +
"                         Test, TestCategory)" + nl +
"    cat = RateCategory.query.get_or_404(cat_id)" + nl +
nl +
"    # Filters from query string" + nl +
"    report_type = (request.args.get('report_type') or 'department').lower()" + nl +
"    variant = (request.args.get('variant') or 'with_discount').lower()" + nl +
"    department_id = request.args.get('department', type=int)" + nl +
"    category_id = request.args.get('category', type=int)" + nl +
"    run = bool(request.args.get('run'))" + nl +
nl +
"    # Departments = TestCategory" + nl +
"    departments = TestCategory.query.order_by(TestCategory.name.asc()).all()" + nl +
nl +
"    rows = []" + nl +
"    if run:" + nl +
"        dept_rates = {d.department_id: d for d in" + nl +
"                      RateCategoryDeptRate.query.filter_by(rate_category_id=cat.id).all()}" + nl +
"        q = (RateCategoryTest.query" + nl +
"             .filter_by(rate_category_id=cat.id)" + nl +
"             .order_by(RateCategoryTest.sort_order.asc()))" + nl +
"        for rct in q.all():" + nl +
"            t = Test.query.get(rct.test_id)" + nl +
"            if not t: continue" + nl +
"            if department_id and t.category_id != department_id: continue" + nl +
"            if category_id and t.category_id != category_id: continue" + nl +
"            dept = TestCategory.query.get(t.category_id) if t.category_id else None" + nl +
"            dr = dept_rates.get(t.category_id) if t.category_id else None" + nl +
"            dept_pct = (dr.discount_percent or 0) if dr else 0" + nl +
"            dept_comm = (dr.commission_percent or 0) if dr else 0" + nl +
"            eff_pct = rct.discount_percent if rct.discount_percent is not None else dept_pct" + nl +
"            eff_comm = rct.commission_percent if rct.commission_percent is not None else dept_comm" + nl +
"            price = float(t.price or 0)" + nl +
"            disc_amt = round(price * eff_pct / 100.0, 2)" + nl +
"            net = round(price - disc_amt, 2)" + nl +
"            rows.append({" + nl +
"                'code': t.code, 'name': t.name," + nl +
"                'department': dept.name if dept else ''," + nl +
"                'price': price, 'discount_pct': eff_pct," + nl +
"                'discount_amt': disc_amt, 'net': net," + nl +
"                'commission_pct': eff_comm," + nl +
"            })" + nl +
nl +
"    ctx = {" + nl +
"        'tab': 'rates'," + nl +
"        'rate_category': cat," + nl +
"        'departments': departments," + nl +
"        'report_type': report_type," + nl +
"        'variant': variant," + nl +
"        'department_id': department_id," + nl +
"        'category_id': category_id," + nl +
"        'rows': rows," + nl +
"        'run': run," + nl +
"    }" + nl +
"    return render_template('test_settings/_rate_list_export.html', **ctx)" + nl
    )
    src = src + route
    print("export preview route added")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
