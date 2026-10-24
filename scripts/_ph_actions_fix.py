"""Fix action + date column widths in patient history."""
import io, os
path = os.path.join("modules", "patients", "templates", "patients", "history.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# 1) widen actions header
old = '<th class="center" style="width: 1%; white-space: nowrap;">Actions</th>'
new = '<th class="center" style="width: 260px; white-space: nowrap;">Actions</th>'
if old in src:
    src = src.replace(old, new, 1)
    print("actions header widened")
else:
    print("actions header anchor MISS")

# 2) force actions cell width + no wrap on buttons
add = (
"/* ===== Fix action + date columns ===== */" + nl +
".ph-table th.actions-col, .ph-table td.actions-cell {" + nl +
"  width: 260px !important;" + nl +
"  min-width: 260px !important;" + nl +
"  white-space: nowrap !important;" + nl +
"}" + nl +
".ph-row-actions {" + nl +
"  display: flex !important;" + nl +
"  flex-wrap: nowrap !important;" + nl +
"  gap: 4px !important;" + nl +
"}" + nl +
".ph-icon-btn {" + nl +
"  display: inline-flex !important;" + nl +
"  align-items: center !important;" + nl +
"  gap: 4px !important;" + nl +
"  padding: 6px 10px !important;" + nl +
"  font-size: 0.78rem !important;" + nl +
"  font-weight: 700 !important;" + nl +
"  white-space: nowrap !important;" + nl +
"  border: 2px solid #212529 !important;" + nl +
"  border-radius: 6px !important;" + nl +
"  background: #fff !important;" + nl +
"  color: #212529 !important;" + nl +
"  text-decoration: none !important;" + nl +
"  min-width: 68px !important;" + nl +
"}" + nl +
".ph-icon-btn:hover { background: #1a3d7c !important; color: #fff !important; }" + nl +
"/* Date column: prevent wrap */" + nl +
".ph-table td:first-child, .ph-table th:first-child {" + nl +
"  white-space: nowrap !important;" + nl +
"  min-width: 90px !important;" + nl +
"}" + nl
)

idx = src.rfind("</style>")
if "Fix action + date columns" not in src and idx > 0:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("column width CSS added")
else:
    print("no </style> or already present")
