"""Add/adjust rate_test_save_override route to accept discount_amount_override."""
import io, os
path = os.path.join("modules", "tests", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# If route doesn't exist, append
if "def rate_test_save_override" not in src:
    route = (
nl + nl +
"@tests_bp.route('/rate-lists/<int:cat_id>/test-override/<int:test_id>', methods=['POST'])" + nl +
"@login_required" + nl +
"@permission_required('manage_tests')" + nl +
"def rate_test_save_override(cat_id, test_id):" + nl +
"    from .models import RateCategoryTest, RateCategoryDeptRate, Test as _T" + nl +
"    rct = RateCategoryTest.query.filter_by(rate_category_id=cat_id, test_id=test_id).first()" + nl +
"    if not rct:" + nl +
"        flash('Test not in this rate list.', 'warning')" + nl +
"        return redirect(request.referrer or url_for('tests.index', tab='rates', cat=cat_id))" + nl +
"    t = _T.query.get(test_id)" + nl +
"    # find the dept rate to know default" + nl +
"    dr = RateCategoryDeptRate.query.filter_by(rate_category_id=cat_id, department_id=t.category_id).first() if t and t.category_id else None" + nl +
"    default_pct = (dr.discount_percent or 0) if dr else 0" + nl +
"    raw_amt = (request.form.get('discount_amount_override') or '').strip()" + nl +
"    if raw_amt == '':" + nl +
"        rct.discount_percent = None  # fall back to dept" + nl +
"    else:" + nl +
"        try:" + nl +
"            amt = float(raw_amt)" + nl +
"            price = float(t.price or 0) if t else 0" + nl +
"            pct = (amt / price * 100.0) if price > 0 else 0.0" + nl +
"            rct.discount_percent = round(pct, 2)" + nl +
"        except (ValueError, TypeError):" + nl +
"            pass" + nl +
"    db.session.commit()" + nl +
"    flash('Test override saved.', 'success')" + nl +
"    dept = request.form.get('dept')" + nl +
"    if dept:" + nl +
"        return redirect(url_for('tests.index', tab='rates', cat=cat_id, dept=dept))" + nl +
"    return redirect(url_for('tests.index', tab='rates', cat=cat_id))" + nl
    )
    src = src + route
    print("route appended")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
