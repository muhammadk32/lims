"""
Soft-disable tests: pause button + status filter on /tests/
- is_active column already exists
- Toggle route: POST /tests/<id>/toggle-active
- Filter: ?status=active|inactive|all
- Greyed rows + PAUSED badge for disabled tests
"""
import os

# ============================================================
# 1. Route — POST /tests/<id>/toggle-active
# ============================================================
rp = 'modules/tests/routes.py'
r = open(rp, encoding='utf-8').read()

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
    from core.decorators import admin_required
    from .models import Test

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
    open(rp, 'w', encoding='utf-8').write(r + new_route)
    print('OK  - routes.py: toggle_active added')
else:
    print('SKIP - route already exists')


# ============================================================
# 2. Update list_tests to support ?status= filter
# ============================================================
if 'status_filter' not in r:
    # Find list_tests and patch it
    old_block = """    tests = (Test.query
             .filter(Test.is_active == True)"""

    # Look for a different possible form
    idx = r.find('def list_tests')
    if idx != -1:
        end = r.find(chr(10) + '@tests_bp', idx + 1)
        if end == -1:
            end = len(r)
        fn = r[idx:end]
        print()
        print('=== current list_tests() ===')
        print(fn[:1200])
        print('=== end ===')
        print()
        print('To add the status filter, I need to see the current query.')
        print('Please paste the output above and I will ship the rest.')
else:
    print('SKIP - status filter already present')


# ============================================================
# 3. CSS + template placeholder (ships after I see list_tests)
# ============================================================
print()
print('=' * 55)
print('Route added. Now I need to see the current list_tests()')
print('function to add the ?status= filter correctly.')
print('=' * 55)
