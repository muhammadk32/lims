"""Force bigger + bolder inputs on labs table."""
import io, os
path = os.path.join("templates", "settings", "laboratories.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

add = (
"/* ===== Force larger bolder inputs everywhere in labs table ===== */" + nl +
".lab-table tbody td .edit-input {" + nl +
"  font-size: 1.1rem !important;" + nl +
"  font-weight: 700 !important;" + nl +
"  color: #000 !important;" + nl +
"  height: 42px !important;" + nl +
"  padding: 10px 14px !important;" + nl +
"  letter-spacing: 0.01em !important;" + nl +
"}" + nl +
".lab-table tbody td:nth-child(1) .edit-input { color: #1a3d7c !important; background: #e7f1ff !important; }" + nl +
".lab-table tbody td:nth-child(2) .edit-input { color: #212529 !important; background: #fff !important; }" + nl +
".lab-table tbody td:nth-child(3) .edit-input { color: #495057 !important; background: #f8f9fa !important; font-family: Consolas, monospace !important; }" + nl
)

idx = src.rfind("</style>")
if "Force larger bolder inputs everywhere" not in src and idx > 0:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("forced larger inputs")
else:
    print("no </style> or already present")
