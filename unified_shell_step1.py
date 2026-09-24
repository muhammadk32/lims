"""
Approach 1 — Unified Lab Test Settings shell.

New structure:
  templates/test_settings/shell.html       ← header + tab strip + dispatcher
  templates/test_settings/_catalog.html    ← content only
  templates/test_settings/_formats.html    ← content only
  templates/test_settings/_categories.html ← content only
  templates/test_settings/_panels.html     ← content only
  templates/test_settings/_units.html      ← coming-soon stub
  templates/test_settings/_bulk.html       ← coming-soon stub

Routes:
  /tests/                 → unified entry (default: catalog)
  /tests/?tab=formats     → shell renders formats partial
  /settings/tests/formats → 302 → /tests/?tab=formats   (old URLs still work)
"""
import os

TPL = 'templates/test_settings'
os.makedirs(TPL, exist_ok=True)


# ============================================================
# 1. shell.html — the shared chrome
# ============================================================
SHELL = '''{% extends "base.html" %}
{% block title %}Lab Test Settings · {{ branding.lab_name }}{% endblock %}

{% block head %}
  {{ super() }}
  <link rel="stylesheet" href="{{ url_for('static', filename='css/test_settings.css') }}">
{% endblock %}

{% block content %}
<div class="lts-page">

  {# ============ PAGE HEADER ============ #}
  <div class="lts-page-header">
    <div>
      <h1 class="lts-page-title"><i class="bi bi-sliders2"></i> Lab Test Settings</h1>
      <div class="lts-page-subtitle">Configure how tests behave, appear, and print across the system</div>
    </div>
    <div class="lts-page-meta">{{ now.strftime('%d-%b-%Y %I:%M %p') if now else '' }}</div>
  </div>

  {# ============ TABS ============ #}
  <div class="lts-tabs">
    <a href="{{ url_for('tests.index', tab='catalog') }}"
       class="lts-tab {% if tab == 'catalog' %}active{% endif %}">
      <i class="bi bi-clipboard2-pulse"></i> Catalog
    </a>
    <a href="{{ url_for('tests.index', tab='formats') }}"
       class="lts-tab {% if tab == 'formats' %}active{% endif %}">
      <i class="bi bi-sliders2"></i> Formats
    </a>
    <a href="{{ url_for('tests.index', tab='categories') }}"
       class="lts-tab {% if tab == 'categories' %}active{% endif %}">
      <i class="bi bi-tags"></i> Categories
    </a>
    <a href="{{ url_for('tests.index', tab='panels') }}"
       class="lts-tab {% if tab == 'panels' %}active{% endif %}">
      <i class="bi bi-collection"></i> Panels
    </a>
    <a href="{{ url_for('tests.index', tab='units') }}"
       class="lts-tab {% if tab == 'units' %}active{% endif %}">
      <i class="bi bi-rulers"></i> Units &amp; Ranges
    </a>
    <a href="{{ url_for('tests.index', tab='bulk') }}"
       class="lts-tab {% if tab == 'bulk' %}active{% endif %}">
      <i class="bi bi-upload"></i> Bulk Actions
    </a>
  </div>

  {# ============ TAB CONTENT ============ #}
  <div class="lts-content">
    {% if tab == 'formats' %}
      {% include 'test_settings/_formats.html' %}
    {% elif tab == 'categories' %}
      {% include 'test_settings/_categories.html' %}
    {% elif tab == 'panels' %}
      {% include 'test_settings/_panels.html' %}
    {% elif tab == 'units' %}
      {% include 'test_settings/_units.html' %}
    {% elif tab == 'bulk' %}
      {% include 'test_settings/_bulk.html' %}
    {% else %}
      {% include 'test_settings/_catalog.html' %}
    {% endif %}
  </div>

</div>
{% endblock %}

{% block scripts %}
  {{ super() }}
  <script src="{{ url_for('static', filename='js/test_settings.js') }}"></script>
{% endblock %}
'''

with open(os.path.join(TPL, 'shell.html'), 'w', encoding='utf-8') as f:
    f.write(SHELL)
print('OK  - shell.html created')


# ============================================================
# 2. Append unified page styles to test_settings.css
# ============================================================
CSS_PATH = 'static/css/test_settings.css'
css_add = '''

/* ============================================================
   Unified Lab Test Settings shell — page chrome
   ============================================================ */
.lts-page {
  max-width: 1500px;
  margin: 0 auto;
  padding: 10px 20px 30px;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 0.82rem;
  color: #212529;
}
.lts-page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 2px solid #212529;
  padding-bottom: 5px;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}
.lts-page-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
.lts-page-subtitle {
  font-size: 0.76rem;
  color: #6c757d;
  margin-top: 2px;
}
.lts-page-meta {
  font-size: 0.72rem;
  color: #6c757d;
  font-family: Consolas, Monaco, monospace;
}

/* Tab strip */
.lts-tabs {
  display: flex;
  gap: 0;
  border-bottom: 2px solid #212529;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.lts-tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #495057;
  text-decoration: none;
  border: 1px solid #dee2e6;
  border-bottom: none;
  margin-bottom: -2px;
  background: #f8f9fa;
  border-radius: 0;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  transition: background 0.12s;
}
.lts-tab:hover {
  background: #e9ecef;
  color: #212529;
}
.lts-tab.active {
  background: #fff;
  color: #198754;
  border-color: #212529;
  border-bottom-color: #fff;
  margin-bottom: -2px;
  padding-bottom: 8px;
}
.lts-tab i { font-size: 0.9rem; }

.lts-content { padding-top: 4px; }
'''

if os.path.exists(CSS_PATH):
    c = open(CSS_PATH, encoding='utf-8').read()
    if '.lts-page' not in c:
        with open(CSS_PATH, 'a', encoding='utf-8') as f:
            f.write(css_add)
        print('OK  - test_settings.css: shell styles appended')
    else:
        print('SKIP - shell styles already in css')
else:
    with open(CSS_PATH, 'w', encoding='utf-8') as f:
        f.write(css_add)
    print('OK  - test_settings.css created')


# ============================================================
# 3. Create the 6 partials
# ============================================================
# 3a. _catalog.html — the catalog body (from tests/list.html)
CATALOG = '''
{# ============ CATALOG TAB ============ #}
<div class="lt-header">
  <div>
    <h2 class="lt-title"><i class="bi bi-clipboard2-pulse"></i> Lab Tests</h2>
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

<form method="GET" action="{{ url_for('tests.index', tab='catalog') }}" class="lt-filter">
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
    <label>Status</label>
    <select name="status">
      <option value="active" {% if status_filter == 'active' %}selected{% endif %}>Active only</option>
      <option value="inactive" {% if status_filter == 'inactive' %}selected{% endif %}>Paused only</option>
      <option value="all" {% if status_filter == 'all' %}selected{% endif %}>All</option>
    </select>
  </div>
  <div class="lt-field">
    <button type="submit" class="lt-btn lt-btn-primary">
      <i class="bi bi-funnel"></i> Filter
    </button>
    {% if q or category_id %}
    <a href="{{ url_for('tests.index', tab='catalog') }}" class="lt-btn lt-btn-clear ms-1">
      <i class="bi bi-x-lg"></i>
    </a>
    {% endif %}
  </div>
</form>

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
    <tr class="{% if not t.is_active %}lt-row-paused{% endif %}">
      <td><code>{{ t.code }}</code></td>
      <td class="name">
        {{ t.name }}
        {% if not t.is_active %}<span class="lt-badge-paused">Paused</span>{% endif %}
      </td>
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
          <a href="{{ url_for('tests.view_test', test_id=t.id) }}" class="lt-icon-btn lt-icon-btn-view" title="View">
            <i class="bi bi-eye"></i>
          </a>
          {% if current_user.role == 'admin' %}
          <a href="{{ url_for('tests.edit_test', test_id=t.id) }}" class="lt-icon-btn lt-icon-btn-edit" title="Edit">
            <i class="bi bi-pencil"></i>
          </a>
          <form method="POST" action="{{ url_for('tests.toggle_active', test_id=t.id) }}" class="d-inline">
            {% if t.is_active %}
            <button class="lt-icon-btn lt-icon-btn-pause" title="Pause (hide from registration)">
              <i class="bi bi-pause-fill"></i>
            </button>
            {% else %}
            <button class="lt-icon-btn lt-icon-btn-resume" title="Resume (show in registration)">
              <i class="bi bi-play-fill"></i>
            </button>
            {% endif %}
          </form>
          <form method="POST" action="{{ url_for('tests.delete_test', test_id=t.id) }}" class="d-inline"
                onsubmit="return confirm('Archive this test?');">
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

{% if tests.pages > 1 %}
<div style="margin-top:10px; display:flex; justify-content:center;">
  <ul class="pagination" style="font-size:0.78rem; margin:0;">
    <li class="page-item {% if not tests.has_prev %}disabled{% endif %}">
      <a class="page-link" href="{{ url_for('tests.index', tab='catalog', page=tests.prev_num, q=q, category=category_id, status=status_filter) }}">Previous</a>
    </li>
    {% for num in tests.iter_pages(left_edge=1, right_edge=1, left_current=2, right_current=2) %}
      {% if num %}
      <li class="page-item {% if num == tests.page %}active{% endif %}">
        <a class="page-link" href="{{ url_for('tests.index', tab='catalog', page=num, q=q, category=category_id, status=status_filter) }}">{{ num }}</a>
      </li>
      {% else %}
      <li class="page-item disabled"><span class="page-link">…</span></li>
      {% endif %}
    {% endfor %}
    <li class="page-item {% if not tests.has_next %}disabled{% endif %}">
      <a class="page-link" href="{{ url_for('tests.index', tab='catalog', page=tests.next_num, q=q, category=category_id, status=status_filter) }}">Next</a>
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
'''

with open(os.path.join(TPL, '_catalog.html'), 'w', encoding='utf-8') as f:
    f.write(CATALOG)
print('OK  - _catalog.html created')


# 3b. _formats.html
FORMATS = '''
{# ============ FORMATS TAB ============ #}
<div class="tf-header">
  <div>
    <h2 class="tf-title"><i class="bi bi-sliders2"></i> Test Formats</h2>
    <div class="tf-subtitle">Configure how tests behave, appear, and print</div>
  </div>
  <div class="tf-count">{{ tests|length }} test{{ 's' if tests|length != 1 }}</div>
</div>

<form method="GET" action="{{ url_for('tests.index', tab='formats') }}" class="tf-filter">
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
        {% if t.is_panel %}<div class="sub">Panel</div>{% endif %}
      </td>
      <td>
        {% if t.category_ref %}
          <span class="tf-badge tf-badge-cat">{{ t.category_ref.name }}</span>
        {% else %}
          <span class="muted">—</span>
        {% endif %}
      </td>
      <td>{% if t.unit %}{{ t.unit }}{% else %}<span class="muted">—</span>{% endif %}</td>
      <td>{% if t.normal_range %}{{ t.normal_range }}{% else %}<span class="muted">—</span>{% endif %}</td>
      <td>
        <select class="tf-format-select" onchange="updateFormat({{ t.id }}, this.value);">
          {% for key, label in result_formats %}
          <option value="{{ key }}" {% if t.result_format == key %}selected{% endif %}>{{ label }}</option>
          {% endfor %}
        </select>
      </td>
      <td class="center">
        <div class="tf-actions">
          <a href="{{ url_for('tests.view_test', test_id=t.id) }}" class="tf-icon-btn" title="View">
            <i class="bi bi-eye"></i>
          </a>
          <a href="{{ url_for('tests.edit_test', test_id=t.id) }}" class="tf-icon-btn" title="Edit">
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
'''

with open(os.path.join(TPL, '_formats.html'), 'w', encoding='utf-8') as f:
    f.write(FORMATS)
print('OK  - _formats.html created')


# 3c. _categories.html
CATEGORIES = '''
{# ============ CATEGORIES TAB ============ #}
<div class="ts-header">
  <div>
    <h2 class="ts-title"><i class="bi bi-tags"></i> Categories</h2>
    <div class="ts-subtitle">Group tests by department - Hematology, Biochemistry, etc.</div>
  </div>
  <div class="ts-count">{{ categories|length }} categor{{ 'y' if categories|length == 1 else 'ies' }}</div>
</div>

<table class="ts-kpi">
  <tr>
    <td><div class="ts-kpi-label">Categories</div><div class="ts-kpi-value">{{ categories|length }}</div></td>
    <td><div class="ts-kpi-label">Uncategorized Tests</div><div class="ts-kpi-value">{{ uncategorized }}</div></td>
    <td style="text-align:right;">
      <button class="ts-btn ts-btn-primary" data-bs-toggle="modal" data-bs-target="#addCategoryModal2">
        <i class="bi bi-plus-lg"></i> New Category
      </button>
    </td>
  </tr>
</table>

<div class="ts-section">
  <span>All Categories</span>
  <span style="font-weight:400; text-transform:none; letter-spacing:0; opacity:0.85; font-size:0.7rem;">
    Click a row to edit - Delete disabled if category has tests
  </span>
</div>

{% if categories %}
<table class="ts-table">
  <thead>
    <tr>
      <th class="center" style="width: 50px;">#</th>
      <th style="width: 280px;">Name</th>
      <th>Description</th>
      <th class="center" style="width: 100px;">Tests</th>
      <th class="center" style="width: 110px;">Actions</th>
    </tr>
  </thead>
  <tbody>
    {% for c in categories %}
    <tr data-cat-id="{{ c.id }}"
        data-cat-name="{{ c.name|e }}"
        data-cat-desc="{{ (c.description or '')|e }}">
      <td class="center muted">{{ loop.index }}</td>
      <td class="name"><i class="bi bi-circle-fill" style="color:#198754; font-size:0.5rem;"></i> {{ c.name }}</td>
      <td class="muted">{{ c.description or '—' }}</td>
      <td class="center">
        {% set count = test_counts.get(c.id, 0) %}
        <span class="ts-badge {% if count %}ts-badge-cyan{% else %}ts-badge-grey{% endif %}">
          {{ count }} test{{ 's' if count != 1 }}
        </span>
      </td>
      <td class="center">
        <div class="ts-actions">
          <button class="ts-icon-btn btn-edit-cat" data-id="{{ c.id }}"
                  data-name="{{ c.name|e }}" data-desc="{{ (c.description or '')|e }}" title="Edit">
            <i class="bi bi-pencil"></i>
          </button>
          <button class="ts-icon-btn ts-icon-btn-danger btn-del-cat"
                  data-id="{{ c.id }}" data-name="{{ c.name|e }}"
                  {% if count > 0 %}disabled title="Cannot delete - has tests"{% endif %}>
            <i class="bi bi-trash"></i>
          </button>
        </div>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% else %}
<div class="ts-empty">
  <i class="bi bi-inbox fs-3 d-block mb-2"></i>
  No categories yet. Click "New Category" to add one.
</div>
{% endif %}

<div class="modal fade" id="addCategoryModal2">
  <div class="modal-dialog">
    <form id="catForm" method="POST">
      <div class="modal-content" style="border-radius:0;">
        <div class="modal-header">
          <h5 class="modal-title" id="catModalTitle">New Test Category</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div id="catError" class="alert alert-danger d-none"></div>
          <input type="hidden" id="catId">
          <div class="mb-2">
            <label class="form-label small">Name</label>
            <input type="text" id="catName" name="name" class="form-control" required>
          </div>
          <div class="mb-2">
            <label class="form-label small">Description</label>
            <textarea id="catDescription" name="description" class="form-control" rows="2"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" id="catSaveBtn">
            <span id="catSaveText">Create</span>
          </button>
        </div>
      </div>
    </form>
  </div>
</div>

<script>
  if (typeof TestSettings !== 'undefined') {
    TestSettings.initCategories({
      csrf: "{{ csrf_token() if csrf_token is defined else '' }}",
      endpoints: {
        create: "{{ url_for('test_settings.category_create') }}",
        update: "{{ url_for('test_settings.category_update', cat_id=0) }}",
        delete: "{{ url_for('test_settings.category_delete', cat_id=0) }}"
      }
    });
  }
</script>
'''

with open(os.path.join(TPL, '_categories.html'), 'w', encoding='utf-8') as f:
    f.write(CATEGORIES)
print('OK  - _categories.html created')


# 3d. _panels.html
PANELS = '''
{# ============ PANELS TAB ============ #}
<div class="ts-header">
  <div>
    <h2 class="ts-title"><i class="bi bi-collection"></i> Panels</h2>
    <div class="ts-subtitle">Bundle multiple tests under one price - CBC, LFT, RFT</div>
  </div>
  <div class="ts-count">{{ panels|length }} panel{{ 's' if panels|length != 1 }}</div>
</div>

<table class="ts-kpi">
  <tr>
    <td><div class="ts-kpi-label">Total Panels</div><div class="ts-kpi-value">{{ total_panels }}</div></td>
    <td colspan="2" style="padding: 4px 10px;">
      <form method="GET" action="{{ url_for('tests.index', tab='panels') }}"
            style="display:flex; gap:6px; align-items:center;">
        <input type="text" name="q" class="form-control form-control-sm"
               placeholder="Search panels..." value="{{ request.args.get('q','') }}"
               style="border-radius:0; font-size:0.82rem;">
        <button type="submit" class="ts-btn"><i class="bi bi-search"></i></button>
      </form>
    </td>
    <td style="text-align:right;">
      <a href="{{ url_for('test_settings.panel_new') }}" class="ts-btn ts-btn-primary">
        <i class="bi bi-plus-lg"></i> New Panel
      </a>
    </td>
  </tr>
</table>

<div class="ts-section">
  <span>All Panels</span>
  <span style="font-weight:400; text-transform:none; letter-spacing:0; opacity:0.85; font-size:0.7rem;">
    Only the panel price is charged - parameters are free
  </span>
</div>

{% if panels %}
<table class="ts-table">
  <thead>
    <tr>
      <th class="center" style="width: 50px;">#</th>
      <th style="width: 110px;">Code</th>
      <th>Panel Name</th>
      <th style="width: 160px;">Category</th>
      <th class="center" style="width: 100px;">Parameters</th>
      <th class="end" style="width: 100px;">Price</th>
      <th class="center" style="width: 130px;">Actions</th>
    </tr>
  </thead>
  <tbody>
    {% for p in panels %}
    <tr data-panel-id="{{ p.id }}">
      <td class="center muted">{{ loop.index }}</td>
      <td><code>{{ p.code }}</code></td>
      <td>
        <div class="name"><i class="bi bi-collection text-primary"></i> {{ p.name }}</div>
        {% if p.description %}
        <div class="muted" style="font-size:0.68rem;">{{ p.description|truncate(80) }}</div>
        {% endif %}
      </td>
      <td>
        {% if p.category_ref %}
          <span class="ts-badge ts-badge-cyan">{{ p.category_ref.name }}</span>
        {% else %}
          <span class="muted">—</span>
        {% endif %}
      </td>
      <td class="center">
        {% set pc = param_counts.get(p.id, 0) %}
        <span class="ts-badge {% if pc > 0 %}ts-badge-cyan{% else %}ts-badge-grey{% endif %}">
          {{ pc }}
        </span>
      </td>
      <td class="num">{{ p.price | money }}</td>
      <td class="center">
        <div class="ts-actions">
          <a href="{{ url_for('test_settings.panel_edit', panel_id=p.id) }}" class="ts-icon-btn" title="Edit">
            <i class="bi bi-pencil"></i>
          </a>
          <button type="button" class="ts-icon-btn ts-icon-btn-danger btn-delete-panel" title="Delete">
            <i class="bi bi-trash"></i>
          </button>
        </div>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% else %}
<div class="ts-empty">
  <i class="bi bi-collection fs-3 d-block mb-2"></i>
  <div class="fw-semibold">No panels yet</div>
  <div class="small mb-3">Panels bundle several tests under one price - e.g. CBC, LFT, RFT.</div>
  <a href="{{ url_for('test_settings.panel_new') }}" class="ts-btn ts-btn-primary">
    <i class="bi bi-plus-lg"></i> Create Your First Panel
  </a>
</div>
{% endif %}

<div class="test-settings-toast" id="settingsToast" aria-live="polite">
  <span class="toast-message"></span>
</div>

<script>
  if (typeof TestSettings !== 'undefined') {
    TestSettings.initPanels({
      csrf: "{{ csrf_token() if csrf_token is defined else '' }}",
      endpoints: {
        delete: "{{ url_for('test_settings.panel_delete', panel_id=0) }}"
      }
    });
  }
</script>
'''

with open(os.path.join(TPL, '_panels.html'), 'w', encoding='utf-8') as f:
    f.write(PANELS)
print('OK  - _panels.html created')


# 3e. _units.html + _bulk.html (stubs)
STUB = '''
{# ============ STUB TAB ============ #}
<div class="ts-stub">
  <i class="bi bi-{icon} ts-stub-icon"></i>
  <div class="ts-stub-title">{title}</div>
  <div class="ts-stub-text">{text}</div>
  <div class="ts-stub-badge">
    <i class="bi bi-hourglass-split"></i> Coming in a future update
  </div>
</div>
'''

with open(os.path.join(TPL, '_units.html'), 'w', encoding='utf-8') as f:
    f.write(STUB.format(icon='rulers', title='Units &amp; Reference Ranges',
                        text='Manage units (mg/dL, mmol/L, ...) and age/gender-specific reference ranges.'))
print('OK  - _units.html created')

with open(os.path.join(TPL, '_bulk.html'), 'w', encoding='utf-8') as f:
    f.write(STUB.format(icon='upload', title='Bulk Actions',
                        text='Import from Excel/CSV, export the catalog, run cleanup tools.'))
print('OK  - _bulk.html created')


# ============================================================
# 4. Rewrite tests/routes.py — unified index + redirects
# ============================================================
print()
print('=' * 60)
print('Partials + shell done.')
print()
print('Now paste back the CURRENT contents of modules/tests/routes.py')
print('so I can rewrite it as the unified index() with tab dispatch.')
print('=' * 60)
