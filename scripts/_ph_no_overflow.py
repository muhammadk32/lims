"""Remove ellipsis/overflow from actions cell."""
import io, os, re
path = os.path.join("modules", "patients", "templates", "patients", "history.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== Override: never clip the actions cell ===== */
.ph-table td.actions-cell {
  overflow: visible !important;
  text-overflow: clip !important;
  white-space: nowrap !important;
}
.ph-table tbody td.actions-cell > .ph-row-actions,
.ph-table tbody td.actions-cell a.ph-icon-btn {
  overflow: visible !important;
}
/* Also kill the generic td ellipsis rule for action cells */
.ph-table tbody td.actions-cell,
.ph-table tbody td.actions-cell * {
  text-overflow: clip !important;
}
"""

idx = src.rfind("</style>")
if "never clip the actions cell" not in src and idx > 0:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("overflow override added")
