# Reorganize topnav:
# - Remove Management Reports from Operations dropdown
# - Remove standalone Cash Summary link
# - Add Management Reports as a top-level dropdown BEFORE Administration
# - Move Cash Summary inside Management Reports
import os

p = 'templates/layout/topnav.html'
s = open(p, encoding='utf-8').read()

# ---------- 1. Remove Management Reports from Operations dropdown ----------
old_op = '''        <a href="{{ url_for('analytics.index') }}" class="dropdown-item {% if request.path.startswith('/analytics') %}active{% endif %}">
          <i class="bi bi-bar-chart-line"></i> Management Reports
        </a>
'''
if old_op in s:
    s = s.replace(old_op, '', 1)
    print('OK  - removed Management Reports from Operations')
else:
    print('WARN - Operations Management Reports link not found')

# ---------- 2. Remove standalone Cash Summary ----------
old_cs = '''    <!-- Cash Summary (was: Billing) -->
    {% if current_user.role in ['admin', 'receptionist'] %}
    <a href="{{ url_for('billing.index') }}"
       class="topnav-link {% if request.endpoint and request.endpoint.startswith('billing.') %}active{% endif %}">
      <i class="bi bi-cash-coin"></i><span>Cash Summary</span>
    </a>
    {% endif %}

'''
if old_cs in s:
    s = s.replace(old_cs, '', 1)
    print('OK  - removed standalone Cash Summary')
else:
    print('WARN - standalone Cash Summary block not found')

# ---------- 3. Insert Management Reports as a top-level dropdown before Administration ----------
old_admin_comment = '    <!-- Administration (admin only) -->'
new_mr = '''    <!-- Management Reports (dropdown) -->
    {% if current_user.role in ['admin', 'doctor', 'receptionist'] %}
    <div class="topnav-item">
      <button type="button" class="topnav-link
        {% if request.path.startswith('/analytics') or (request.endpoint and request.endpoint.startswith('billing.')) %}active{% endif %}">
        <i class="bi bi-bar-chart-line"></i>
        <span>Reports</span>
        <i class="bi bi-chevron-down small"></i>
      </button>
      <div class="topnav-dropdown">

        <div class="dropdown-section">Financial</div>
        <a href="{{ url_for('billing.index') }}"
           class="dropdown-item {% if request.endpoint and request.endpoint.startswith('billing.') %}active{% endif %}">
          <i class="bi bi-cash-coin"></i> Cash Summary
        </a>
        <a href="{{ url_for('analytics.due') }}"
           class="dropdown-item {% if request.endpoint == 'analytics.due' %}active{% endif %}">
          <i class="bi bi-cash-stack"></i> Due Collection
        </a>
        <a href="{{ url_for('analytics.commissions') }}"
           class="dropdown-item {% if request.endpoint and request.endpoint.startswith('analytics.commission') %}active{% endif %}">
          <i class="bi bi-person-badge"></i> Referral Commissions
        </a>

        <div class="dropdown-divider"></div>

        <div class="dropdown-section">Clinical</div>
        <a href="{{ url_for('analytics.doctors') }}"
           class="dropdown-item {% if request.endpoint and 'analytics.doctors' in request.endpoint %}active{% endif %}">
          <i class="bi bi-person-vcard"></i> Doctor / Referral
        </a>
        <a href="{{ url_for('analytics.tests') }}"
           class="dropdown-item {% if request.endpoint and 'analytics.tests' in request.endpoint %}active{% endif %}">
          <i class="bi bi-clipboard2-pulse"></i> Test Volume
        </a>
        <a href="{{ url_for('analytics.abnormal') }}"
           class="dropdown-item {% if request.endpoint == 'analytics.abnormal' %}active{% endif %}">
          <i class="bi bi-exclamation-triangle"></i> Abnormal Results
        </a>

        <div class="dropdown-divider"></div>

        <div class="dropdown-section">Operations</div>
        <a href="{{ url_for('analytics.daily') }}"
           class="dropdown-item {% if request.endpoint == 'analytics.daily' %}active{% endif %}">
          <i class="bi bi-calendar-week"></i> Daily Summary
        </a>

        <div class="dropdown-divider"></div>

        <a href="{{ url_for('analytics.index') }}"
           class="dropdown-item {% if request.endpoint == 'analytics.index' %}active{% endif %}">
          <i class="bi bi-grid"></i> All Reports
        </a>
      </div>
    </div>
    {% endif %}

'''
if old_admin_comment in s:
    s = s.replace(old_admin_comment, new_mr + old_admin_comment, 1)
    print('OK  - Reports dropdown added before Administration')
else:
    print('WARN - Administration comment anchor not found')

open(p, 'w', encoding='utf-8').write(s)

# Verify
s2 = open(p, encoding='utf-8').read()
print()
print('Verify:')
print('  Management Reports removed from Operations:', 'Management Reports' not in s2.split('Laboratory')[0])
print('  Standalone Cash Summary removed:', s2.count('billing.index') == 1)
print('  Reports dropdown present:', '>Reports<' in s2 or '<span>Reports</span>' in s2)
print('  Administration still present:', 'Administration' in s2)
