"""Rewrite rate_list_export_preview: full data + 6 variants."""
import io, os
path = os.path.join("modules", "tests", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# find and replace the whole function
start_marker = "@tests_bp.route('/rate-lists/<int:cat_id>/export', methods=['GET'])"
end_marker = "@tests_bp.route('/rate-lists/<int:cat_id>/test-override/<int:test_id>'"
si = src.find(start_marker)
ei = src.find(end_marker)
if si < 0 or ei < 0:
    print("function boundaries not found")
else:
    new_fn = (
"@tests_bp.route('/rate-lists/<int:cat_id>/export', methods=['GET'])" + nl +
"@login_required" + nl +
"@permission_required('manage_tests')" + nl +
"def rate_list_export_preview(cat_id):" + nl +
"    from .models import (RateCategory, RateCategoryTest, RateCategoryDeptRate," + nl +
"                         Test, TestCategory, Specimen)" + nl +
"    cat = RateCategory.query.get_or_404(cat_id)" + nl +
nl +
"    report_type = (request.args.get('report_type') or 'department').lower()" + nl +
"    variant = (request.args.get('variant') or 'with_discount').lower()" + nl +
"    department_id = request.args.get('department', type=int)" + nl +
"    category_id = request.args.get('category', type=int)" + nl +
"    run = bool(request.args.get('run'))" + nl +
nl +
"    departments = TestCategory.query.order_by(TestCategory.name.asc()).all()" + nl +
nl +
"    def fmt_time(hours):" + nl +
"        if not hours or hours <= 0: return 'SAME DAY'" + nl +
"        if hours <= 24: return 'SAME DAY'" + nl +
"        if hours < 48: return 'AFTER ONE DAY'" + nl +
"        days = round(hours / 24)" + nl +
"        if days < 7: return f'AFTER {days} DAYS'" + nl +
"        weeks = round(days / 7)" + nl +
"        return f'AFTER {weeks} WEEK' + ('S' if weeks > 1 else '')" + nl +
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
"            spec = Specimen.query.get(t.specimen_id) if t.specimen_id else None" + nl +
"            rows.append({" + nl +
"                'code': t.code, 'name': t.name," + nl +
"                'department': dept.name if dept else '—'," + nl +
"                'specimen': spec.name if spec else (t.sample_type or '—')," + nl +
"                'reporting_time': fmt_time(t.turnaround_hours)," + nl +
"                'price': price, 'discount_pct': eff_pct," + nl +
"                'discount_amt': disc_amt, 'net': net," + nl +
"                'commission_pct': eff_comm," + nl +
"            })" + nl +
nl +
"        # sort for grouping" + nl +
"        if variant == 'department_wise':" + nl +
"            rows.sort(key=lambda r: (r['department'] or '', r['name'] or ''))" + nl +
"        elif variant == 'category_wise':" + nl +
"            rows.sort(key=lambda r: (r['department'] or '', r['name'] or ''))" + nl +
nl +
"    # header uses current lab branding" + nl +
"    from core.models import LabSettings" + nl +
"    settings = LabSettings.get()" + nl +
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
"        'settings': settings," + nl +
"    }" + nl +
"    return render_template('test_settings/_rate_list_export.html', **ctx)" + nl +
nl + nl
    )
    src = src[:si] + new_fn + src[ei:]
    print("preview function rewritten")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
