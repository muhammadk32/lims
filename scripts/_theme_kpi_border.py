"""Border around KPI strips (categories, packages, etc)."""
import io, os
path = os.path.join("static", "css", "test_settings_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== KPI strips ===== */
.ts-kpi {
  border: 2px solid #212529 !important;
  border-radius: 12px !important;
  overflow: hidden !important;
  background: #fff !important;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
  margin-bottom: 14px !important;
}
.ts-kpi td {
  padding: 12px 16px !important;
  border-right: 2px solid #212529 !important;
  vertical-align: middle !important;
}
.ts-kpi td:last-child {
  border-right: none !important;
}
.ts-kpi .ts-kpi-label {
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  color: #6c757d !important;
  letter-spacing: 0.05em;
}
.ts-kpi .ts-kpi-value {
  font-size: 1.3rem !important;
  font-weight: 800 !important;
  color: #1a3d7c !important;
}
"""

if ".ts-kpi {" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("ts-kpi border added")
else:
    print("already present")
