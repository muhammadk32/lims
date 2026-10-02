"""
Add test-settings tab strip to /tests/ catalog page.
Tabs: Formats · Categories · Panels · Units · Bulk
"""
import os

# ============================================================
# 1. CSS — reuse existing .settings-tabs style if available,
#    or define our own compact version
# ============================================================
tp = 'modules/tests/templates/tests/list.html'
t = open(tp, encoding='utf-8').read()

if 'lts-tabs' not in t:
    # Add CSS right before </style>
    css_block = '''
/* ============================================================
   Lab Test Settings tab strip (shown on catalog page)
   ============================================================ */
.lts-tabs {
  display: flex;
  gap: 0;
  border-bottom: 2px solid #212529;
  margin-bottom: 10px;
  flex-wrap: wrap;
}
.lts-tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  font-size: 0.82rem;
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
'''
    end = t.find('</style>')
    if end != -1:
        t = t[:end] + css_block + t[end:]
        print('OK  - CSS added')

# ============================================================
# 2. Insert tab strip right after the header row
# ============================================================
old_header_end = '''    <div class="lt-actions">
      {% if current_user.role == 'admin' %}
      <button class="lt-btn" data-bs-toggle="modal" data-bs-target="#addCategoryModal">
        <i class="bi bi-tags"></i> New Category
      </button>
      <a href="{{ url_for('tests.new_test') }}" class="lt-btn lt-btn-primary">
        <i class="bi bi-plus-lg"></i> Add Test
      </a>
      {% endif %}
    </div>
  </div>'''

new_header_end = '''    <div class="lt-actions">
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

  {# ============ Settings Tab Strip ============ #}
  {% if current_user.role == 'admin' %}
  <div class="lts-tabs">
    <a href="{{ url_for('tests.list_tests') }}"
       class="lts-tab active">
      <i class="bi bi-clipboard2-pulse"></i> Catalog
    </a>
    <a href="{{ url_for('test_settings.formats') }}" class="lts-tab">
      <i class="bi bi-sliders2"></i> Formats
    </a>
    <a href="{{ url_for('test_settings.categories') }}" class="lts-tab">
      <i class="bi bi-tags"></i> Categories
    </a>
    <a href="{{ url_for('test_settings.panels') }}" class="lts-tab">
      <i class="bi bi-collection"></i> Panels
    </a>
    <a href="{{ url_for('test_settings.units') }}" class="lts-tab">
      <i class="bi bi-rulers"></i> Units &amp; Ranges
    </a>
    <a href="{{ url_for('test_settings.bulk') }}" class="lts-tab">
      <i class="bi bi-upload"></i> Bulk
    </a>
  </div>
  {% endif %}'''

if old_header_end in t:
    t = t.replace(old_header_end, new_header_end, 1)
    print('OK  - tab strip inserted')
else:
    print('WARN - header end anchor not found')
    # Fallback: insert after the closing of lt-header
    anchor = '''<div class="lt-filter">'''
    tabs = '''  {% if current_user.role == 'admin' %}
  <div class="lts-tabs">
    <a href="{{ url_for('tests.list_tests') }}" class="lts-tab active">
      <i class="bi bi-clipboard2-pulse"></i> Catalog
    </a>
    <a href="{{ url_for('test_settings.formats') }}" class="lts-tab">
      <i class="bi bi-sliders2"></i> Formats
    </a>
    <a href="{{ url_for('test_settings.categories') }}" class="lts-tab">
      <i class="bi bi-tags"></i> Categories
    </a>
    <a href="{{ url_for('test_settings.panels') }}" class="lts-tab">
      <i class="bi bi-collection"></i> Panels
    </a>
    <a href="{{ url_for('test_settings.units') }}" class="lts-tab">
      <i class="bi bi-rulers"></i> Units &amp; Ranges
    </a>
    <a href="{{ url_for('test_settings.bulk') }}" class="lts-tab">
      <i class="bi bi-upload"></i> Bulk
    </a>
  </div>
  {% endif %}

'''
    if anchor in t:
        t = t.replace(anchor, tabs + anchor, 1)
        print('OK  - tab strip inserted (fallback)')
    else:
        print('ERR - could not find insertion point')

open(tp, 'w', encoding='utf-8').write(t)


# ============================================================
# 3. Add matching "Catalog" tab to the test_settings/base.html
# ============================================================
bp = 'templates/test_settings/base.html'
if os.path.exists(bp):
    b = open(bp, encoding='utf-8').read()

    if 'Catalog' not in b:
        # Look for existing tabs block
        import re
        # Find where the tab strip is (usually around Formats | Categories | ...)
        # Try to insert a Catalog tab before Formats
        if 'Formats' in b:
            # Insert an anchor link before the first "Formats" tab
            b_new = re.sub(
                r'(<a[^>]*?href="[^"]*formats[^"]*"[^>]*?>)',
                r'<a href="{{ url_for(\'tests.list_tests\') }}" class="...">Catalog</a>\n\1',
                b,
                count=1,
            )
            if b_new != b:
                b = b_new
                open(bp, 'w', encoding='utf-8').write(b)
                print('OK  - Catalog tab added to settings base')
            else:
                print('SKIP - no formats tab found in settings base to anchor to')
        else:
            print('SKIP - formats tab not found in settings base')
    else:
        print('SKIP - Catalog tab already exists in settings base')
else:
    print('WARN - templates/test_settings/base.html not found')


print()
print('=' * 55)
print('Done. Restart Flask and check /tests/')
print('=' * 55)
