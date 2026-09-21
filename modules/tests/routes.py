from flask import (
    render_template, request, redirect, url_for, flash, abort
)
from flask_login import login_required
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


# ---------- List ----------
@tests_bp.route('/')
@login_required
def list_tests():
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
    return render_template('tests/view.html', test=test)


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