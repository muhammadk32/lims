"""Auto-create a rate list for a lab, populated from Standard."""
import io, os

path = os.path.join("modules", "laboratories", "services.py")
if not os.path.exists(path):
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write("")

with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

if "def sync_lab_rate_list" not in src:
    block = (
(nl if src else "") + (nl if src else "") +
"def sync_lab_rate_list(lab, force=False):" + nl +
"    \"\"\"Ensure the lab has its own rate list, populated from Standard.""" + nl +
"    from extensions import db" + nl +
"    from modules.tests.models import (RateCategory, RateCategoryTest," + nl +
"                                     RateCategoryDeptRate, TestCategory)" + nl +
nl +
"    if lab.rate_category_id and not force:" + nl +
"        return lab.rate_category" + nl +
nl +
"    std = RateCategory.query.filter_by(is_standard=True).first() or \\" + nl +
"          RateCategory.query.order_by(RateCategory.id.asc()).first()" + nl +
"    if not std:" + nl +
"        return None" + nl +
nl +
"    # reuse existing auto-created list for this lab if present" + nl +
"    auto_name = f'{lab.name} rate'" + nl +
"    existing = RateCategory.query.filter_by(name=auto_name).first()" + nl +
"    if existing:" + nl +
"        lab.rate_category_id = existing.id" + nl +
"        db.session.commit()" + nl +
"        return existing" + nl +
nl +
"    new_cat = RateCategory(" + nl +
"        name=auto_name," + nl +
"        description=f'Auto-created for {lab.name}'," + nl +
"        parent_rate_category_id=std.id," + nl +
"        is_standard=False," + nl +
"        is_active=True," + nl +
"    )" + nl +
"    db.session.add(new_cat)" + nl +
"    db.session.flush()" + nl +
nl +
"    # copy test links from Standard" + nl +
"    seen = set()" + nl +
"    for lt in RateCategoryTest.query.filter_by(rate_category_id=std.id).all():" + nl +
"        if lt.test_id in seen:" + nl +
"            continue" + nl +
"        seen.add(lt.test_id)" + nl +
"        db.session.add(RateCategoryTest(" + nl +
"            rate_category_id=new_cat.id," + nl +
"            test_id=lt.test_id," + nl +
"            sort_order=lt.sort_order," + nl +
"        ))" + nl +
nl +
"    # seed dept-level rates using lab.discount_percent" + nl +
"    default_pct = float(lab.discount_percent or 0)" + nl +
"    default_comm = float(lab.commission_percent or 0)" + nl +
"    for dept in TestCategory.query.all():" + nl +
"        db.session.add(RateCategoryDeptRate(" + nl +
"            rate_category_id=new_cat.id," + nl +
"            department_id=dept.id," + nl +
"            discount_percent=default_pct," + nl +
"            commission_percent=default_comm," + nl +
"        ))" + nl +
nl +
"    lab.rate_category_id = new_cat.id" + nl +
"    db.session.commit()" + nl +
"    return new_cat" + nl
    )
    src = src + block
    print("sync_lab_rate_list() added")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
