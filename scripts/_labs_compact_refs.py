"""Compact ref labs: smaller font + fit text inside boxes."""
import io, os
path = os.path.join("templates", "settings", "laboratories.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

add = (
"/* ===== Fit text inside inputs (reference labs) ===== */" + nl +
".lab-table tbody td .edit-input {" + nl +
"  font-size: 0.86rem !important;" + nl +
"  font-weight: 600 !important;" + nl +
"  padding: 6px 10px !important;" + nl +
"  height: 34px !important;" + nl +
"  text-overflow: ellipsis !important;" + nl +
"  overflow: hidden !important;" + nl +
"  white-space: nowrap !important;" + nl +
"}" + nl +
".lab-table tbody td:nth-child(1) .edit-input { font-size: 0.9rem !important; font-weight: 700 !important; }" + nl +
".lab-table tbody td:nth-child(2) .edit-input { font-size: 0.86rem !important; font-weight: 500 !important; }" + nl +
".lab-table tbody td:nth-child(3) .edit-input { font-size: 0.86rem !important; font-weight: 600 !important; font-family: Consolas, monospace !important; }" + nl +
".lab-table tbody td:nth-child(5) .edit-input {" + nl +
"  font-size: 0.82rem !important;" + nl +
"  padding: 6px 8px !important;" + nl +
"}" + nl
)

idx = src.rfind("</style>")
if "Fit text inside inputs" not in src and idx > 0:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("compact styles added")
else:
    print("no </style> or already present")
