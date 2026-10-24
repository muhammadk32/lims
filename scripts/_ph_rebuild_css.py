"""Rebuild actions CSS cleanly — remove all old rules, add one clean block."""
import io, os, re
path = os.path.join("modules", "patients", "templates", "patients", "history.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# Remove ALL .ph-icon-btn* rules
src = re.sub(r'\.ph-icon-btn[a-z\-]*\s*(:hover)?\s*\{[^}]*\}', '', src)
# Remove ALL .ph-row-actions rules
src = re.sub(r'\.ph-row-actions\s*\{[^}]*\}', '', src)
# Remove ALL .ph-table th.actions-col / td.actions-cell rules
src = re.sub(r'\.ph-table (th\.actions-col|td\.actions-cell)[^{]*\{[^}]*\}', '', src)

# Clean up excessive blank lines
src = re.sub(r'\n{3,}', '\n\n', src)

# Now inject ONE clean block right before </style>
add = """
/* ===== Row actions — FINAL clean block ===== */
.ph-table th.actions-col,
.ph-table td.actions-cell {
  width: 240px !important;
  min-width: 240px !important;
  padding: 8px 10px !important;
  text-align: left !important;
  vertical-align: middle !important;
}
.ph-row-actions {
  display: flex !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
  gap: 6px !important;
  white-space: nowrap !important;
}
.ph-icon-btn {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 4px !important;
  padding: 6px 12px !important;
  min-width: 70px !important;
  height: 30px !important;
  font-size: 0.78rem !important;
  font-weight: 700 !important;
  border: 2px solid #212529 !important;
  background: #fff !important;
  color: #212529 !important;
  text-decoration: none !important;
  border-radius: 6px !important;
  cursor: pointer !important;
  line-height: 1 !important;
  white-space: nowrap !important;
  flex: 0 0 auto !important;
  box-sizing: border-box !important;
}
.ph-icon-btn:hover {
  background: #1a3d7c !important;
  border-color: #1a3d7c !important;
  color: #fff !important;
}
.ph-icon-btn-revisit {
  background: #0d6efd !important;
  border-color: #0d6efd !important;
  color: #fff !important;
}
.ph-icon-btn-revisit:hover { background: #0b5ed7 !important; }
.ph-icon-btn-report {
  background: #198754 !important;
  border-color: #198754 !important;
  color: #fff !important;
}
.ph-icon-btn-report:hover { background: #146c43 !important; }
"""

idx = src.rfind("</style>")
if idx > 0:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("clean actions CSS rebuilt")
