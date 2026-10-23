"""Add broad pattern rules to admin_theme.css — catch all custom headers/filters."""
import io, os
path = os.path.join("static", "css", "admin_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== BROAD PATTERN: any admin page header/filter ===== */
[class$="-header"], [class*="-header "]:not(.modal-header):not(.card-header):not(.dropdown-header) {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  color: #fff !important;
  padding: 14px 20px !important;
  border-radius: 12px !important;
  border: 2px solid #1a3d7c !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
  margin-bottom: 14px !important;
}
[class$="-header"] h1,
[class$="-header"] h2,
[class$="-header"] h3,
[class$="-header"] [class$="-title"],
[class$="-header"] [class$="-title"] i,
[class$="-header"] [class$="-sub"],
[class$="-header"] [class$="-subtitle"] {
  color: #fff !important;
}
[class$="-header"] i {
  color: #ffd166 !important;
}

[class$="-picker"], [class$="-filter"], [class$="-toolbar"], [class$="-strip"] {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
  border: 2px solid #1a3d7c !important;
  border-radius: 12px !important;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
  padding: 14px 16px !important;
}
[class$="-picker"] label,
[class$="-filter"] label,
[class$="-toolbar"] label {
  color: #1a3d7c !important;
  font-weight: 800 !important;
}
[class$="-picker"] select,
[class$="-picker"] input,
[class$="-filter"] select,
[class$="-filter"] input,
[class$="-toolbar"] select,
[class$="-toolbar"] input {
  border: 2px solid #ced4da !important;
  border-radius: 8px !important;
  padding: 6px 10px !important;
  height: 36px !important;
}

[class$="-empty"] {
  border: 2px dashed #1a3d7c !important;
  border-radius: 12px !important;
  background: #f0f4ff !important;
  color: #1a3d7c !important;
  padding: 24px !important;
  font-weight: 600;
}
"""

if "BROAD PATTERN: any admin page header" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("broad pattern rules added")
else:
    print("already present")
