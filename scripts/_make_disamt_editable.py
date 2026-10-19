"""Make DIS. AMT column editable per test."""
import io, os
path = os.path.join("templates", "test_settings", "_rate_dept_grid.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# 1) Replace read-only discount_amt cell with editable input
old_cell = "                <td class=\"text-end\">{{ row.discount_amt or 0 }}</td>"
new_cell = (
"                <td class=\"text-end\">" + nl +
"                  <input type=\"number\" step=\"0.01\" min=\"0\" name=\"discount_amount_override\"" + nl +
"                         value=\"{{ row.override_discount_amt if row.override_discount_amt is not none else (row.discount_amt or 0) }}\"" + nl +
"                         form=\"ovr-{{ row.test.id }}\"" + nl +
"                         title=\"Leave as-is to use dept rate; change to override this test only\"" + nl +
"                         style=\"width:80px;padding:4px 8px;border:1px solid #ced4da;border-radius:4px;font-size:0.86rem;text-align:right;\">" + nl +
"                </td>"
)
if old_cell in src:
    src = src.replace(old_cell, new_cell, 1)
    print("DIS. AMT cell → editable input")
else:
    print("DIS. AMT cell anchor MISS")

# 2) Replace the read-only Update link with a real form (if still there)
old_link = (
"              <td class=\"text-end\">" + nl +
"                <a href=\"{{ url_for('tests.view_test', test_id=row.test.id) }}\" class=\"rdg-sbtn\" target=\"_blank\">Update</a>" + nl +
"              </td>"
)
new_link = (
"              <td class=\"text-end\">" + nl +
"                <form id=\"ovr-{{ row.test.id }}\" method=\"POST\" action=\"{{ url_for('tests.rate_test_save_override', cat_id=rate_category.id, test_id=row.test.id) }}\" style=\"display:inline;\">" + nl +
"                  <input type=\"hidden\" name=\"dept\" value=\"{{ selected_dept.id }}\">" + nl +
"                  <button type=\"submit\" class=\"rdg-sbtn rdg-sbtn-blue\">Update</button>" + nl +
"                </form>" + nl +
"              </td>"
)
if old_link in src:
    src = src.replace(old_link, new_link, 1)
    print("Update link → real form")
else:
    print("Update link MISS (already form?)")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
