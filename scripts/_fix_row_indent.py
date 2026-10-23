"""Add specimen + reporting_time to rows.append (12-space indent)."""
import io, os
path = os.path.join("modules", "tests", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

old = (
"            rows.append({" + nl +
"                'code': t.code, 'name': t.name," + nl +
"                'department': dept.name if dept else ''," + nl +
"                'price': price, 'discount_pct': eff_pct," + nl +
"                'discount_amt': disc_amt, 'net': net," + nl +
"                'commission_pct': eff_comm," + nl +
"            })"
)

new = (
"            spec = Specimen.query.get(t.specimen_id) if t.specimen_id else None" + nl +
"            rows.append({" + nl +
"                'code': t.code, 'name': t.name," + nl +
"                'department': dept.name if dept else ''," + nl +
"                'specimen': spec.name if spec else (t.sample_type or '—')," + nl +
"                'reporting_time': _fmt_time(t.turnaround_hours)," + nl +
"                'price': price, 'discount_pct': eff_pct," + nl +
"                'discount_amt': disc_amt, 'net': net," + nl +
"                'commission_pct': eff_comm," + nl +
"            })"
)

if old in src:
    src = src.replace(old, new, 1)
    print("row patched")
else:
    print("anchor MISS — indent mismatch")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
