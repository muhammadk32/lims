"""Create admin_theme.css — same look as Lab Test Settings."""
import io, os

css = """
/* ============================================================
   ADMIN THEME — applied to Administration pages
   ============================================================ */

:root {
  --admin-primary: #1a3d7c;
  --admin-accent: #0d6efd;
  --admin-gold: #ffd166;
  --admin-border: #212529;
}

/* ===== Page headers (any h1/h2 sitting in a card) ===== */
.lab-header, .rs-header, .ref-header, .user-header,
.page-header, .admin-header {
  background: linear-gradient(135deg, var(--admin-primary) 0%, var(--admin-accent) 100%) !important;
  color: #fff !important;
  padding: 14px 20px !important;
  border-radius: 12px !important;
  border: 2px solid var(--admin-primary) !important;
  margin-bottom: 14px !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
}
.lab-header h1, .lab-header h2,
.rs-header h1, .rs-header h2,
.ref-header h1, .ref-header h2,
.user-header h1, .user-header h2,
.page-header h1, .page-header h2,
.admin-header h1, .admin-header h2 {
  color: #fff !important;
}
.lab-header i, .rs-header i, .ref-header i,
.user-header i, .page-header i, .admin-header i {
  color: var(--admin-gold) !important;
}
.lab-sub, .rs-sub, .ref-sub, .user-sub, .page-sub {
  color: rgba(255,255,255,0.9) !important;
}

/* ===== All tables inside admin pages ===== */
table:not(.no-theme):not(.ts-kpi):not(.modal-dialog *):not(.pagination *) {
  border-collapse: separate !important;
  border-spacing: 0 !important;
  border: 2px solid var(--admin-border) !important;
  border-radius: 12px !important;
  overflow: hidden !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}
table:not(.no-theme):not(.ts-kpi) thead th {
  background: linear-gradient(135deg, var(--admin-primary) 0%, var(--admin-accent) 100%) !important;
  color: #fff !important;
  padding: 10px 12px !important;
  text-transform: uppercase;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  border-right: 1px solid var(--admin-border) !important;
  border-bottom: 2px solid var(--admin-border) !important;
}
table:not(.no-theme):not(.ts-kpi) thead th:last-child {
  border-right: none !important;
}
table:not(.no-theme):not(.ts-kpi) tbody td {
  padding: 8px 12px !important;
  border-bottom: 1px solid var(--admin-border) !important;
  border-right: 1px solid var(--admin-border) !important;
  vertical-align: middle;
}
table:not(.no-theme):not(.ts-kpi) tbody td:last-child {
  border-right: none !important;
}
table:not(.no-theme):not(.ts-kpi) tbody tr:last-child td {
  border-bottom: none !important;
}
table:not(.no-theme):not(.ts-kpi) tbody tr:nth-child(even) td {
  background: #f7f9fc !important;
}
table:not(.no-theme):not(.ts-kpi) tbody tr:hover td {
  background: #eaf2ff !important;
}

/* ===== Buttons ===== */
.btn-primary:not(.no-theme) {
  background: linear-gradient(135deg, var(--admin-primary) 0%, var(--admin-accent) 100%) !important;
  border: 2px solid var(--admin-primary) !important;
  color: #fff !important;
  border-radius: 8px !important;
  font-weight: 700 !important;
}
.btn-primary:not(.no-theme):hover {
  filter: brightness(1.15);
  border-color: var(--admin-primary) !important;
}
.btn-outline-primary {
  border: 2px solid var(--admin-primary) !important;
  color: var(--admin-primary) !important;
  border-radius: 8px !important;
  font-weight: 700 !important;
}

/* ===== Forms ===== */
.form-control:not(.no-theme), .form-select:not(.no-theme) {
  border: 2px solid #ced4da !important;
  border-radius: 8px !important;
}
.form-control:not(.no-theme):focus, .form-select:not(.no-theme):focus {
  border-color: var(--admin-accent) !important;
  box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.15) !important;
}

/* ===== Cards ===== */
.card:not(.no-theme), .panel:not(.no-theme) {
  border: 2px solid var(--admin-border) !important;
  border-radius: 12px !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}

/* ===== Alerts ===== */
.alert {
  border-radius: 10px !important;
  border-width: 2px !important;
  font-weight: 500;
}

/* ===== Modals ===== */
.modal-content:not(.no-theme) {
  border-radius: 14px !important;
  border: 2px solid var(--admin-border) !important;
  box-shadow: 0 8px 32px rgba(0,0,0,0.25) !important;
}

/* ===== Pills / Badges ===== */
.badge, .pill, .pill-active, .pill-inactive {
  border-radius: 8px !important;
  font-weight: 700;
  letter-spacing: 0.03em;
}
"""

path = os.path.join("static", "css", "admin_theme.css")
with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(css)
print(f"created {path}")
