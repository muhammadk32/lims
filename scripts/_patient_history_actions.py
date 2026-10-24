"""Patient History: fix action column alignment + prevent wrap."""
import io, os
path = os.path.join("static", "css", "admin_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== Patient History action column ===== */
.app-content table td:last-child,
.app-content table th:last-child {
  white-space: nowrap !important;
  text-align: center !important;
  vertical-align: middle !important;
  padding: 8px 10px !important;
}
.app-content table td:last-child .btn,
.app-content table td:last-child a.btn,
.app-content table td:last-child button {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  min-width: 60px !important;
  height: 32px !important;
  padding: 0 10px !important;
  font-size: 0.78rem !important;
  font-weight: 700 !important;
  border-radius: 6px !important;
  border-width: 2px !important;
  margin: 0 2px !important;
  vertical-align: middle !important;
  white-space: nowrap !important;
}
/* Ensure the row doesn't compress */
.app-content table td:last-child {
  min-width: 220px !important;
}
"""

if "Patient History action column" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("action column fix added")
else:
    print("already present")
