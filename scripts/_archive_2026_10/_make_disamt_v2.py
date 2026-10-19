"""Make DIS. AMT editable — exact patch."""
import io, os
path = os.path.join("templates", "test_settings", "_rate_dept_grid.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# Try all common indentation variants
for indent in ["                ", "              ", "                  "]:
    old = indent + "<td class=\"text-end\">{{ row.discount_amt or 0 }}</td>"
    if old in src:
        new = (
indent + "<td class=\"text-end\">" + nl +
indent + "  <input type=\"number\" step=\"0.01\" min=\"0\" name=\"discount_amount_override\"" + nl +
indent + "         value=\"{{ row.override_discount_amt if row.override_discount_amt is not none else (row.discount_amt or 0) }}\"" + nl +
indent + "         form=\"ovr-{{ row.test.id }}\"" + nl +
indent + "         title=\"Blank = dept rate\" " + nl +
indent + "         style=\"width:90px;padding:4px 8px;border:1px solid #0d6efd;border-radius:4px;font-size:0.86rem;text-align:right;\">" + nl +
indent + "</td>"
        )
        src = src.replace(old, new, 1)
        print(f"DIS. AMT → input (indent '{indent}')")
        break
else:
    print("all indent variants MISSED")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
