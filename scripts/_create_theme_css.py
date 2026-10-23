"""Create global theme CSS."""
import io, os

css = """
/* ============================================================
   GLOBAL THEME — applied everywhere
   Blue + gold, dark borders, rounded corners, hero cards
   ============================================================ */

:root {
  --theme-primary: #1a3d7c;
  --theme-accent: #0d6efd;
  --theme-gold: #ffd166;
  --theme-gold-dark: #ffb703;
  --theme-border-dark: #212529;
  --theme-bg-soft: #f8f9fa;
}

/* ===== Universal dark borders + rounded corners ===== */
.card, .panel, .rec-cell, .bulk-card, .lts-content > div {
  border-radius: 12px !important;
}
.card, .panel, .bulk-card {
  border: 2px solid var(--theme-border-dark) !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}

/* ===== All tables: dark borders, rounded, striped ===== */
table:not(.no-theme) {
  border-collapse: separate !important;
  border-spacing: 0 !important;
  border: 2px solid var(--theme-border-dark) !important;
  border-radius: 10px !important;
  overflow: hidden !important;
}
table:not(.no-theme) thead th {
  background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-accent) 100%) !important;
  color: #fff !important;
  padding: 10px 12px !important;
  text-transform: uppercase;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  border-right: 1px solid var(--theme-border-dark) !important;
  border-bottom: 2px solid var(--theme-border-dark) !important;
}
table:not(.no-theme) thead th:last-child {
  border-right: none !important;
}
table:not(.no-theme) tbody td {
  padding: 8px 12px !important;
  border-bottom: 1px solid var(--theme-border-dark) !important;
  border-right: 1px solid var(--theme-border-dark) !important;
  vertical-align: middle;
}
table:not(.no-theme) tbody td:last-child {
  border-right: none !important;
}
table:not(.no-theme) tbody tr:last-child td {
  border-bottom: none !important;
}
table:not(.no-theme) tbody tr:nth-child(even) td {
  background: #f7f9fc !important;
}
table:not(.no-theme) tbody tr:hover td {
  background: #eaf2ff !important;
}

/* ===== Buttons ===== */
.btn, button:not(.btn-close):not(.no-theme), .btn-primary, a.btn {
  border-radius: 8px !important;
  font-weight: 600;
}
.btn:not(.btn-link) {
  border-width: 2px !important;
}
.btn-primary {
  background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-accent) 100%) !important;
  border-color: var(--theme-primary) !important;
  color: #fff !important;
}
.btn-primary:hover {
  filter: brightness(1.15);
  border-color: var(--theme-primary) !important;
}

/* ===== Form inputs ===== */
.form-control, .form-select {
  border: 2px solid #ced4da !important;
  border-radius: 8px !important;
  transition: border-color 0.12s, box-shadow 0.12s;
}
.form-control:focus, .form-select:focus {
  border-color: var(--theme-accent) !important;
  box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.15) !important;
}

/* ===== Page headings get accent color ===== */
h1, h2, h3, h4 {
  letter-spacing: 0.01em;
}

/* ===== Alerts / messages ===== */
.alert {
  border-radius: 10px !important;
  border-width: 2px !important;
  font-weight: 500;
}

/* ===== Badges ===== */
.badge, .lt-badge, .ts-badge {
  border-radius: 6px !important;
  font-weight: 700;
  letter-spacing: 0.03em;
}

/* ===== Pagination ===== */
.pagination .page-link {
  border-radius: 6px !important;
  border: 2px solid #dee2e6;
  color: var(--theme-primary);
  font-weight: 600;
}
.pagination .page-item.active .page-link {
  background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-accent) 100%);
  border-color: var(--theme-primary);
}

/* ===== Modals ===== */
.modal-content {
  border-radius: 14px !important;
  border: 2px solid var(--theme-border-dark) !important;
  box-shadow: 0 8px 32px rgba(0,0,0,0.25) !important;
}

/* ===== Apply the hero style to first big h1/header sections ===== */
.page-header, .lab-header, .lt-header, .ts-header {
  background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-accent) 100%) !important;
  color: #fff !important;
  padding: 14px 20px !important;
  border-radius: 12px !important;
  margin-bottom: 16px !important;
  border: 2px solid var(--theme-primary) !important;
}
.page-header h1, .page-header h2,
.lab-header h1, .lab-header h2,
.lt-header h1, .lt-header h2,
.ts-header h1, .ts-header h2 {
  color: #fff !important;
}
.page-header .subtitle, .lab-header .lab-sub, .lt-subtitle,
.page-header p, .lab-header p {
  color: rgba(255,255,255,0.9) !important;
}

/* ===== Icons inside headers get gold color ===== */
.page-header i, .lab-header i, .lt-header i, .ts-header i {
  color: var(--theme-gold) !important;
}
"""

path = os.path.join("static", "css", "app_theme.css")
with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(css)
print(f"created {path}")
