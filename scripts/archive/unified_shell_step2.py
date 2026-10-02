"""
Stage 2 — Unified route at /tests/?tab=X
- Adds tests.index() with tab dispatch
- Keeps old list_tests as alias (so url_for('tests.list_tests') still works)
- Old test_settings routes become 302 redirects to /tests/?tab=X
"""
import os

# ============================================================
# 1. Rewrite modules/tests/routes.py — add index() + keep list_tests alias
# ============================================================
rp = 'modules/tests/routes.py'
r = open(rp, encoding='utf-8').read()

# If already unified, skip
if 'def index():' in r and "tab = request.args.get('tab'" in r:
    print('SKIP - tests.index already exists')
else:
    # Insert unified index() right before list_tests()
    old_list = '''# ---------- List ----------
@tests_bp.route('/')
@login_required
def list_tests():'''

    new_block = '''# ============================================================
# Unified Lab Test Settings — all tabs on one page
# ============================================================
@tests_bp.route('/')
@login_required
def index():
    """Lab Test Settings hub with tab dispatch.

    ?tab=catalog    → test catalog (default)
    ?tab=formats    → test result formats
    ?tab=categories → test categories
    ?tab=panels     → test panels
    ?tab=units      → units stub
    ?tab=bulk       → bulk stub
    """
    from datetime import datetime as _dt
    from modules.tests import (
        RESULT_FORMAT_KEYS, RESULT_FORMATS,
    )
    from modules.test_settings.helpers import (
        catalog_stats, format_counts, format_meta,
    )

    tab = request.args.get('tab', 'catalog').strip().lower()
    valid_tabs = ('catalog', 'formats', 'categories', 'panels', 'units', 'bulk')
    if tab not in valid_tabs:
        tab = 'catalog'

    ctx = {
        'tab': tab,
        'now': _dt.now(),
    }

    if tab == 'catalog':
        q = request.args.get('q', '').strip()
        category_id = request.args.get('category', type=int)
        status_filter = request.args.get('status', 'active').strip()
        page = request.args.get('page', 1, type=int)

        query = Test.query
        if status_filter == 'active':
            query = query.filter(Test.is_active == True)  # noqa: E712
        elif status_filter == 'inactive':
            query = query.filter(Test.is_active == False)  # noqa: E712

        if q:
            like = f'%{q}%'
            query = query.filter(or_(Test.name.ilike(like), Test.code.ilike(like)))
        if category_id:
            query = query.filter(Test.category_id == category_id)

        ctx.update({
            'tests': query.order_by(Test.name).paginate(page=page, per_page=15, error_out=False),
            'categories': TestCategory.query.order_by(TestCategory.name).all(),
            'q': q,
            'category_id': category_id,
            'status_filter': status_filter,
        })

    elif tab == 'formats':
        q = request.args.get('q', '').strip()
        fmt_filter = request.args.get('format', '').strip()
        cat_filter = request.args.get('category', '').strip()

        if fmt_filter and fmt_filter not in RESULT_FORMAT_KEYS:
            fmt_filter = ''

        query = Test.query.filter(Test.is_active == True)  # noqa: E712
        if q:
            like = f'%{q}%'
            query = query.filter(or_(Test.code.ilike(like), Test.name.ilike(like)))
        if fmt_filter:
            query = query.filter(Test.result_format == fmt_filter)
        if cat_filter:
            try:
                query = query.filter(Test.category_id == int(cat_filter))
            except (ValueError, TypeError):
                pass

        ctx.update({
            'tests': query.order_by(Test.is_panel.desc(), Test.name.asc()).all(),
            'categories': TestCategory.query.order_by(TestCategory.name.asc()).all(),
            'result_formats': RESULT_FORMATS,
            'format_counts': format_counts(),
            'format_meta': format_meta,
            'stats': catalog_stats(),
            'q': q,
            'fmt_filter': fmt_filter,
            'cat_filter': cat_filter,
        })

    elif tab == 'categories':
        from sqlalchemy import func
        cats = TestCategory.query.order_by(TestCategory.name.asc()).all()
        counts = dict(
            db.session.query(Test.category_id, func.count(Test.id))
            .filter(Test.is_active == True)  # noqa: E712
            .group_by(Test.category_id)
            .all()
        )
        uncategorized = (
            Test.query
            .filter(Test.is_active == True, Test.category_id.is_(None))  # noqa: E712
            .count()
        )
        ctx.update({
            'categories': cats,
            'test_counts': counts,
            'uncategorized': uncategorized,
        })

    elif tab == 'panels':
        from modules.tests import PanelParameter
        from sqlalchemy import func
        q = request.args.get('q', '').strip()
        query = Test.query.filter(Test.is_active == True, Test.is_panel == True)  # noqa: E712
        if q:
            like = f'%{q}%'
            query = query.filter(or_(Test.code.ilike(like), Test.name.ilike(like)))
        panels = query.order_by(Test.name.asc()).all()
        param_counts = dict(
            db.session.query(PanelParameter.panel_id, func.count(PanelParameter.id))
            .group_by(PanelParameter.panel_id)
            .all()
        )
        standalone_tests = (
            Test.query
            .filter(Test.is_active == True, Test.is_panel == False)  # noqa: E712
            .order_by(Test.name.asc())
            .all()
        )
        ctx.update({
            'panels': panels,
            'param_counts': param_counts,
            'categories': TestCategory.query.order_by(TestCategory.name.asc()).all(),
            'standalone_tests': standalone_tests,
            'total_panels': len(panels),
        })

    # 'units' and 'bulk' need no extra context

    return render_template('test_settings/shell.html', **ctx)


@tests_bp.route('/old')
@login_required
def _old_list_redirect():
    """Legacy /tests/old — redirects to unified index."""
    return redirect(url_for('tests.index'))


# ---------- Legacy alias (kept so url_for('tests.list_tests') still works) ----------
@tests_bp.route('/_legacy_list')
@login_required
def list_tests():
    """Alias for tests.index — kept so old url_for() calls keep working."""
    return redirect(url_for('tests.index', **request.args))'''

    if old_list in r:
        r = r.replace(old_list, new_block, 1)
        print('OK  - tests/routes.py: unified index() added')
    else:
        print('WARN - list_tests anchor not found')

    # Make url_for('tests.list_tests') resolve without a path change
    # by adding an endpoint alias
    if 'list_tests = index' not in r:
        # Add at the end of the file
        r += '''


# Compatibility: expose `list_tests` name mapped to the same view
list_tests = index
'''

    open(rp, 'w', encoding='utf-8').write(r)
    print('OK  - tests/routes.py saved')


# ============================================================
# 2. Rewrite modules/test_settings/routes.py — 5 tab routes become redirects
# ============================================================
sp = 'modules/test_settings/routes.py'
s = open(sp, encoding='utf-8').read()

if 'redirect_to_index' in s:
    print('SKIP - test_settings routes already redirected')
else:
    # Add a helper at the top
    helper = '''

# ============================================================
# Redirect helper — old routes now live inside tests.index
# ============================================================
def _redirect_to_index(tab):
    from flask import redirect, url_for, request
    args = {k: v for k, v in request.args.items()}
    args['tab'] = tab
    return redirect(url_for('tests.index', **args))
'''

    # Insert helper after imports (after the last import line, before the first @)
    idx_first_route = s.find('@test_settings_bp.route')
    if idx_first_route == -1:
        print('ERR - no routes found in test_settings/routes.py')
    else:
        s = s[:idx_first_route] + helper.strip() + '\n\n\n' + s[idx_first_route:]

        # Replace formats()
        import re
        s = re.sub(
            r'@test_settings_bp\.route\(\'/formats\'\).*?(?=@test_settings_bp\.route|\Z)',
            '''@test_settings_bp.route('/formats')
def formats():
    return _redirect_to_index('formats')


''',
            s,
            count=1,
            flags=re.DOTALL,
        )

        # Replace categories()
        s = re.sub(
            r'@test_settings_bp\.route\(\'/categories\'\).*?(?=@test_settings_bp\.route|\Z)',
            '''@test_settings_bp.route('/categories')
def categories():
    return _redirect_to_index('categories')


''',
            s,
            count=1,
            flags=re.DOTALL,
        )

        # Replace panels()
        s = re.sub(
            r'@test_settings_bp\.route\(\'/panels\'\).*?(?=@test_settings_bp\.route|\Z)',
            '''@test_settings_bp.route('/panels')
def panels():
    return _redirect_to_index('panels')


''',
            s,
            count=1,
            flags=re.DOTALL,
        )

        # Replace units()
        s = re.sub(
            r'@test_settings_bp\.route\(\'/units\'\).*?(?=@test_settings_bp\.route|\Z)',
            '''@test_settings_bp.route('/units')
def units():
    return _redirect_to_index('units')


''',
            s,
            count=1,
            flags=re.DOTALL,
        )

        # Replace bulk()
        s = re.sub(
            r'@test_settings_bp\.route\(\'/bulk\'\).*?(?=@test_settings_bp\.route|\Z)',
            '''@test_settings_bp.route('/bulk')
def bulk():
    return _redirect_to_index('bulk')


''',
            s,
            count=1,
            flags=re.DOTALL,
        )

        open(sp, 'w', encoding='utf-8').write(s)
        print('OK  - test_settings/routes.py: 5 tab routes now redirect')


print()
print('=' * 60)
print('Stage 2 done.')
print()
print('Restart Flask and test:')
print('  /tests/                 → catalog tab')
print('  /tests/?tab=formats     → formats tab')
print('  /tests/?tab=categories  → categories tab')
print('  /tests/?tab=panels      → panels tab')
print('  /tests/?tab=units       → units stub')
print('  /tests/?tab=bulk        → bulk stub')
print('  /settings/tests/formats → 302 to /tests/?tab=formats')
print('=' * 60)
