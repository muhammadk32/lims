"""Polish reception form settings page."""
import io, os
path = os.path.join("templates", "settings", "reception_form.html")
if not os.path.exists(path):
    # try alt name
    cand = [f for f in os.listdir("templates/settings") if "reception" in f.lower() or "form_settings" in f.lower()]
    print("candidates:", cand)
    if cand:
        path = os.path.join("templates", "settings", cand[0])
    else:
        print("not found"); raise SystemExit

with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

add = (
"/* ===== Reception Form Settings polish ===== */" + nl +
"/* Section headers → blue gradient */" + nl +
".rfs-section-hd, .reception-section-hd, .form-section-hd," + nl +
".section-header, .rfs-section-head {" + nl +
"  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;" + nl +
"  color: #fff !important;" + nl +
"  padding: 10px 14px !important;" + nl +
"  border-radius: 8px 8px 0 0 !important;" + nl +
"  border: 2px solid #212529 !important;" + nl +
"  border-bottom: 2px solid #212529 !important;" + nl +
"  font-weight: 800 !important;" + nl +
"  text-transform: uppercase !important;" + nl +
"  letter-spacing: 0.05em !important;" + nl +
"}" + nl +
"/* Section body: rounded card */" + nl +
".rfs-section-bd, .reception-section-bd, .form-section-bd," + nl +
".section-body, .rfs-section-body {" + nl +
"  background: #fff !important;" + nl +
"  border: 2px solid #212529 !important;" + nl +
"  border-top: none !important;" + nl +
"  border-radius: 0 0 8px 8px !important;" + nl +
"  padding: 12px 14px !important;" + nl +
"  margin-bottom: 12px !important;" + nl +
"}" + nl +
"/* Form rows */" + nl +
".rfs-row, .reception-row, .form-row, .rfs-field-row {" + nl +
"  padding: 8px 10px !important;" + nl +
"  border-bottom: 1px solid #dee2e6 !important;" + nl +
"}" + nl +
".rfs-row:last-child, .reception-row:last-child, .form-row:last-child { border-bottom: none !important; }" + nl +
".rfs-row:hover, .reception-row:hover, .form-row:hover {" + nl +
"  background: #f5f9ff !important;" + nl +
"}" + nl +
"/* Field labels: bold + uppercase */" + nl +
".rfs-lbl, .reception-lbl, .form-lbl, .rfs-field-lbl {" + nl +
"  font-size: 0.85rem !important;" + nl +
"  font-weight: 700 !important;" + nl +
"  color: #212529 !important;" + nl +
"  text-transform: uppercase !important;" + nl +
"  letter-spacing: 0.02em !important;" + nl +
"}" + nl +
"/* Presets row */" + nl +
".rfs-presets, .reception-presets, .presets-bar {" + nl +
"  background: #fff !important;" + nl +
"  border: 2px solid #212529 !important;" + nl +
"  border-radius: 10px !important;" + nl +
"  padding: 10px 14px !important;" + nl +
"  margin-bottom: 14px !important;" + nl +
"}" + nl +
".rfs-presets button, .reception-presets button, .presets-bar button {" + nl +
"  border: 2px solid #1a3d7c !important;" + nl +
"  border-radius: 6px !important;" + nl +
"  background: #fff !important;" + nl +
"  color: #1a3d7c !important;" + nl +
"  font-weight: 700 !important;" + nl +
"  font-size: 0.8rem !important;" + nl +
"  padding: 6px 14px !important;" + nl +
"  text-transform: uppercase !important;" + nl +
"  letter-spacing: 0.04em !important;" + nl +
"}" + nl +
".rfs-presets button:hover, .reception-presets button:hover {" + nl +
"  background: #1a3d7c !important;" + nl +
"  color: #fff !important;" + nl +
"}" + nl +
"/* Page header (already blue gradient) */" + nl +
".rfs-header, .reception-header {" + nl +
"  max-width: 100% !important;" + nl +
"}" + nl +
"/* Toggle switches → theme color */" + nl +
"input[type=\"checkbox\"].form-check-input:checked," + nl +
".form-switch input[type=\"checkbox\"]:checked {" + nl +
"  background-color: #0d6efd !important;" + nl +
"  border-color: #1a3d7c !important;" + nl +
"}" + nl +
"/* Save button */" + nl +
".rfs-page button[type=\"submit\"], .reception-page button[type=\"submit\"] {" + nl +
"  background: linear-gradient(135deg, #198754 0%, #20c997 100%) !important;" + nl +
"  border: 2px solid #198754 !important;" + nl +
"  color: #fff !important;" + nl +
"  font-weight: 700 !important;" + nl +
"  padding: 10px 26px !important;" + nl +
"  border-radius: 8px !important;" + nl +
"  box-shadow: 0 2px 6px rgba(25,135,84,0.25) !important;" + nl +
"}" + nl
)

idx = src.rfind("</style>")
if "Reception Form Settings polish" not in src:
    if idx > 0:
        src = src[:idx] + add + src[idx:]
    else:
        anchor = "{% block content %}"
        if anchor in src:
            src = src.replace(anchor, anchor + nl + "<style>" + nl + add + "</style>", 1)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print(f"polish added to {path}")
else:
    print("already present")
