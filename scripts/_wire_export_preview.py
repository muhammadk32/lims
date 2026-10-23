"""Export button → preview page."""
import io, os
path = os.path.join("templates", "test_settings", "_rate_lists.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# change href from rate_list_export_csv to rate_list_export_preview (the /export page)
src = src.replace(
"url_for('tests.rate_list_export_csv', cat_id=c.id)",
"url_for('tests.rate_list_export_preview', cat_id=c.id)")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("export button now → preview")
