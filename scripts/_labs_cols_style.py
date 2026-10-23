"""Restyle name/contact/phone columns."""
import io, os
path = os.path.join("templates", "settings", "laboratories.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

add = (
"/* ===== Name/Contact/Phone column styling ===== */" + nl +
".lab-table td:nth-child(1) .edit-input {" + nl +
"  font-size: 1.05rem !important;" + nl +
"  font-weight: 700 !important;" + nl +
"  color: #1a3d7c !important;" + nl +
"  background: #f0f4ff !important;" + nl +
"  letter-spacing: 0.01em;" + nl +
"}" + nl +
".lab-table td:nth-child(2) .edit-input {" + nl +
"  font-size: 0.95rem !important;" + nl +
"  font-weight: 500 !important;" + nl +
"  color: #212529 !important;" + nl +
"  background: #fff !important;" + nl +
"}" + nl +
".lab-table td:nth-child(3) .edit-input {" + nl +
"  font-size: 0.95rem !important;" + nl +
"  font-weight: 600 !important;" + nl +
"  color: #495057 !important;" + nl +
"  background: #f8f9fa !important;" + nl +
"  font-family: Consolas, Monaco, monospace !important;" + nl +
"  letter-spacing: 0.03em;" + nl +
"}" + nl +
"/* Focus states keep brand color */" + nl +
".lab-table td:nth-child(1) .edit-input:focus," + nl +
".lab-table td:nth-child(2) .edit-input:focus," + nl +
".lab-table td:nth-child(3) .edit-input:focus {" + nl +
"  background: #fff !important;" + nl +
"  border-color: #0d6efd !important;" + nl +
"  box-shadow: 0 0 0 3px rgba(13,110,253,0.15) !important;" + nl +
"}" + nl
)

idx = src.rfind("</style>")
if "Name/Contact/Phone column styling" not in src and idx > 0:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("column styles added")
else:
    print("no </style> or already present")
