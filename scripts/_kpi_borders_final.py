"""Force KPI border visible — thicker, border-collapse, no shrink."""
import io, os
path = os.path.join("static", "css", "test_settings_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# Remove existing kpi blocks
import re
src = re.sub(r'\.ts-kpi\s*\{[^}]*\}', '', src)
src = re.sub(r'\.ts-kpi td\s*\{[^}]*\}', '', src)
src = re.sub(r'\.ts-kpi td:last-child\s*\{[^}]*\}', '', src)

# Add clean, strong border rules at end
css = """
/* ===== KPI strip: strong dark border ===== */
table.ts-kpi {
  border: 3px solid #1a1a1a !important;
  border-collapse: separate !important;
  border-spacing: 0 !important;
  border-radius: 12px !important;
  overflow: hidden !important;
  box-shadow: 0 4px 14px rgba(0,0,0,0.15) !important;
  background: #fff !important;
  width: 100%;
}
table.ts-kpi td {
  border: none !important;
  border-right: 2px solid #1a1a1a !important;
  padding: 14px 18px !important;
  vertical-align: middle !important;
  background: #fff !important;
}
table.ts-kpi td:last-child {
  border-right: none !important;
}
table.ts-kpi .ts-kpi-label {
  font-size: 0.72rem !important;
  font-weight: 800 !important;
  text-transform: uppercase !important;
  color: #6c757d !important;
  letter-spacing: 0.06em;
}
table.ts-kpi .ts-kpi-value {
  font-size: 1.35rem !important;
  font-weight: 900 !important;
  color: #1a3d7c !important;
  margin-top: 4px;
}
"""
src = src + "\n" + css

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("KPI borders forced — 3px dark + shadow")
