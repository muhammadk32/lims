"""Thicker borders on culture labels inputs."""
import io, os
path = os.path.join("static", "css", "admin_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# Strengthen the existing .cl-input rule
old = ".cl-input {\n  width: 100% !important;\n  padding: 8px 12px !important;\n  border: 2px solid #ced4da !important;"
new = ".cl-input {\n  width: 100% !important;\n  padding: 10px 14px !important;\n  border: 3px solid #1a1a1a !important;\n  box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;"

if old in src:
    src = src.replace(old, new, 1)
    print("cl-input border thickened")
else:
    # append a stronger rule at end
    src = src + "\n" + """
/* Thicker input borders */
.cl-input {
  border: 3px solid #1a1a1a !important;
  padding: 10px 14px !important;
  font-weight: 500 !important;
}
.cl-input:focus {
  border-color: #0d6efd !important;
  box-shadow: 0 0 0 4px rgba(13,110,253,0.2) !important;
}
"""
    print("appended stronger rule")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
