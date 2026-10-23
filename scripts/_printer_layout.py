"""Printer Settings: full width + bigger fonts + aligned save button."""
import io, os
path = os.path.join("templates", "settings", "printers.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

add = (
"/* ===== Printer settings layout ===== */" + nl +
".pr-page, .printer-page, .container, .printer-container { max-width: 100% !important; }" + nl +
".pr-header, .printer-header { max-width: 100% !important; margin-bottom: 16px !important; }" + nl +
"table.pr-table, table.printer-table, .pr-body table {" + nl +
"  width: 100% !important;" + nl +
"}" + nl +
"table.pr-table tbody td, table.printer-table tbody td {" + nl +
"  font-size: 0.95rem !important;" + nl +
"  padding: 14px 14px !important;" + nl +
"}" + nl +
"table.pr-table thead th, table.printer-table thead th {" + nl +
"  font-size: 0.86rem !important;" + nl +
"  padding: 14px 14px !important;" + nl +
"}" + nl +
"table.pr-table select, table.printer-table select, .pr-body select {" + nl +
"  font-size: 0.92rem !important;" + nl +
"  padding: 8px 12px !important;" + nl +
"  height: 40px !important;" + nl +
"  border: 2px solid #212529 !important;" + nl +
"  border-radius: 8px !important;" + nl +
"}" + nl +
"/* Save button alignment */" + nl +
".pr-actions, .printer-actions, .form-actions {" + nl +
"  display: flex !important;" + nl +
"  justify-content: flex-end !important;" + nl +
"  padding-top: 14px !important;" + nl +
"}" + nl +
".pr-actions button, .printer-actions button, .pr-body form button[type='submit'] {" + nl +
"  background: linear-gradient(135deg, #198754 0%, #20c997 100%) !important;" + nl +
"  border: 2px solid #198754 !important;" + nl +
"  color: #fff !important;" + nl +
"  font-weight: 700 !important;" + nl +
"  font-size: 0.88rem !important;" + nl +
"  padding: 10px 26px !important;" + nl +
"  border-radius: 8px !important;" + nl +
"  box-shadow: 0 2px 6px rgba(25,135,84,0.25) !important;" + nl +
"}" + nl +
".pr-actions button:hover {" + nl +
"  filter: brightness(1.15);" + nl +
"}" + nl
)

# Append inside last </style> if exists; else add before {% endblock %}
idx = src.rfind("</style>")
if "Printer settings layout" not in src:
    if idx > 0:
        src = src[:idx] + add + src[idx:]
    else:
        # create a new style block at top of content
        anchor = "{% block content %}"
        if anchor in src:
            src = src.replace(anchor, anchor + nl + "<style>" + nl + add + "</style>", 1)
        else:
            print("no style and no content block")
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("printer styles added")
else:
    print("already present")
