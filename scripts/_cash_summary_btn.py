"""Fix Report button height/width balance."""
import io, os
path = os.path.join("static", "css", "admin_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== Cash Summary Report button ===== */
.app-content .container .btn-primary.btn-lg {
  min-height: 44px !important;
  height: 44px !important;
  padding: 0 20px !important;
  font-size: 0.9rem !important;
  white-space: nowrap !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 6px !important;
}
"""

if "Cash Summary Report button" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("button height fixed")
