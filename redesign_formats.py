# Lab Test Settings — Formats page: dense classical layout
p = 'templates/test_settings/formats.html'
import os

if not os.path.exists(p):
    print('ERR - formats.html not found at', p)
else:
    t = '''{% extends "test_settings/base.html" %}
{% block title %}Test Formats - Lab Test Settings{% endblock %}

{% block settings_content %}
<style>
/* ============================================================
   Test Formats — dense classical layout
   ============================================================ */
.tf-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 2px solid #212529;
  padding-bottom: 5px;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}
.tf-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
.tf-subtitle {
  font-size: 0.76rem;
  color: #6c757d;
  margin-top: 2px;
}
.tf-count {
  font-size: 0.76rem;
  color: #6c757d;
  font-family: Consolas, Monaco, monospace;
}

/* Filter strip */
.tf-filter {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 8px 10px;
  margin-bottom: 8px;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr auto;
  gap: 8px;
  align-items: end;
}
.tf-field label {
  display: block;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6c757d;
  margin-bottom: 2px;
}
.tf-field input,
.tf-field select {
  width: 100%;
  padding: 3px 8px;
  border: 1px solid #6c757d;
  border-radius: 0;
  font-size: 0.82rem;
  background: #fff;
  height: 28px;
}
.tf-field input:focus,
.tf-field select:focus { outline: none; border-color: #198754; }

/* Buttons */
.tf-btn {
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
}
.tf-btn:hover { background: #f1f3f5; color: #212529; }
.tf-btn-primary { background: #198754; border-color: #198754; color: #fff; }
.tf-btn-primary:hover { background: #146c43; color: #fff; }

/* Section bar */
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

/* Table */
.tf-table {
  width: 100%;
  border-collapse: collapse;
  border: 1.5px solid #212529;
  border-top: none;
  font-size: 0.78rem;
  background: #fff;
}
.tf-table thead th {
  background: #e9ecef;
  color: #212529;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 4px 8px;
  text-align: left;
  border: 1px solid #adb5bd;
  white-space: nowrap;
}
.tf-table thead th.center { text-align: center; }
.tf-table thead th.end { text-align: right; }
.tf-table tbody td {
  padding: 4px 8px;
  border: 1px solid #dee2e6;
  vertical-align: middle;
}
.tf-table tbody tr:nth-child(even) { background: #fbfcfd; }
.tf-table tbody tr:hover { background: #f1f3f5; }
.tf-table code {
  font-size: 0.72rem;
  font-family: Consolas, Monaco, monospace;
  padding: 0 3px;
  background: #f1f3f5;
  border: 1px solid #dee2e6;
}
.tf-table .name { font-weight: 700; font-size: 0.82rem; }
.tf-table .sub {
  font-size: 0.68rem;
  color: #6c757d;
  font-family: Consolas, Monaco, monospace;
}
.tf-table .muted { color: #6c757d; font-size: 0.72rem; }
.tf-table .num {
  text-align: right;
  font-family: Consolas, Monaco, monospace;
  font-variant-numeric: tabular-nums;
}
.tf-table .center { text-align: center; }

/* Badges */
.tf-badge {
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
.tf-badge-cat { background: #0dcaf0; color: #055160; }
.tf-badge-panel { background: #0d6efd; }
.tf-badge-unit { background: #e9ecef; color: #495057; }

/* Format select */
.tf-format-select {
  width: 100%;
  padding: 2px 6px;
  font-size: 0.74rem;
  border: 1px solid #6c757d;
  border-radius: 0;
  background: #fff;
  height: 24px;
}

/* Row actions */
.tf-actions { display: inline-flex; gap: 3px; }
.tf-icon-btn {
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
.tf-icon-btn:hover { background: #f1f3f5; color: #212529; }
.tf-icon-btn-danger {
  border-color: #dc3545;
  color: #dc3545;
}
.tf-icon-btn-danger:hover { background: #dc3545; color: #fff; }

/* Empty */
.tf-empty {
  text-align: center;
  padding: 30px 16px;
  color: #6c757d;
  font-style: italic;
  border: 1.5px solid #212529;
  border-top: none;
  background: #fafbfc;
}

@media (max-width: 900px) {
  .tf-filter { grid-template-columns: 1fr; }
  .tf-table { font-size: 0.72rem; }
  .tf-table thead th,
  .tf-table tbody td { padding: 3px 5px; }
}
</style>

<div class="tf-header">
  <div>
    <h1 class="tf-title"><i class="bi bi-sliders2"></i> Test Formats</h1>
    <div class="tf-subtitle">Configure how tests behave, appear, and print</div>
  </div>
  <div class="tf-count">{{ tests|length }} test{{ 's' if tests|length != 1 }}</div>
</div>

{# Filter strip #}
<form method="GET" action="{{ url_for('test_settings.formats') }}" class="tf-filter">
  <div class="tf-field">
    <label>Search</label>
    <input type="text" name="q" value="{{ q or '' }}" placeholder="Search by code or name...">
  </div>
  <div class="tf-field">
    <label>Format</label>
    <select name="format">
      <option value="">All formats</option>
      {% for key, label in result_formats %}
      <option value="{{ key }}" {% if fmt_filter == key %}selected{% endif %}>{{ label }}</option>
      {% endfor %}
    </select>
  </div>
  <div class="tf-field">
    <label>Category</label>
    <select name="category">
      <option value="">All categories</option>
      {% for c in categories %}
      <option value="{{ c.id }}" {% if cat_filter == c.id|string %}selected{% endif %}>{{ c.name }}</option>
      {% endfor %}
    </select>
  </div>
  <div class="tf-field">
    <button type="submit" class="tf-btn tf-btn-primary">
      <i class="bi bi-search"></i> Filter
    </button>
  </div>
</form>

{# Section header with actions #}
<div class="tf-section">
  <span>Tests &amp; Panels ({{ tests|length }} shown)</span>
  <div class="tf-section-actions">
    <a href="{{ url_for('tests.new_test') }}" class="tf-btn tf-btn-primary">
      <i class="bi bi-plus-lg"></i> New Test
    </a>
    <a href="{{ url_for('test_settings.panel_new') }}" class="tf-btn">
      <i class="bi bi-plus-lg"></i> New Panel
    </a>
  </div>
</div>

{% if tests %}
<table class="tf-table">
  <thead>
    <tr>
      <th style="width: 90px;">Code</th>
      <th>Test Name</th>
      <th style="width: 140px;">Category</th>
      <th style="width: 90px;">Unit</th>
      <th style="width: 110px;">Normal Range</th>
      <th style="width: 220px;">Result Format</th>
      <th class="center" style="width: 90px;">Actions</th>
    </tr>
  </thead>
  <tbody>
    {% for t in tests %}
    <tr data-test-id="{{ t.id }}">
      <td><code>{{ t.code }}</code></td>
      <td>
        <div class="name">
          {% if t.is_panel %}<i class="bi bi-collection text-primary"></i> {% endif %}
          {{ t.name }}
        </div>
        {% if t.is_panel %}
        <div class="sub">Panel</div>
        {% endif %}
      </td>
      <td>
        {% if t.category_ref %}
          <span class="tf-badge tf-badge-cat">{{ t.category_ref.name }}</span>
        {% else %}
          <span class="muted">—</span>
        {% endif %}
      </td>
      <td>
        {% if t.unit %}{{ t.unit }}{% else %}<span class="muted">—</span>{% endif %}
      </td>
      <td>
        {% if t.normal_range %}{{ t.normal_range }}{% else %}<span class="muted">—</span>{% endif %}
      </td>
      <td>
        <select class="tf-format-select"
                onchange="updateFormat({{ t.id }}, this.value);">
          {% for key, label in result_formats %}
          <option value="{{ key }}" {% if t.result_format == key %}selected{% endif %}>{{ label }}</option>
          {% endfor %}
        </select>
      </td>
      <td class="center">
        <div class="tf-actions">
          <a href="{{ url_for('tests.view_test', test_id=t.id) }}"
             class="tf-icon-btn" title="View">
            <i class="bi bi-eye"></i>
          </a>
          <a href="{{ url_for('tests.edit_test', test_id=t.id) }}"
             class="tf-icon-btn" title="Edit">
            <i class="bi bi-pencil"></i>
          </a>
        </div>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% else %}
<div class="tf-empty">
  <i class="bi bi-inbox fs-3 d-block mb-2"></i>
  {% if q or fmt_filter or cat_filter %}No tests match the filters.{% else %}No tests yet.{% endif %}
</div>
{% endif %}

<script>
function updateFormat(testId, newFormat) {
  fetch('/settings/tests/formats/' + testId + '/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ result_format: newFormat })
  })
  .then(function (r) { return r.json(); })
  .then(function (data) {
    if (!data.ok) { alert(data.error || 'Update failed'); }
  })
  .catch(function (err) { console.error(err); });
}
</script>
{% endblock %}
'''
    with open(p, 'w', encoding='utf-8') as f:
        f.write(t)
    print('OK  - formats.html rewritten (dense classical)')
