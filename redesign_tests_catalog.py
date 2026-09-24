# Lab Tests (catalog) — dense classical layout
p = 'modules/tests/templates/tests/list.html'

t = """{% extends 'base.html' %}
{% block title %}Lab Tests - LabMS{% endblock %}

{% block head %}
<style>
/* ============================================================
   Lab Tests (catalog) - dense classical layout
   ============================================================ */
.lt-page {
  max-width: 1500px;
  margin: 0 auto;
  padding: 10px 20px 30px;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 0.82rem;
  color: #212529;
}
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
.lt-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
.lt-subtitle { font-size: 0.76rem; color: #6c757d; margin-top: 2px; }
.lt-actions { display: flex; gap: 6px; }

/* Filter strip */
.lt-filter {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 8px 10px;
  margin-bottom: 8px;
  display: grid;
  grid-template-columns: 2fr 1.4fr auto;
  gap: 8px;
  align-items: end;
}
.lt-field label {
  display: block;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6c757d;
  margin-bottom: 2px;
}
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
.lt-field input:focus,
.lt-field select:focus { outline: none; border-color: #198754; }

/* Buttons */
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
.lt-btn:hover { background: #f1f3f5; color: #212529; }
.lt-btn-primary { background: #198754; border-color: #198754; color: #fff; }
.lt-btn-primary:hover { background: #146c43; color: #fff; }
.lt-btn-clear { background: #fff; border-color: #dc3545; color: #dc3545; }
.lt-btn-clear:hover { background: #dc3545; color: #fff; }

/* Table */
.lt-table {
  width: 100%;
  border-collapse: collapse;
  border: 1.5px solid #212529;
  font-size: 0.78rem;
  background: #fff;
}
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
.lt-table thead th.center { text-align: center; }
.lt-table thead th.end { text-align: right; }
.lt-table tbody td {
  padding: 4px 8px;
  border: 1px solid #dee2e6;
  vertical-align: middle;
}
.lt-table tbody tr:nth-child(even) { background: #fbfcfd; }
.lt-table tbody tr:hover { background: #f1f3f5; }
.lt-table code {
  font-size: 0.72rem;
  font-family: Consolas, Monaco, monospace;
  padding: 0 3px;
  background: #f1f3f5;
  border: 1px solid #dee2e6;
}
.lt-table .name { font-weight: 700; font-size: 0.82rem; }
.lt-table .muted { color: #6c757d; font-size: 0.74rem; }
.lt-table .num {
  text-align: right;
  font-family: Consolas, Monaco, monospace;
  font-variant-numeric: tabular-nums;
}
.lt-table .center { text-align: center; }
.lt-table .price { color: #146c43; font-weight: 600; }

/* Badges */
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
.lt-badge-cat { background: #0dcaf0; color: #055160; }

/* Row actions */
.lt-actions-col { display: inline-flex; gap: 3px; }
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
.lt-icon-btn:hover { background: #f1f3f5; color: #212529; }
.lt-icon-btn-view { border-color: #0d6efd; color: #0d6efd; }
.lt-icon-btn-view:hover { background: #0d6efd; color: #fff; }
.lt-icon-btn-edit { border-color: #6c757d; color: #495057; }
.lt-icon-btn-edit:hover { background: #495057; color: #fff; }
.lt-icon-btn-danger { border-color: #dc3545; color: #dc3545; }
.lt-icon-btn-danger:hover { background: #dc3545; color: #fff; }

/* Empty */
.lt-empty {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
  font-style: italic;
  border: 1.5px solid #212529;
  background: #fafbfc;
}

@media (max-width: 900px) {
  .lt-filter { grid-template-columns: 1fr; }
  .lt-table { font-size: 0.72rem; }
  .lt-table thead th,
  .lt-table tbody td { padding: 3px 5px; }
}
</style>
{% endblock %}

{% block content %}
<div class="lt-page">

  <div class="lt-header">
    <div>
      <h1 class="lt-title"><i class="bi bi-clipboard2-pulse"></i> Lab Tests</h1>
      <div class="lt-subtitle">Test catalog offered by the laboratory</div>
    </div>
    <div class="lt-actions">
      {% if current_user.role == 'admin' %}
      <button class="lt-btn" data-bs-toggle="modal" data-bs-target="#addCategoryModal">
        <i class="bi bi-tags"></i> New Category
      </button>
      <a href="{{ url_for('tests.new_test') }}" class="lt-btn lt-btn-primary">
        <i class="bi bi-plus-lg"></i> Add Test
      </a>
      {% endif %}
    </div>
  </div>

  {# Filter strip #}
  <form method="GET" action="{{ url_for('tests.list_tests') }}" class="lt-filter">
    <div class="lt-field">
      <label>Search</label>
      <input type="text" name="q" value="{{ q }}" placeholder="Search by name or code...">
    </div>
    <div class="lt-field">
      <label>Category</label>
      <select name="category">
        <option value="">All categories</option>
        {% for c in categories %}
        <option value="{{ c.id }}" {% if category_id == c.id %}selected{% endif %}>{{ c.name }}</option>
        {% endfor %}
      </select>
    </div>
    <div class="lt-field">
      <button type="submit" class="lt-btn lt-btn-primary">
        <i class="bi bi-funnel"></i> Filter
      </button>
      {% if q or category_id %}
      <a href="{{ url_for('tests.list_tests') }}" class="lt-btn lt-btn-clear ms-1">
        <i class="bi bi-x-lg"></i>
      </a>
      {% endif %}
    </div>
  </form>

  {# Table #}
  {% if tests.items %}
  <table class="lt-table">
    <thead>
      <tr>
        <th style="width: 90px;">Code</th>
        <th>Name</th>
        <th style="width: 140px;">Category</th>
        <th class="num" style="width: 90px;">Price</th>
        <th style="width: 90px;">Unit</th>
        <th style="width: 120px;">Normal Range</th>
        <th class="center" style="width: 130px;">Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for t in tests.items %}
      <tr>
        <td><code>{{ t.code }}</code></td>
        <td class="name">{{ t.name }}</td>
        <td>
          {% if t.category_ref %}
            <span class="lt-badge lt-badge-cat">{{ t.category_ref.name }}</span>
          {% else %}
            <span class="muted">—</span>
          {% endif %}
        </td>
        <td class="num price">{{ t.price | money }}</td>
        <td>{% if t.unit %}{{ t.unit }}{% else %}<span class="muted">—</span>{% endif %}</td>
        <td class="muted">{% if t.normal_range %}{{ t.normal_range }}{% else %}—{% endif %}</td>
        <td class="center">
          <div class="lt-actions-col">
            <a href="{{ url_for('tests.view_test', test_id=t.id) }}"
               class="lt-icon-btn lt-icon-btn-view" title="View">
              <i class="bi bi-eye"></i>
            </a>
            {% if current_user.role == 'admin' %}
            <a href="{{ url_for('tests.edit_test', test_id=t.id) }}"
               class="lt-icon-btn lt-icon-btn-edit" title="Edit">
              <i class="bi bi-pencil"></i>
            </a>
            <form method="POST" action="{{ url_for('tests.delete_test', test_id=t.id) }}"
                  class="d-inline" onsubmit="return confirm('Archive this test?');">
              <button class="lt-icon-btn lt-icon-btn-danger" title="Archive">
                <i class="bi bi-trash"></i>
              </button>
            </form>
            {% endif %}
          </div>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  {# Pagination #}
  {% if tests.pages > 1 %}
  <div style="margin-top: 10px; display:flex; justify-content:center;">
    <ul class="pagination" style="font-size: 0.78rem; margin:0;">
      <li class="page-item {% if not tests.has_prev %}disabled{% endif %}">
        <a class="page-link" href="{{ url_for('tests.list_tests', page=tests.prev_num, q=q, category=category_id) }}">Previous</a>
      </li>
      {% for num in tests.iter_pages(left_edge=1, right_edge=1, left_current=2, right_current=2) %}
        {% if num %}
        <li class="page-item {% if num == tests.page %}active{% endif %}">
          <a class="page-link" href="{{ url_for('tests.list_tests', page=num, q=q, category=category_id) }}">{{ num }}</a>
        </li>
        {% else %}
        <li class="page-item disabled"><span class="page-link">…</span></li>
        {% endif %}
      {% endfor %}
      <li class="page-item {% if not tests.has_next %}disabled{% endif %}">
        <a class="page-link" href="{{ url_for('tests.list_tests', page=tests.next_num, q=q, category=category_id) }}">Next</a>
      </li>
    </ul>
  </div>
  {% endif %}

  {% else %}
  <div class="lt-empty">
    <i class="bi bi-inbox fs-3 d-block mb-2"></i>
    {% if q or category_id %}No tests match the filters.{% else %}No tests yet.{% endif %}
  </div>
  {% endif %}

</div>

{# Add Category modal #}
<div class="modal fade" id="addCategoryModal">
  <div class="modal-dialog">
    <form method="POST" action="{{ url_for('tests.add_category') }}">
      <div class="modal-content" style="border-radius:0;">
        <div class="modal-header">
          <h5 class="modal-title">New Test Category</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input type="text" name="name" class="form-control" placeholder="e.g. Hematology" required>
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary">Save</button>
        </div>
      </div>
    </form>
  </div>
</div>
{% endblock %}
"""

with open(p, 'w', encoding='utf-8') as f:
    f.write(t)
print('OK  - tests/list.html rewritten (dense classical)')
