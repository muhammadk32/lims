"""Force patient history table to give actions column space."""
import io, os
path = os.path.join("static", "css", "admin_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* Patient history table: don't squash action column */
.app-content table {
  table-layout: auto !important;
}
.app-content table th:last-child,
.app-content table td:last-child {
  min-width: 220px !important;
  width: 220px !important;
}
"""

if "Patient history table: don't squash" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("table width fix added")
