"""Scope theme CSS to Lab Test Settings + topnav dropdown."""
import io, os

css = """
/* ============================================================
   LAB TEST SETTINGS THEME — scoped
   Applies to: /tests/?tab=* pages + Lab Test Settings nav dropdown
   ============================================================ */

:root {
  --theme-primary: #1a3d7c;
  --theme-accent: #0d6efd;
  --theme-gold: #ffd166;
  --theme-gold-dark: #ffb703;
  --theme-border-dark: #212529;
}

/* ===== tables ===== */
table.lt-table, table.ts-table, table.rl-table, table.rdg-table,
table.rle-table, table.rlk-table {
  border-collapse: separate !important;
  border-spacing: 0 !important;
  border: 2px solid var(--theme-border-dark) !important;
  border-radius: 12px !important;
  overflow: hidden !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}

table.lt-table thead th, table.ts-table thead th, table.rl-table thead th,
table.rdg-table thead th, table.rle-table thead th, table.rlk-table thead th {
  background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-accent) 100%) !important;
  color: #fff !important;
  padding: 10px 12px !important;
  text-transform: uppercase;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  border-right: 1px solid var(--theme-border-dark) !important;
  border-bottom: 2px solid var(--theme-border-dark) !important;
}

table.lt-table thead th:last-child, table.ts-table thead th:last-child,
table.rl-table thead th:last-child, table.rdg-table thead th:last-child,
table.rle-table thead th:last-child, table.rlk-table thead th:last-child {
  border-right: none !important;
}

table.lt-table tbody td, table.ts-table tbody td, table.rl-table tbody td,
table.rdg-table tbody td, table.rle-table tbody td, table.rlk-table tbody td {
  padding: 8px 12px !important;
  border-bottom: 1px solid var(--theme-border-dark) !important;
  border-right: 1px solid var(--theme-border-dark) !important;
  vertical-align: middle;
}

table.lt-table tbody td:last-child, table.ts-table tbody td:last-child,
table.rl-table tbody td:last-child, table.rdg-table tbody td:last-child,
table.rle-table tbody td:last-child, table.rlk-table tbody td:last-child {
  border-right: none !important;
}

table.lt-table tbody tr:last-child td, table.ts-table tbody tr:last-child td,
table.rl-table tbody tr:last-child td, table.rdg-table tbody tr:last-child td,
table.rle-table tbody tr:last-child td, table.rlk-table tbody tr:last-child td {
  border-bottom: none !important;
}

table.lt-table tbody tr:nth-child(even) td, table.ts-table tbody tr:nth-child(even) td,
table.rl-table tbody tr:nth-child(even) td, table.rdg-table tbody tr:nth-child(even) td,
table.rle-table tbody tr:nth-child(even) td, table.rlk-table tbody tr:nth-child(even) td {
  background: #f7f9fc !important;
}

table.lt-table tbody tr:hover td, table.ts-table tbody tr:hover td,
table.rl-table tbody tr:hover td, table.rdg-table tbody tr:hover td,
table.rle-table tbody tr:hover td, table.rlk-table tbody tr:hover td {
  background: #eaf2ff !important;
}

/* ===== buttons in lab test settings ===== */
.ts-btn, .lt-btn, .rl-btn, .rdg-sbtn, .rle-btn {
  border-radius: 8px !important;
  border-width: 2px !important;
  font-weight: 700 !important;
}

.ts-btn-primary, .lt-btn-primary, .rle-btn-primary {
  background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-accent) 100%) !important;
  border-color: var(--theme-primary) !important;
  color: #fff !important;
}

.ts-btn-primary:hover, .lt-btn-primary:hover, .rle-btn-primary:hover {
  filter: brightness(1.15);
}

/* ===== filter strips ===== */
.lt-filter, .rl-filter, .rle-filters, .rdg-search {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
  border: 2px solid var(--theme-primary) !important;
  border-radius: 12px !important;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
}

/* ===== Lab Test Settings topnav dropdown ===== */
.topnav-item.tn-tests .topnav-dropdown {
  border: 2px solid var(--theme-primary) !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15) !important;
  overflow: hidden;
}

.topnav-item.tn-tests .topnav-dropdown .dropdown-item {
  border-bottom: 1px solid #dee2e6;
  transition: background 0.1s;
}
.topnav-item.tn-tests .topnav-dropdown .dropdown-item:last-child {
  border-bottom: none;
}
.topnav-item.tn-tests .topnav-dropdown .dropdown-item:hover {
  background: linear-gradient(135deg, #e7f1ff 0%, #d0e2ff 100%);
  color: var(--theme-primary) !important;
}
.topnav-item.tn-tests .topnav-dropdown .dropdown-item.active {
  background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-accent) 100%) !important;
  color: #fff !important;
}

/* ===== tab-strip bullets (bulk nav items) ===== */
.lts-tab {
  border-radius: 8px 8px 0 0 !important;
  border: 2px solid var(--theme-primary) !important;
  border-bottom: none !important;
  font-weight: 700;
  color: var(--theme-primary) !important;
}
.lts-tab.active {
  background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-accent) 100%) !important;
  color: #fff !important;
}

/* ===== page header for test settings ===== */
.lt-header {
  background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-accent) 100%) !important;
  color: #fff !important;
  padding: 14px 20px !important;
  border-radius: 12px !important;
  border: 2px solid var(--theme-primary) !important;
  margin-bottom: 14px !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
}
.lt-header .lt-title, .lt-header .lt-title i,
.lt-header .lt-subtitle {
  color: #fff !important;
}
.lt-header .lt-title i { color: var(--theme-gold) !important; }

.ts-header {
  background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-accent) 100%) !important;
  color: #fff !important;
  padding: 14px 18px !important;
  border-radius: 12px !important;
  border: 2px solid var(--theme-primary) !important;
  margin-bottom: 14px !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
}
.ts-header .ts-title, .ts-header .ts-title i, .ts-header .ts-subtitle,
.ts-header .ts-count {
  color: #fff !important;
}
.ts-header .ts-title i { color: var(--theme-gold) !important; }

/* ===== KPI strips ===== */
.ts-kpi { border-radius: 10px !important; overflow: hidden; }
.ts-kpi td { padding: 8px 12px !important; border: 2px solid var(--theme-primary) !important; }

/* ===== forms inside lab test settings ===== */
.lt-page .form-control, .lt-page .form-select,
.bulk-card .form-control, .bulk-card .form-select {
  border: 2px solid #ced4da !important;
  border-radius: 8px !important;
}
.lt-page .form-control:focus, .lt-page .form-select:focus {
  border-color: var(--theme-accent) !important;
  box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.15) !important;
}

/* ===== info / warning strips ===== */
.alert, .bi-info, .bulk-info {
  border-radius: 10px !important;
  border-width: 2px !important;
}
"""

path = os.path.join("static", "css", "test_settings_theme.css")
with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(css)
print(f"created {path}")
