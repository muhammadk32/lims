"""Fix KPI strip border — table has outer border, cells have only right/bottom."""
import io, os
path = os.path.join("static", "css", "test_settings_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

old = (
".ts-kpi { border-radius: 10px !important; overflow: hidden; }\n"
".ts-kpi td { padding: 8px 12px !important; border: 2px solid var(--theme-primary) !important; }"
)
new = (
".ts-kpi {\n"
"  border: 2px solid #212529 !important;\n"
"  border-radius: 12px !important;\n"
"  overflow: hidden !important;\n"
"  background: #fff !important;\n"
"  box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;\n"
"}\n"
".ts-kpi td {\n"
"  padding: 12px 16px !important;\n"
"  border-right: 2px solid #212529 !important;\n"
"  border-bottom: none !important;\n"
"  border-top: none !important;\n"
"  border-left: none !important;\n"
"}\n"
".ts-kpi td:last-child {\n"
"  border-right: none !important;\n"
"}\n"
".ts-kpi .ts-kpi-label {\n"
"  font-size: 0.72rem !important;\n"
"  font-weight: 700 !important;\n"
"  text-transform: uppercase !important;\n"
"  color: #6c757d !important;\n"
"  letter-spacing: 0.05em;\n"
"}\n"
".ts-kpi .ts-kpi-value {\n"
"  font-size: 1.3rem !important;\n"
"  font-weight: 800 !important;\n"
"  color: #1a3d7c !important;\n"
"}"
)

if old in src:
    src = src.replace(old, new, 1)
    print("KPI border fixed")
else:
    print("anchor MISS — dump current .ts-kpi rules")

# Remove the duplicate block I added earlier (if present)
dup = (
"/* ===== KPI strips ===== */\n"
".ts-kpi {\n"
"  border: 2px solid #212529 !important;\n"
"  border-radius: 12px !important;\n"
"  overflow: hidden !important;\n"
"  background: #fff !important;\n"
"  box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;\n"
"  margin-bottom: 14px !important;\n"
"}"
)
if dup in src:
    src = src.replace(dup, "", 1)
    print("removed duplicate")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
