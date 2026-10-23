"""Add export download icon to rate list actions."""
import io, os
path = os.path.join("templates", "test_settings", "_rate_lists.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# Find the action buttons block — insert export before the delete form
anchor = "            <form method=\"POST\" action=\"{{ url_for('tests.rate_list_delete', cat_id=c.id) }}\""
insert = (
"            <a href=\"{{ url_for('tests.rate_list_export_csv', cat_id=c.id) }}\"" + nl +
"               class=\"rdg-sbtn\" title=\"Download CSV\"" + nl +
"               style=\"display:inline-flex;width:28px;height:28px;align-items:center;justify-content:center;background:#e7f7ee;color:#198754;border:none;border-radius:999px;margin-right:4px;\" >" + nl +
"              <i class=\"bi bi-download\"></i>" + nl +
"            </a>" + nl +
"            <form method=\"POST\" action=\"{{ url_for('tests.rate_list_delete', cat_id=c.id) }}\""
)

if "rate_list_export_csv" not in src:
    if anchor in src:
        src = src.replace(anchor, insert, 1)
        print("export button added")
    else:
        print("anchor MISS — check actions block")
else:
    print("already has export button")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
