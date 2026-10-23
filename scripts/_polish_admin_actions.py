"""Polish status badges + action buttons on antibiotics page."""
import io, os
path = os.path.join("static", "css", "admin_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== STATUS pills (ACTIVE / INACTIVE) ===== */
.admin-content .badge,
.admin-content .pill,
.admin-content .status-active,
.admin-content .status-inactive,
table td .badge,
table td .pill,
table td span[class*="status"] {
  display: inline-block !important;
  padding: 4px 12px !important;
  border-radius: 999px !important;
  font-size: 0.68rem !important;
  font-weight: 800 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em;
  border: 2px solid transparent;
  white-space: nowrap;
}

/* ACTIVE (green) */
.admin-content .badge.bg-success,
.admin-content .badge-success,
.admin-content .status-active,
.admin-content .pill-active,
table td .badge.bg-success,
table td .status-active {
  background: #198754 !important;
  color: #fff !important;
  border-color: #0f5132 !important;
  box-shadow: 0 1px 3px rgba(25,135,84,0.3);
}

/* INACTIVE (grey/red) */
.admin-content .badge.bg-secondary,
.admin-content .badge-secondary,
.admin-content .status-inactive,
.admin-content .pill-inactive,
table td .badge.bg-secondary,
table td .status-inactive {
  background: #6c757d !important;
  color: #fff !important;
  border-color: #495057 !important;
  box-shadow: 0 1px 3px rgba(108,117,125,0.3);
}

/* Delete/inactive (red) */
.admin-content .badge.bg-danger,
.admin-content .status-deleted,
table td .badge.bg-danger,
table td .status-deleted {
  background: #dc3545 !important;
  color: #fff !important;
  border-color: #a71d2a !important;
}

/* ===== ACTIONS column: tighter layout ===== */
.actions-col {
  display: inline-flex;
  gap: 4px;
  align-items: center;
  justify-content: center;
  flex-wrap: nowrap;
}

/* Small action buttons */
table td .btn,
table td button.btn,
table td a.btn,
table td .ab-btn,
table td .ab-edit,
table td .ab-delete,
table td .ab-toggle {
  min-height: 28px !important;
  height: 28px !important;
  padding: 2px 10px !important;
  line-height: 1 !important;
  font-size: 0.7rem !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  border-radius: 6px !important;
  gap: 3px !important;
}

/* Icon-only buttons in actions */
table td button:has(> i:only-child),
table td a:has(> i:only-child),
table td .btn-icon {
  width: 28px !important;
  height: 28px !important;
  padding: 0 !important;
  min-width: 28px !important;
}

/* Icon sizing inside buttons */
table td button i,
table td a i {
  font-size: 0.8rem !important;
}

/* Compact row padding */
.admin-content table tbody td {
  padding: 6px 8px !important;
}
"""

if "STATUS pills (ACTIVE / INACTIVE)" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("status + actions polish added")
else:
    print("already present")
