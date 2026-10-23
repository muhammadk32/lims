"""Labs table: bigger fonts + colored action buttons."""
import io, os
path = os.path.join("templates", "settings", "laboratories.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

add = (
"/* ===== Bigger fonts for labs table ===== */" + nl +
".lab-table thead th { font-size: 0.9rem !important; padding: 14px 12px !important; letter-spacing: 0.06em !important; }" + nl +
".lab-table tbody td { font-size: 1rem !important; padding: 12px 10px !important; }" + nl +
".lab-table .edit-input { font-size: 0.95rem !important; height: 36px !important; padding: 8px 12px !important; }" + nl +
".lab-table .pill { font-size: 0.78rem !important; padding: 5px 12px !important; font-weight: 800 !important; }" + nl +
"" + nl +
"/* ===== Colored action buttons ===== */" + nl +
".lab-table td.actions .lab-btn-sm {" + nl +
"  width: 34px !important; height: 34px !important; border-radius: 8px !important;" + nl +
"  font-size: 1rem !important; font-weight: 700 !important; display: inline-flex !important;" + nl +
"  align-items: center !important; justify-content: center !important; border-width: 2px !important;" + nl +
"  transition: all .12s !important;" + nl +
"}" + nl +
"/* Save (green) */" + nl +
".lab-table td.actions .lab-btn-primary {" + nl +
"  background: #198754 !important; border-color: #198754 !important; color: #fff !important;" + nl +
"}" + nl +
".lab-table td.actions .lab-btn-primary:hover { background: #146c43 !important; filter: brightness(1.15); }" + nl +
"/* Toggle/Power (amber) */" + nl +
".lab-table td.actions .lab-btn-warn {" + nl +
"  background: #ffc107 !important; border-color: #e0a800 !important; color: #1a1a1a !important;" + nl +
"}" + nl +
".lab-table td.actions .lab-btn-warn:hover { background: #e0a800 !important; }" + nl +
"/* Delete (red) */" + nl +
".lab-table td.actions .lab-btn-danger {" + nl +
"  background: #dc3545 !important; border-color: #dc3545 !important; color: #fff !important;" + nl +
"}" + nl +
".lab-table td.actions .lab-btn-danger:hover { background: #a71d2a !important; }" + nl
)

# append inside the last </style> in the template
idx = src.rfind("</style>")
if "Bigger fonts for labs table" not in src and idx > 0:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("styles injected")
else:
    print("no </style> or already present")
