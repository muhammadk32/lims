"""Distinct background color per input column."""
import io, os
path = os.path.join("templates", "settings", "laboratories.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

add = (
"/* ===== Distinct background per input column ===== */" + nl +
".lab-table tbody td:nth-child(1) .edit-input {" + nl +
"  background: #e7f1ff !important;" + nl +
"  border-color: #0d6efd !important;" + nl +
"  color: #0a3d8f !important;" + nl +
"}" + nl +
".lab-table tbody td:nth-child(2) .edit-input {" + nl +
"  background: #e7f7ee !important;" + nl +
"  border-color: #198754 !important;" + nl +
"  color: #0f5132 !important;" + nl +
"}" + nl +
".lab-table tbody td:nth-child(3) .edit-input {" + nl +
"  background: #fff8e1 !important;" + nl +
"  border-color: #ffc107 !important;" + nl +
"  color: #664d03 !important;" + nl +
"}" + nl +
".lab-table tbody td:nth-child(4) .edit-input {" + nl +
"  background: #fdecef !important;" + nl +
"  border-color: #dc3545 !important;" + nl +
"  color: #842029 !important;" + nl +
"}" + nl +
".lab-table tbody td:nth-child(5) .edit-input {" + nl +
"  background: #f4eefe !important;" + nl +
"  border-color: #6f42c1 !important;" + nl +
"  color: #432874 !important;" + nl +
"}" + nl +
".lab-table tbody td:nth-child(1) .edit-input:focus," + nl +
".lab-table tbody td:nth-child(2) .edit-input:focus," + nl +
".lab-table tbody td:nth-child(3) .edit-input:focus," + nl +
".lab-table tbody td:nth-child(4) .edit-input:focus," + nl +
".lab-table tbody td:nth-child(5) .edit-input:focus {" + nl +
"  background: #fff !important;" + nl +
"  box-shadow: 0 0 0 3px rgba(13,110,253,0.2) !important;" + nl +
"}" + nl
)

idx = src.rfind("</style>")
if "Distinct background per input column" not in src and idx > 0:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("colored per-column inputs")
else:
    print("no </style> or already present")
