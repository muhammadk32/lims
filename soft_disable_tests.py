"""
Soft-disable tests:
- ?status=active|inactive|all filter
- Toggle route POST /tests/<id>/toggle-active
- Template: status dropdown + pause/resume button + greyed row
- CSS: greyed inactive rows + PAUSED badge
"""
import os

# ============================================================
# 1. Route — patch list_tests to support status filter + add toggle
# ============================================================
rp = 'modules/tests/routes.py'
r = open(rp, encoding='utf-8').read()

# --- 1a. Replace list_tests with status-aware version ---
old_fn = '''def list_tests():
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)
    page = request.args.get('page', 1, type=int)

    query = Test.query.filter_by(is_active=True)

    if q:
        like = f'%{q}%'
        query = query.filter(
            or_(
                Test.name.ilike(like),
                Test.code.ilike(like),
            )
        )

    if category_id:
        query = query.filter(Test.category_id == category_id)

    tests = query.order_by(Test.name).paginate(page=page, per_page=15, error_out=False)
    categories = TestCategory.query.order_by(TestCategory.name).all()

    return render_template(
        'tests/list.html',
        tests=tests,
        categories=categories,
        q=q,
        category_id=category_id,
    )'''

new_fn = '''def list_tests():
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)
    status_filter = request.args.get('status', 'active').strip()
    page = request.args.get('page', 1, type=int)

    query = Test.query

    # ----- Status filter -----
    if status_filter == 'active':
        query = query.filter(Test.is_active == True)          # noqa: E712
    elif status_filter == 'inactive':
        query = query.filter(Test.is_active == False)         # noqa: E712
    # 'all' → no filter

    if q:
        like = f'%{q}%'
        query = query.filter(
            or_(
                Test.name.ilike(like),
                Test.code.ilike(like),
            )
        )

    if category_id:
        query = query.filter(Test.category_id == category_id)

    tests = query.order_by(Test.name).paginate(page=page, per_page=15, error_out=False)
    categories = TestCategory.query.order_by(TestCategory.name).all()

    return render_template(
        'tests/list.html',
        tests=tests,
        categories=categories,
        q=q,
        category_id=category_id,
        status_filter=status_filter,
    )'''

if old_fn in r:
    r = r.replace(old_fn, new_fn, 1)
    print('OK  - list_tests updated with status filter')
elif 'status_filter = request.args.get' in r:
    print('SKIP - list_tests already has status filter')
else:
    print('WARN - list_tests anchor not found')

# --- 1b. Add toggle route if missing ---
if 'def toggle_active' not in r:
    new_route = '''

# ============================================================
# Toggle test active (pause / resume)
# ============================================================
@tests_bp.route('/<int:test_id>/toggle-active', methods=['POST'])
@login_required
def toggle_active(test_id):
    """Pause or resume a test. Paused tests are hidden from
    registration but stay in the catalog and past orders."""
    if current_user.role != 'admin':
        flash('Only admins can pause or resume tests.', 'danger')
        return redirect(url_for('tests.list_tests'))

    test = Test.query.get_or_404(test_id)
    test.is_active = not test.is_active
    db.session.commit()

    state = 'resumed' if test.is_active else 'paused'
    flash(f'Test "{test.name}" has been {state}.', 'success')
    return redirect(request.referrer or url_for('tests.list_tests'))
'''
    r = r + new_route
    print('OK  - toggle_active route added')
else:
    print('SKIP - toggle route already exists')

open(rp, 'w', encoding='utf-8').write(r)


# ============================================================
# 2. Template — add status dropdown + pause/resume button + styles
# ============================================================
tp = 'modules/tests/templates/tests/list.html'
t = open(tp, encoding='utf-8').read()

# --- 2a. Status filter in the filter strip ---
old_filter = '''    <div class="lt-field">
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
      </button>'''

new_filter = '''    <div class="lt-field">
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
      </button>'''

if old_filter in t:
    t = t.replace(old_filter, new_filter, 1)
    print('OK  - template: status filter added')
else:
    print('WARN - filter strip anchor not found')

# Change grid to fit 4 columns
t = t.replace(
    '  grid-template-columns: 2fr 1.4fr auto;',
    '  grid-template-columns: 2fr 1.3fr 1.2fr auto;',
    1,
)

# --- 2b. Add CSS for inactive rows + PAUSED badge ---
if '.lt-row-paused' not in t:
    css_block = '''
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
.lt-icon-btn-pause { border-color: #ffc107; color: #664d03; }
.lt-icon-btn-pause:hover { background: #ffc107; color: #664d03; }
.lt-icon-btn-resume { border-color: #198754; color: #198754; }
.lt-icon-btn-resume:hover { background: #198754; color: #fff; }
'''
    # Insert before closing </style>
    end = t.find('</style>')
    if end != -1:
        t = t[:end] + css_block + t[end:]
        print('OK  - template: paused styles added')

# --- 2c. Mark row class + add PAUSED badge ---
old_row = '''      <tr>
        <td><code>{{ t.code }}</code></td>
        <td class="name">{{ t.name }}</td>'''

new_row = '''      <tr class="{% if not t.is_active %}lt-row-paused{% endif %}">
        <td><code>{{ t.code }}</code></td>
        <td class="name">
          {{ t.name }}
          {% if not t.is_active %}
            <span class="lt-badge-paused">Paused</span>
          {% endif %}
        </td>'''

if old_row in t and 'lt-row-paused' not in t.split('old_row')[0][-100:]:
    t = t.replace(old_row, new_row, 1)
    print('OK  - template: row marked with paused state')

# --- 2d. Add pause/resume button in Actions column ---
old_actions = '''            <a href="{{ url_for('tests.edit_test', test_id=t.id) }}"
               class="lt-icon-btn lt-icon-btn-edit" title="Edit">
              <i class="bi bi-pencil"></i>
            </a>'''

new_actions = '''            <a href="{{ url_for('tests.edit_test', test_id=t.id) }}"
               class="lt-icon-btn lt-icon-btn-edit" title="Edit">
              <i class="bi bi-pencil"></i>
            </a>
            <form method="POST" action="{{ url_for('tests.toggle_active', test_id=t.id) }}"
                  class="d-inline">
              {% if t.is_active %}
              <button class="lt-icon-btn lt-icon-btn-pause" title="Pause (hide from registration)">
                <i class="bi bi-pause-fill"></i>
              </button>
              {% else %}
              <button class="lt-icon-btn lt-icon-btn-resume" title="Resume (show in registration)">
                <i class="bi bi-play-fill"></i>
              </button>
              {% endif %}
            </form>'''

if old_actions in t:
    t = t.replace(old_actions, new_actions, 1)
    print('OK  - template: pause/resume button added')
else:
    print('WARN - actions anchor not found')

open(tp, 'w', encoding='utf-8').write(t)


# ============================================================
# 3. Verify
# ============================================================
print()
print('=' * 55)
print('Verify:')
r2 = open(rp, encoding='utf-8').read()
t2 = open(tp, encoding='utf-8').read()
print('  routes: toggle_active:', 'def toggle_active' in r2)
print('  routes: status filter:', 'status_filter' in r2)
print('  template: status dropdown:', 'status_filter' in t2)
print('  template: pause button:', 'toggle_active' in t2)
print('  template: paused CSS:', '.lt-row-paused' in t2)
print('=' * 55)
