"""Add rate list CSV export route."""
import io, os
path = os.path.join("modules", "tests", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

if "def rate_list_export_csv" not in src:
    route = (
nl + nl +
"@tests_bp.route('/rate-lists/<int:cat_id>/export.csv')" + nl +
"@login_required" + nl +
"@permission_required('manage_tests')" + nl +
"def rate_list_export_csv(cat_id):" + nl +
"    from flask import Response" + nl +
"    from .models import (RateCategory, RateCategoryTest," + nl +
"                         RateCategoryDeptRate, Test, TestCategory)" + nl +
"    import csv, io" + nl +
nl +
"    cat = RateCategory.query.get_or_404(cat_id)" + nl +
"    dept_rates = {d.department_id: d for d in" + nl +
"                  RateCategoryDeptRate.query.filter_by(rate_category_id=cat.id).all()}" + nl +
"    rows = (RateCategoryTest.query" + nl +
"            .filter_by(rate_category_id=cat.id)" + nl +
"            .order_by(RateCategoryTest.sort_order.asc()).all())" + nl +
nl +
"    buf = io.StringIO()" + nl +
"    buf.write('\\ufeff')  # UTF-8 BOM for Excel" + nl +
"    w = csv.writer(buf)" + nl +
"    w.writerow(['Test Code', 'Test Name', 'Department'," + nl +
"                'Lab Rate', 'Discount %', 'Discount Amt'," + nl +
"                'Net Rate', 'Commission %'])" + nl +
"    for r in rows:" + nl +
"        t = Test.query.get(r.test_id)" + nl +
"        if not t: continue" + nl +
"        dept = TestCategory.query.get(t.category_id) if t.category_id else None" + nl +
"        dr = dept_rates.get(t.category_id) if t.category_id else None" + nl +
"        dept_pct = (dr.discount_percent or 0) if dr else 0" + nl +
"        dept_comm = (dr.commission_percent or 0) if dr else 0" + nl +
"        eff_pct = r.discount_percent if r.discount_percent is not None else dept_pct" + nl +
"        eff_comm = r.commission_percent if r.commission_percent is not None else dept_comm" + nl +
"        price = float(t.price or 0)" + nl +
"        disc_amt = round(price * eff_pct / 100.0, 2)" + nl +
"        net = round(price - disc_amt, 2)" + nl +
"        w.writerow([t.code, t.name, dept.name if dept else ''," + nl +
"                    f'{price:.2f}', f'{eff_pct:.2f}', f'{disc_amt:.2f}'," + nl +
"                    f'{net:.2f}', f'{eff_comm:.2f}'])" + nl +
nl +
"    data = buf.getvalue()" + nl +
"    fname = f'rate_list_{cat.name.replace(\" \", \"_\")}.csv'" + nl +
"    return Response(data, mimetype='text/csv'," + nl +
"                    headers={'Content-Disposition': f'attachment; filename={fname}'})" + nl
    )
    src = src + route
    print("export route added")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
