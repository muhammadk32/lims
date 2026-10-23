"""Referrals page: dark bordered rounded input boxes."""
import io, os
path = os.path.join("templates", "settings", "referrals.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

add = (
"/* ===== Referrals page: all inputs bordered + rounded ===== */" + nl +
".app-content input[type=\"text\"]," + nl +
".app-content input[type=\"email\"]," + nl +
".app-content input[type=\"number\"]," + nl +
".app-content input[type=\"search\"]," + nl +
".app-content select," + nl +
".app-content textarea {" + nl +
"  border: 2px solid #212529 !important;" + nl +
"  border-radius: 8px !important;" + nl +
"  padding: 8px 12px !important;" + nl +
"  font-size: 0.95rem !important;" + nl +
"  background: #fff !important;" + nl +
"  height: 40px !important;" + nl +
"  box-sizing: border-box !important;" + nl +
"}" + nl +
".app-content input:focus," + nl +
".app-content select:focus," + nl +
".app-content textarea:focus {" + nl +
"  border-color: #0d6efd !important;" + nl +
"  box-shadow: 0 0 0 3px rgba(13,110,253,0.15) !important;" + nl +
"  outline: none !important;" + nl +
"}" + nl +
"/* Commission % input inside table (narrower) */" + nl +
".app-content table input[type=\"number\"] {" + nl +
"  width: 90px !important;" + nl +
"  height: 36px !important;" + nl +
"  padding: 6px 8px !important;" + nl +
"  text-align: right !important;" + nl +
"}" + nl +
"/* Make the commission % column cleaner */" + nl +
".app-content table td:nth-last-child(2) {" + nl +
"  text-align: center !important;" + nl +
"}" + nl +
"/* Save/tick buttons inside the table */" + nl +
".app-content table button[type=\"submit\"].btn-success," + nl +
".app-content table .btn-success {" + nl +
"  background: #198754 !important;" + nl +
"  border: 2px solid #0f5132 !important;" + nl +
"  color: #fff !important;" + nl +
"  border-radius: 8px !important;" + nl +
"  width: 36px !important;" + nl +
"  height: 36px !important;" + nl +
"  padding: 0 !important;" + nl +
"  display: inline-flex !important;" + nl +
"  align-items: center !important;" + nl +
"  justify-content: center !important;" + nl +
"}" + nl +
".app-content table .btn-success:hover { filter: brightness(1.15); }" + nl +
"/* Delete/trash */" + nl +
".app-content table button[type=\"submit\"].btn-danger," + nl +
".app-content table .btn-danger {" + nl +
"  background: #fff !important;" + nl +
"  border: 2px solid #dc3545 !important;" + nl +
"  color: #dc3545 !important;" + nl +
"  border-radius: 8px !important;" + nl +
"  width: 36px !important;" + nl +
"  height: 36px !important;" + nl +
"  padding: 0 !important;" + nl +
"  display: inline-flex !important;" + nl +
"  align-items: center !important;" + nl +
"  justify-content: center !important;" + nl +
"}" + nl +
".app-content table .btn-danger:hover { background: #dc3545 !important; color: #fff !important; }" + nl +
"/* Add button */" + nl +
".app-content .btn-primary {" + nl +
"  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;" + nl +
"  border: 2px solid #1a3d7c !important;" + nl +
"  border-radius: 8px !important;" + nl +
"  font-weight: 700 !important;" + nl +
"  height: 40px !important;" + nl +
"  padding: 0 20px !important;" + nl +
"}" + nl
)

idx = src.rfind("</style>")
if "Referrals page: all inputs bordered" not in src:
    if idx > 0:
        src = src[:idx] + add + src[idx:]
    else:
        anchor = "{% block content %}"
        if anchor in src:
            src = src.replace(anchor, anchor + nl + "<style>" + nl + add + "</style>", 1)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("referrals styles added")
else:
    print("already present")
