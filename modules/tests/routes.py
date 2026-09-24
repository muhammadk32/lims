from flask import (
    render_template, request, redirect, url_for, flash, abort
)
from flask_login import login_required, current_user
from sqlalchemy import or_
from extensions import db
from . import tests_bp
from .models import Test, TestCategory
from core.decorators import permission_required
from core.audit import log_action


# ---------- Helpers ----------
def _get_test_or_404(test_id):
    t = Test.query.get(test_id)
    if not t:
        abort(404)
    return t


def _get_or_create_category(name):
    """Return a category by name, creating it if needed."""
    if not name:
        return None
    name = name.strip()
    if not name:
        return None
    cat = TestCategory.query.filter_by(name=name).first()
    if not cat:
        cat = TestCategory(name=name)
        db.session.add(cat)
        db.session.flush()
    return cat


# ============================================================
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
    return redirect(url_for('tests.index', **request.args))
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
    )


# ---------- New ----------
@tests_bp.route('/new', methods=['GET', 'POST'])
@login_required
@permission_required('manage_tests')
def new_test():
    categories = TestCategory.query.order_by(TestCategory.name).all()

    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        name = request.form.get('name', '').strip()

        if not code or not name:
            flash('Code and Name are required.', 'danger')
            return render_template('tests/form.html', test=None, categories=categories, form=request.form)

        # Duplicate check
        if Test.query.filter_by(code=code).first():
            flash(f'A test with code "{code}" already exists.', 'danger')
            return render_template('tests/form.html', test=None, categories=categories, form=request.form)

        category = None
        cat_id = request.form.get('category_id', type=int)
        if cat_id:
            category = TestCategory.query.get(cat_id)

        test = Test(
            code=code,
            name=name,
            category_id=category.id if category else None,
            price=request.form.get('price', type=float) or 0.0,
            normal_range=request.form.get('normal_range', '').strip() or None,
            unit=request.form.get('unit', '').strip() or None,
            description=request.form.get('description', '').strip() or None,
            turnaround_hours=request.form.get('turnaround_hours', type=int) or 24,
        )

        db.session.add(test)
        db.session.commit()

        log_action('create', 'test', test.id, f'Created test {test.code} — {test.name}')

        flash(f'Test "{test.name}" created.', 'success')
        return redirect(url_for('tests.list_tests'))

    return render_template('tests/form.html', test=None, categories=categories, form={})


# ---------- View ----------
@tests_bp.route('/<int:test_id>')
@login_required
def view_test(test_id):
    test = _get_test_or_404(test_id)
    return render_template(
        'tests/view.html',
        test=test,
        ranges=[r for r in (test.reference_ranges or []) if r.is_active],
    )


# ---------- Edit ----------
@tests_bp.route('/<int:test_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('manage_tests')
def edit_test(test_id):
    test = _get_test_or_404(test_id)
    categories = TestCategory.query.order_by(TestCategory.name).all()

    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        name = request.form.get('name', '').strip()

        if not code or not name:
            flash('Code and Name are required.', 'danger')
            return render_template('tests/form.html', test=test, categories=categories, form=request.form)

        # Duplicate check (excluding self)
        existing = Test.query.filter(Test.code == code, Test.id != test.id).first()
        if existing:
            flash(f'Another test already uses code "{code}".', 'danger')
            return render_template('tests/form.html', test=test, categories=categories, form=request.form)

        test.code = code
        test.name = name
        cat_id = request.form.get('category_id', type=int)
        test.category_id = cat_id if cat_id else None
        test.price = request.form.get('price', type=float) or 0.0
        test.normal_range = request.form.get('normal_range', '').strip() or None
        test.unit = request.form.get('unit', '').strip() or None
        test.description = request.form.get('description', '').strip() or None
        test.turnaround_hours = request.form.get('turnaround_hours', type=int) or 24

        db.session.commit()

        log_action('update', 'test', test.id, f'Updated test {test.code}')

        flash('Test updated.', 'success')
        return redirect(url_for('tests.view_test', test_id=test.id))

    return render_template('tests/form.html', test=test, categories=categories, form={})


# ---------- Archive ----------
@tests_bp.route('/<int:test_id>/delete', methods=['POST'])
@login_required
@permission_required('manage_tests')
def delete_test(test_id):
    test = _get_test_or_404(test_id)
    test.is_active = False
    db.session.commit()

    log_action('delete', 'test', test.id, f'Archived test {test.code}')

    flash(f'Test "{test.name}" archived.', 'info')
    return redirect(url_for('tests.list_tests'))


# ---------- Categories ----------
@tests_bp.route('/categories/new', methods=['POST'])
@login_required
@permission_required('manage_tests')
def add_category():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Category name required.', 'danger')
        return redirect(url_for('tests.list_tests'))

    if TestCategory.query.filter_by(name=name).first():
        flash(f'Category "{name}" already exists.', 'warning')
    else:
        db.session.add(TestCategory(name=name))
        db.session.commit()
        flash(f'Category "{name}" added.', 'success')

    return redirect(url_for('tests.list_tests'))

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



# Compatibility: expose `list_tests` name mapped to the same view
list_tests = index
