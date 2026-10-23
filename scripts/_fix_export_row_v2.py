"""Add specimen + reporting_time back to rate_list_export_preview rows."""
import io, os
path = os.path.join("modules", "tests", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# 1) Add imports
src = src.replace(
"    from .models import (RateCategory, RateCategoryTest, RateCategoryDeptRate," + nl +
"                         Test, TestCategory)",
"    from .models import (RateCategory, RateCategoryTest, RateCategoryDeptRate," + nl +
"                         Test, TestCategory, Specimen)")

# 2) Add fmt_time helper
old_helper_anchor = "    # Departments = TestCategory"
new_helper = (
"    def _fmt_time(hours):" + nl +
"        if not hours or hours <= 24: return 'SAME DAY'" + nl +
"        if hours < 48: return 'AFTER ONE DAY'" + nl +
"        days = round(hours / 24)" + nl +
"        if days < 7: return f'AFTER {days} DAYS'" + nl +
"        weeks = round(days / 7)" + nl +
"        return f'AFTER {weeks} WEEK' + ('S' if weeks > 1 else '')" + nl +
nl +
"    # Departments = TestCategory"
)
src = src.replace(old_helper_anchor, new_helper, 1)

# 3) Add specimen + reporting_time to each row dict
old_row = (
"              rows.append({" + nl +
"                  'code': t.code, 'name': t.name," + nl +
"                  'department': dept.name if dept else ''," + nl +
"                  'price': price, 'discount_pct': eff_pct," + nl +
"                  'discount_amt': disc_amt, 'net': net," + nl +
"                  'commission_pct': eff_comm," + nl +
"              })"
)
new_row = (
"              spec = Specimen.query.get(t.specimen_id) if t.specimen_id else None" + nl +
"              rows.append({" + nl +
"                  'code': t.code, 'name': t.name," + nl +
"                  'department': dept.name if dept else ''," + nl +
"                  'specimen': spec.name if spec else (t.sample_type or '—')," + nl +
"                  'reporting_time': _fmt_time(t.turnaround_hours)," + nl +
"                  'price': price, 'discount_pct': eff_pct," + nl +
"                  'discount_amt': disc_amt, 'net': net," + nl +
"                  'commission_pct': eff_comm," + nl +
"              })"
)
if old_row in src:
    src = src.replace(old_row, new_row, 1)
    print("row dict: specimen + reporting_time added")
else:
    print("ROW anchor MISS")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
