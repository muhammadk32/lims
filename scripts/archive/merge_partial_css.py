"""Stage 3 — merge partial CSS into shared test_settings.css."""
import os

CSS_PATH = 'static/css/test_settings.css'

CSS_BLOCKS = '''
/* ============================================================
   Tab content — shared styles for all 6 tabs
   (moved from each partial's inline <style> block)
   ============================================================ */

/* ---------- Common header (used by all tabs) ---------- */
.ts-header,
.tf-header,
.lt-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 2px solid #212529;
  padding-bottom: 5px;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}
.ts-title,
.tf-title,
.lt-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
.ts-subtitle,
.tf-subtitle,
.lt-subtitle {
  font-size: 0.76rem;
  color: #6c757d;
  margin-top: 2px;
}
.ts-count,
.tf-count {
  font-size: 0.76rem;
  color: #6c757d;
  font-family: Consolas, Monaco, monospace;
}

/* ---------- Buttons ---------- */
.ts-btn,
.tf-btn,
.lt-btn {
  display: inline-block;
  padding: 4px 12px;
  font-size: 0.74rem;
  font-weight: 600;
  border: 1px solid #212529;
  background: #fff;
  color: #212529;
  text-decoration: none;
  border-radius: 0;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  height: 28px;
  line-height: 1.6;
}
.ts-btn:hover,
.tf-btn:hover,
.lt-btn:hover { background: #f1f3f5; color: #212529; }
.ts-btn-primary,
.tf-btn-primary,
.lt-btn-primary { background: #198754; border-color: #198754; color: #fff; }
.ts-btn-primary:hover,
.tf-btn-primary:hover,
.lt-btn-primary:hover { background: #146c43; color: #fff; }
.ts-btn-danger,
.lt-btn-clear { background: #fff; border-color: #dc3545; color: #dc3545; }
.ts-btn-danger:hover,
.lt-btn-clear:hover { background: #dc3545; color: #fff; }

/* ---------- Filter strip ---------- */
.tf-filter,
.lt-filter {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 8px 10px;
  margin-bottom: 8px;
  display: grid;
  gap: 8px;
  align-items: end;
}
.tf-filter { grid-template-columns: 2fr 1fr 1fr auto; }
.lt-filter { grid-template-columns: 2fr 1.3fr 1.2fr auto; }

.tf-field label,
.lt-field label {
  display: block;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6c757d;
  margin-bottom: 2px;
}
.tf-field input,
.tf-field select,
.lt-field input,
.lt-field select {
  width: 100%;
  padding: 3px 8px;
  border: 1px solid #6c757d;
  border-radius: 0;
  font-size: 0.82rem;
  background: #fff;
  height: 28px;
}
.tf-field input:focus,
.tf-field select:focus,
.lt-field input:focus,
.lt-field select:focus { outline: none; border-color: #198754; }

/* ---------- KPI strip ---------- */
.ts-kpi {
  width: 100%;
  border-collapse: collapse;
  border: 1.5px solid #212529;
  margin-bottom: 10px;
}
.ts-kpi td {
  border: 1px solid #6c757d;
  padding: 8px 14px;
  background: #f8f9fa;
}
.ts-kpi-label {
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6c757d;
  font-weight: 700;
  margin-bottom: 3px;
}
.ts-kpi-value {
  font-size: 1.15rem;
  font-weight: 700;
  font-family: Consolas, Monaco, monospace;
}

/* ---------- Section bar ---------- */
.ts-section,
.tf-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #212529;
  color: #fff;
  padding: 5px 12px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 10px;
}
.tf-section-actions { display: flex; gap: 6px; }
.tf-section .tf-btn {
  border-color: #fff;
  background: transparent;
  color: #fff;
  height: 22px;
  padding: 1px 10px;
  font-size: 0.68rem;
}
.tf-section .tf-btn:hover { background: #495057; color: #fff; }
.tf-section .tf-btn-primary { background: #198754; border-color: #198754; }
.tf-section .tf-btn-primary:hover { background: #146c43; }

/* ---------- Tables ---------- */
.ts-table,
.tf-table,
.lt-table {
  width: 100%;
  border-collapse: collapse;
  border: 1.5px solid #212529;
  border-top: none;
  font-size: 0.78rem;
  background: #fff;
}
.tf-table,
.lt-table { border-top: 1.5px solid #212529; }

.ts-table thead th,
.tf-table thead th,
.lt-table thead th {
  background: #212529;
  color: #fff;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 4px 8px;
  text-align: left;
  border: 1px solid #212529;
  white-space: nowrap;
}
.tf-table thead th,
.ts-table thead th { background: #e9ecef; color: #212529; border: 1px solid #adb5bd; }

.ts-table thead th.center,
.tf-table thead th.center,
.lt-table thead th.center { text-align: center; }
.ts-table thead th.end,
.tf-table thead th.end,
.lt-table thead th.end { text-align: right; }
.ts-table thead th.num,
.tf-table thead th.num,
.lt-table thead th.num { text-align: right; }

.ts-table tbody td,
.tf-table tbody td,
.lt-table tbody td {
  padding: 4px 8px;
  border: 1px solid #dee2e6;
  vertical-align: middle;
}
.ts-table tbody tr:nth-child(even),
.tf-table tbody tr:nth-child(even),
.lt-table tbody tr:nth-child(even) { background: #fbfcfd; }
.ts-table tbody tr:hover,
.tf-table tbody tr:hover,
.lt-table tbody tr:hover { background: #f1f3f5; }

.ts-table code,
.tf-table code,
.lt-table code {
  font-size: 0.72rem;
  font-family: Consolas, Monaco, monospace;
  padding: 0 3px;
  background: #f1f3f5;
  border: 1px solid #dee2e6;
}
.ts-table .name,
.tf-table .name,
.lt-table .name { font-weight: 700; font-size: 0.82rem; }
.ts-table .muted,
.tf-table .muted,
.lt-table .muted { color: #6c757d; font-size: 0.72rem; }
.ts-table .num,
.tf-table .num,
.lt-table .num {
  text-align: right;
  font-family: Consolas, Monaco, monospace;
  font-variant-numeric: tabular-nums;
}
.ts-table .center,
.tf-table .center,
.lt-table .center { text-align: center; }
.tf-table .sub {
  font-size: 0.68rem;
  color: #6c757d;
  font-family: Consolas, Monaco, monospace;
}
.lt-table .price { color: #146c43; font-weight: 600; }

/* ---------- Badges ---------- */
.ts-badge,
.tf-badge,
.lt-badge {
  display: inline-block;
  padding: 1px 6px;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  border-radius: 0;
  text-transform: uppercase;
  color: #fff;
  white-space: nowrap;
}
.ts-badge-grey { background: #e9ecef; color: #495057; }
.ts-badge-cyan,
.tf-badge-cat,
.lt-badge-cat { background: #0dcaf0; color: #055160; }
.ts-badge-green { background: #198754; }
.tf-badge-panel { background: #0d6efd; }

/* ---------- Row actions ---------- */
.ts-actions,
.tf-actions,
.lt-actions-col { display: inline-flex; gap: 3px; }
.ts-icon-btn,
.tf-icon-btn,
.lt-icon-btn {
  display: inline-block;
  padding: 2px 7px;
  font-size: 0.72rem;
  border: 1px solid #6c757d;
  background: #fff;
  color: #212529;
  text-decoration: none;
  border-radius: 0;
  cursor: pointer;
  line-height: 1.3;
}
.ts-icon-btn:hover,
.tf-icon-btn:hover,
.lt-icon-btn:hover { background: #f1f3f5; color: #212529; }
.ts-icon-btn-danger,
.tf-icon-btn-danger,
.lt-icon-btn-danger { border-color: #dc3545; color: #dc3545; }
.ts-icon-btn-danger:hover,
.tf-icon-btn-danger:hover,
.lt-icon-btn-danger:hover { background: #dc3545; color: #fff; }
.lt-icon-btn-view { border-color: #0d6efd; color: #0d6efd; }
.lt-icon-btn-view:hover { background: #0d6efd; color: #fff; }
.lt-icon-btn-edit { border-color: #6c757d; color: #495057; }
.lt-icon-btn-edit:hover { background: #495057; color: #fff; }
.lt-icon-btn-pause { border-color: #ffc107; color: #664d03; }
.lt-icon-btn-pause:hover { background: #ffc107; color: #664d03; }
.lt-icon-btn-resume { border-color: #198754; color: #198754; }
.lt-icon-btn-resume:hover { background: #198754; color: #fff; }

.lt-row-paused { opacity: 0.6; }
.lt-row-paused td { background: #f8f9fa !important; }
.lt-badge-paused {
  background: #6c757d; color: #fff;
  font-size: 0.6rem; font-weight: 700;
  padding: 1px 6px;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  margin-left: 6px;
}

/* ---------- Format select ---------- */
.tf-format-select {
  width: 100%;
  padding: 2px 6px;
  font-size: 0.74rem;
  border: 1px solid #6c757d;
  border-radius: 0;
  background: #fff;
  height: 24px;
}

/* ---------- Empty states ---------- */
.ts-empty,
.tf-empty,
.lt-empty {
  text-align: center;
  padding: 30px 16px;
  color: #6c757d;
  font-style: italic;
  border: 1.5px solid #212529;
  background: #fafbfc;
}
.tf-empty,
.ts-empty { border-top: none; }

/* ---------- Stub pages (Units, Bulk) ---------- */
.ts-stub {
  border: 1.5px solid #212529;
  padding: 40px 20px;
  text-align: center;
  background: #f8f9fa;
}
.ts-stub-icon { font-size: 2.5rem; color: #198754; display: block; margin-bottom: 12px; }
.ts-stub-title { font-size: 1.1rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 6px; }
.ts-stub-text { color: #6c757d; font-size: 0.82rem; margin-bottom: 14px; }
.ts-stub-badge {
  display: inline-block;
  background: #e7f1ff;
  border: 1px solid #0d6efd;
  color: #084298;
  padding: 4px 12px;
  font-size: 0.74rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* ---------- Small responsive tweaks ---------- */
@media (max-width: 900px) {
  .tf-filter, .lt-filter { grid-template-columns: 1fr; }
  .ts-table, .tf-table, .lt-table { font-size: 0.72rem; }
  .ts-table thead th, .ts-table tbody td,
  .tf-table thead th, .tf-table tbody td,
  .lt-table thead th, .lt-table tbody td { padding: 3px 5px; }
}
'''

if os.path.exists(CSS_PATH):
    c = open(CSS_PATH, encoding='utf-8').read()
    if 'Tab content — shared styles' not in c:
        with open(CSS_PATH, 'a', encoding='utf-8') as f:
            f.write(CSS_BLOCKS)
        print('OK  - test_settings.css: tab-content styles appended')
    else:
        print('SKIP - styles already present')
else:
    with open(CSS_PATH, 'w', encoding='utf-8') as f:
        f.write(CSS_BLOCKS)
    print('OK  - test_settings.css created with tab styles')

print()
print('=' * 55)
print('Restart Flask. Hard-refresh (Ctrl+Shift+R) on /tests/.')
print('All tabs should now look dense-classical.')
print('=' * 55)
