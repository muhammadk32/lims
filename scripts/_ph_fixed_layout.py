"""Force fixed table-layout so actions column width is respected."""
import io, os
path = os.path.join("modules", "patients", "templates", "patients", "history.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== Force fixed layout so column widths are honoured ===== */
.ph-table {
  table-layout: fixed !important;
  width: 100% !important;
}
/* Ensure text inside cells doesn't overflow */
.ph-table tbody td {
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
}
/* Actions column gets a fixed slot */
.ph-table th.actions-col,
.ph-table td.actions-cell {
  width: 280px !important;
  min-width: 280px !important;
  overflow: visible !important;
}
/* Buttons stay side-by-side */
.ph-row-actions {
  display: flex !important;
  flex-wrap: nowrap !important;
  gap: 6px !important;
  justify-content: flex-start !important;
}
.ph-icon-btn {
  flex-shrink: 0 !important;
}
"""

idx = src.rfind("</style>")
if "Force fixed layout so column widths are honoured" not in src:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("fixed layout applied")
