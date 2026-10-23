"""Fix antibiotics actions + status columns, larger fonts."""
import io, os
path = os.path.join("static", "css", "admin_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== Antibiotics: uniform action buttons ===== */
.admin-content table td .actions-cell,
.admin-content table td[class*="action"],
.admin-content table td:last-child {
  white-space: nowrap !important;
  text-align: center !important;
  vertical-align: middle !important;
}

.admin-content table td:last-child .btn,
.admin-content table td:last-child a,
.admin-content table td:last-child button {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 4px !important;
  min-width: 32px !important;
  height: 30px !important;
  padding: 0 10px !important;
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  border-radius: 6px !important;
  border-width: 2px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.03em;
  text-decoration: none !important;
  vertical-align: middle;
  line-height: 1;
  margin: 0 2px !important;
}

/* Icon-only (delete trash) */
.admin-content table td:last-child .btn:has(> i:only-child),
.admin-content table td:last-child button:has(> i:only-child),
.admin-content table td:last-child a:has(> i:only-child) {
  width: 30px !important;
  min-width: 30px !important;
  padding: 0 !important;
}

/* ===== Antibiotics: bigger ACTIVE pill ===== */
.admin-content table td .badge,
.admin-content table td .pill,
.admin-content table td [class*="status"] {
  display: inline-block !important;
  padding: 5px 14px !important;
  font-size: 0.74rem !important;
  font-weight: 800 !important;
  border-radius: 6px !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
  line-height: 1.1 !important;
}

.admin-content table td .badge.bg-success,
.admin-content table td .status-active,
.admin-content table td [class*="status-active"] {
  background: #198754 !important;
  color: #fff !important;
  border: 2px solid #0f5132 !important;
}

/* ===== Bigger general table font on admin pages ===== */
.admin-content table tbody td {
  font-size: 0.92rem !important;
  padding: 8px 10px !important;
}
.admin-content table thead th {
  font-size: 0.8rem !important;
  padding: 10px 10px !important;
}
"""

if "uniform action buttons" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("actions + status + font fixed")
else:
    print("already present")
