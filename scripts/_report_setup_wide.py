"""Report Page Setup: wider layout + dark bordered rounded fields."""
import io, os
path = os.path.join("templates", "settings", "report_setup.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

add = (
"/* ===== Report Page Setup — wider + dark bordered ===== */" + nl +
".rps-page, .rpt-page, .report-setup-page, .setup-page { max-width: 100% !important; margin: 0 !important; padding: 10px 20px !important; }" + nl +
".rps-header, .rpt-header, .report-setup-header { max-width: 100% !important; }" + nl +
".rps-body, .rpt-body, .report-setup-body { max-width: 100% !important; }" + nl +
"/* Card container around each section */" + nl +
".rps-card, .rpt-card, .section-card, .rps-section, .rpt-section {" + nl +
"  border: 2px solid #212529 !important;" + nl +
"  border-radius: 12px !important;" + nl +
"  overflow: hidden !important;" + nl +
"  background: #fff !important;" + nl +
"  margin-bottom: 16px !important;" + nl +
"  box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;" + nl +
"}" + nl +
"/* Section headers stay dark */" + nl +
".rps-card-hd, .rpt-card-hd, .section-card-hd, .rps-section-hd, .rpt-section-hd {" + nl +
"  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;" + nl +
"  color: #fff !important;" + nl +
"  padding: 10px 16px !important;" + nl +
"  border-bottom: 2px solid #212529 !important;" + nl +
"  font-weight: 800 !important;" + nl +
"  text-transform: uppercase !important;" + nl +
"  letter-spacing: 0.05em !important;" + nl +
"  font-size: 0.82rem !important;" + nl +
"}" + nl +
"/* Every text field / select / textarea inside */" + nl +
".rps-card input[type=\"text\"]," + nl +
".rps-card input[type=\"email\"]," + nl +
".rps-card input[type=\"number\"]," + nl +
".rps-card input[type=\"color\"]," + nl +
".rps-card select," + nl +
".rps-card textarea," + nl +
".rpt-card input[type=\"text\"]," + nl +
".rpt-card input[type=\"email\"]," + nl +
".rpt-card select," + nl +
".report-setup-page input[type=\"text\"]," + nl +
".report-setup-page input[type=\"email\"]," + nl +
".report-setup-page input[type=\"number\"]," + nl +
".report-setup-page input[type=\"color\"]," + nl +
".report-setup-page select," + nl +
".report-setup-page textarea {" + nl +
"  border: 2px solid #212529 !important;" + nl +
"  border-radius: 8px !important;" + nl +
"  padding: 8px 12px !important;" + nl +
"  font-size: 0.95rem !important;" + nl +
"  background: #fff !important;" + nl +
"  height: 38px !important;" + nl +
"}" + nl +
".rps-card textarea, .report-setup-page textarea { height: auto !important; min-height: 64px !important; }" + nl +
".rps-card input[type=\"color\"], .report-setup-page input[type=\"color\"] { padding: 3px !important; }" + nl +
".rps-card input:focus," + nl +
".rps-card select:focus," + nl +
".rps-card textarea:focus," + nl +
".report-setup-page input:focus," + nl +
".report-setup-page select:focus," + nl +
".report-setup-page textarea:focus {" + nl +
"  border-color: #0d6efd !important;" + nl +
"  box-shadow: 0 0 0 3px rgba(13,110,253,0.15) !important;" + nl +
"}" + nl +
"/* Save button */" + nl +
".report-setup-page button[type=\"submit\"]," + nl +
".rps-actions button," + nl +
".rpt-actions button {" + nl +
"  background: linear-gradient(135deg, #198754 0%, #20c997 100%) !important;" + nl +
"  border: 2px solid #198754 !important;" + nl +
"  color: #fff !important;" + nl +
"  font-weight: 700 !important;" + nl +
"  font-size: 0.9rem !important;" + nl +
"  padding: 10px 26px !important;" + nl +
"  border-radius: 8px !important;" + nl +
"  box-shadow: 0 2px 6px rgba(25,135,84,0.25) !important;" + nl +
"}" + nl +
".report-setup-page button[type=\"submit\"]:hover { filter: brightness(1.15); }" + nl +
"/* Preview button (in header) */" + nl +
".rps-header .btn, .report-setup-header .btn {" + nl +
"  background: #fff !important;" + nl +
"  color: #1a3d7c !important;" + nl +
"  border: 2px solid #fff !important;" + nl +
"  border-radius: 8px !important;" + nl +
"  font-weight: 700 !important;" + nl +
"}" + nl +
".rps-header .btn:hover { background: #ffd166 !important; border-color: #ffd166 !important; }" + nl
)

idx = src.rfind("</style>")
if "Report Page Setup — wider" not in src:
    if idx > 0:
        src = src[:idx] + add + src[idx:]
    else:
        anchor = "{% block content %}"
        if anchor in src:
            src = src.replace(anchor, anchor + nl + "<style>" + nl + add + "</style>", 1)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("report setup styles added")
else:
    print("already present")
