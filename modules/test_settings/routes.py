"""
Lab Test Settings — routes.

All routes are admin-only via the 'manage_test_settings' permission.
"""
from flask import (
    render_template, request, redirect, url_for, flash, abort, jsonify,
)
from flask_login import login_required, current_user
from sqlalchemy import func

from extensions import db
from core.decorators import manage_test_settings_required
from modules.tests import (
    Test, TestCategory, PanelParameter,
    RESULT_FORMAT_KEYS, RESULT_FORMATS,
)
from . import test_settings_bp
from .helpers import catalog_stats, format_counts, format_meta


# ============================================================
# Blueprint-wide guard
# ============================================================
@test_settings_bp.before_request
@login_required
@manage_test_settings_required
def _guard():
    return None


# ============================================================
# Root
# ============================================================
@test_settings_bp.route('/')
def index():
    return redirect(url_for('test_settings.formats'))


# ============================================================
# Tab 1 — Formats
# ============================================================
@test_settings_bp.route('/formats')
def formats():
    q = request.args.get('q', '').strip()
    fmt_filter = request.args.get('format', '').strip()
    cat_filter = request.args.get('category', '').strip()

    query = Test.query.filter(Test.is_active == True)   # noqa: E712

    if q:
        like = f'%{q}%'
        query = query.filter(
            (Test.code.ilike(like)) | (Test.name.ilike(like))
        )

    if fmt_filter and fmt_filter in RESULT_FORMAT_KEYS:
        query = query.filter(Test.result_format == fmt_filter)

    if cat_filter:
        try:
            query = query.filter(Test.category_id == int(cat_filter))
        except (ValueError, TypeError):
            pass

    tests = query.order_by(Test.is_panel.desc(), Test.name.asc()).all()
    categories = TestCategory.query.order_by(TestCategory.name.asc()).all()

    return render_template(
        'test_settings/formats.html',
        active_tab='formats',
        tests=tests,
        categories=categories,
        result_formats=RESULT_FORMATS,
        format_counts=format_counts(),
        format_meta=format_meta,
        stats=catalog_stats(),
        q=q,
        fmt_filter=fmt_filter,
        cat_filter=cat_filter,
    )


@test_settings_bp.route('/formats/<int:test_id>/update', methods=['POST'])
def format_update(test_id):
    test = Test.query.get_or_404(test_id)

    data = request.get_json(silent=True) or {}
    new_format = (data.get('result_format') or '').strip()

    if new_format not in RESULT_FORMAT_KEYS:
        return jsonify({'ok': False, 'error': 'Invalid format'}), 400

    was_panel = test.is_panel
    test.result_format = new_format

    if new_format == 'panel':
        test.is_panel = True
        test.unit = None
        test.normal_range = None
    else:
        test.is_panel = False

    db.session.commit()

    return jsonify({
        'ok': True,
        'test_id': test.id,
        'result_format': test.result_format,
        'is_panel': test.is_panel,
        'panel_changed': (was_panel != test.is_panel),
        'label': dict(RESULT_FORMATS).get(test.result_format, test.result_format),
    })


# ============================================================
# Tab 2 — Categories
# ============================================================
@test_settings_bp.route('/categories')
def categories():
    cats = TestCategory.query.order_by(TestCategory.name.asc()).all()

    counts = dict(
        db.session.query(Test.category_id, func.count(Test.id))
        .filter(Test.is_active == True)             # noqa: E712
        .group_by(Test.category_id)
        .all()
    )
    uncategorized = (
        Test.query
        .filter(Test.is_active == True, Test.category_id.is_(None))   # noqa: E712
        .count()
    )

    return render_template(
        'test_settings/categories.html',
        active_tab='categories',
        categories=cats,
        test_counts=counts,
        uncategorized=uncategorized,
        total_categories=len(cats),
    )


@test_settings_bp.route('/categories/create', methods=['POST'])
def category_create():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    description = (data.get('description') or '').strip()

    if not name:
        return jsonify({'ok': False, 'error': 'Name is required'}), 400
    if len(name) > 80:
        return jsonify({'ok': False, 'error': 'Name too long (max 80 chars)'}), 400

    existing = TestCategory.query.filter(
        func.lower(TestCategory.name) == name.lower()
    ).first()
    if existing:
        return jsonify({'ok': False, 'error': f'Category "{name}" already exists'}), 400

    cat = TestCategory(name=name, description=description or None)
    db.session.add(cat)
    db.session.commit()

    return jsonify({'ok': True, 'id': cat.id, 'name': cat.name,
                    'description': cat.description or ''})


@test_settings_bp.route('/categories/<int:cat_id>/update', methods=['POST'])
def category_update(cat_id):
    cat = TestCategory.query.get_or_404(cat_id)

    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    description = (data.get('description') or '').strip()

    if not name:
        return jsonify({'ok': False, 'error': 'Name is required'}), 400

    dup = TestCategory.query.filter(
        func.lower(TestCategory.name) == name.lower(),
        TestCategory.id != cat.id,
    ).first()
    if dup:
        return jsonify({'ok': False, 'error': f'Category "{name}" already exists'}), 400

    cat.name = name
    cat.description = description or None
    db.session.commit()

    return jsonify({'ok': True, 'id': cat.id, 'name': cat.name,
                    'description': cat.description or ''})


@test_settings_bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
def category_delete(cat_id):
    cat = TestCategory.query.get_or_404(cat_id)

    test_count = Test.query.filter(Test.category_id == cat.id).count()
    if test_count > 0:
        return jsonify({
            'ok': False,
            'error': f'Cannot delete — {test_count} test(s) still use this category.',
        }), 400

    db.session.delete(cat)
    db.session.commit()
    return jsonify({'ok': True, 'id': cat_id})


# ============================================================
# Tab 3 — Units (stub)
# ============================================================
@test_settings_bp.route('/units')
def units():
    return render_template(
        'test_settings/coming_soon.html',
        active_tab='units',
        tab_name='Units & Reference Ranges',
        tab_icon='bi-rulers',
        description='Manage units (mg/dL, mmol/L, …) and age/gender-specific reference ranges.',
    )


# ============================================================
# Tab 4 — Panels (FULL)
# ============================================================
@test_settings_bp.route('/panels')
def panels():
    """List all panels with their parameter counts."""
    q = request.args.get('q', '').strip()

    query = Test.query.filter(
        Test.is_active == True,                         # noqa: E712
        Test.is_panel == True,                          # noqa: E712
    )
    if q:
        like = f'%{q}%'
        query = query.filter(
            (Test.code.ilike(like)) | (Test.name.ilike(like))
        )

    panels = query.order_by(Test.name.asc()).all()

    # Parameter counts per panel
    param_counts = dict(
        db.session.query(PanelParameter.panel_id, func.count(PanelParameter.id))
        .group_by(PanelParameter.panel_id)
        .all()
    )

    categories = TestCategory.query.order_by(TestCategory.name.asc()).all()

    # Standalone tests available for adding to panels
    standalone_tests = (
        Test.query
        .filter(Test.is_active == True, Test.is_panel == False)   # noqa: E712
        .order_by(Test.name.asc())
        .all()
    )

    return render_template(
        'test_settings/panels.html',
        active_tab='panels',
        panels=panels,
        param_counts=param_counts,
        categories=categories,
        standalone_tests=standalone_tests,
        total_panels=len(panels),
    )


@test_settings_bp.route('/panels/new', methods=['GET'])
def panel_new():
    """Create-panel page."""
    categories = TestCategory.query.order_by(TestCategory.name.asc()).all()
    standalone_tests = (
        Test.query
        .filter(Test.is_active == True, Test.is_panel == False)   # noqa: E712
        .order_by(Test.name.asc())
        .all()
    )
    return render_template(
        'test_settings/panel_edit.html',
        active_tab='panels',
        panel=None,
        selected_ids=[],
        categories=categories,
        standalone_tests=standalone_tests,
        mode='create',
    )


@test_settings_bp.route('/panels/<int:panel_id>/edit', methods=['GET'])
def panel_edit(panel_id):
    """Edit-panel page."""
    panel = Test.query.get_or_404(panel_id)
    if not panel.is_panel:
        flash('That test is not a panel.', 'warning')
        return redirect(url_for('test_settings.panels'))

    categories = TestCategory.query.order_by(TestCategory.name.asc()).all()
    standalone_tests = (
        Test.query
        .filter(Test.is_active == True, Test.is_panel == False)   # noqa: E712
        .order_by(Test.name.asc())
        .all()
    )

    # Current parameters (ordered)
    params = (
        PanelParameter.query
        .filter_by(panel_id=panel.id)
        .order_by(PanelParameter.sort_order, PanelParameter.id)
        .all()
    )
    selected_ids = [p.test_id for p in params]
    selected_tests = [p.test for p in params]

    return render_template(
        'test_settings/panel_edit.html',
        active_tab='panels',
        panel=panel,
        selected_ids=selected_ids,
        selected_tests=selected_tests,
        categories=categories,
        standalone_tests=standalone_tests,
        mode='edit',
    )


@test_settings_bp.route('/panels/create', methods=['POST'])
def panel_create():
    """Create a new panel (form POST)."""
    data = request.form
    code = (data.get('code') or '').strip().upper()
    name = (data.get('name') or '').strip()
    cat_id = data.get('category_id') or None
    price = data.get('price') or '0'
    description = (data.get('description') or '').strip()
    param_ids = data.getlist('parameter_ids')

    errors = []
    if not code:
        errors.append('Code is required.')
    if not name:
        errors.append('Name is required.')
    if Test.query.filter_by(code=code).first():
        errors.append(f'Code "{code}" already exists.')

    try:
        price_val = float(price)
        if price_val < 0:
            errors.append('Price must be ≥ 0.')
    except ValueError:
        errors.append('Price must be a number.')
        price_val = 0.0

    if errors:
        for e in errors:
            flash(e, 'danger')
        return redirect(url_for('test_settings.panel_new'))

    panel = Test(
        code=code,
        name=name,
        category_id=int(cat_id) if cat_id else None,
        price=price_val,
        description=description or None,
        is_panel=True,
        is_active=True,
        result_format='panel',
        unit=None,
        normal_range=None,
    )
    db.session.add(panel)
    db.session.flush()

    # Add parameters in given order
    for i, tid in enumerate(param_ids):
        try:
            tid_int = int(tid)
        except (ValueError, TypeError):
            continue
        db.session.add(PanelParameter(
            panel_id=panel.id,
            test_id=tid_int,
            sort_order=i,
        ))

    db.session.commit()
    flash(f'Panel "{panel.name}" created.', 'success')
    return redirect(url_for('test_settings.panels'))


@test_settings_bp.route('/panels/<int:panel_id>/update', methods=['POST'])
def panel_update(panel_id):
    """Update an existing panel (form POST)."""
    panel = Test.query.get_or_404(panel_id)
    if not panel.is_panel:
        flash('Not a panel.', 'danger')
        return redirect(url_for('test_settings.panels'))

    data = request.form
    code = (data.get('code') or '').strip().upper()
    name = (data.get('name') or '').strip()
    cat_id = data.get('category_id') or None
    price = data.get('price') or '0'
    description = (data.get('description') or '').strip()
    param_ids = data.getlist('parameter_ids')

    errors = []
    if not code:
        errors.append('Code is required.')
    if not name:
        errors.append('Name is required.')

    dup = Test.query.filter(Test.code == code, Test.id != panel.id).first()
    if dup:
        errors.append(f'Code "{code}" already used by another test.')

    try:
        price_val = float(price)
        if price_val < 0:
            errors.append('Price must be ≥ 0.')
    except ValueError:
        errors.append('Price must be a number.')
        price_val = panel.price

    if errors:
        for e in errors:
            flash(e, 'danger')
        return redirect(url_for('test_settings.panel_edit', panel_id=panel.id))

    panel.code = code
    panel.name = name
    panel.category_id = int(cat_id) if cat_id else None
    panel.price = price_val
    panel.description = description or None
    panel.is_active = bool(data.get('is_active', True))

    # Replace parameters (simplest reliable approach)
    PanelParameter.query.filter_by(panel_id=panel.id).delete()
    for i, tid in enumerate(param_ids):
        try:
            tid_int = int(tid)
        except (ValueError, TypeError):
            continue
        db.session.add(PanelParameter(
            panel_id=panel.id,
            test_id=tid_int,
            sort_order=i,
        ))

    db.session.commit()
    flash(f'Panel "{panel.name}" updated.', 'success')
    return redirect(url_for('test_settings.panels'))


@test_settings_bp.route('/panels/<int:panel_id>/delete', methods=['POST'])
def panel_delete(panel_id):
    """Delete a panel (only if it has no order items)."""
    panel = Test.query.get_or_404(panel_id)

    # Check if used in any orders
    from modules.orders.models import OrderItem
    used = OrderItem.query.filter_by(test_id=panel.id).count()
    if used > 0:
        return jsonify({
            'ok': False,
            'error': f'Cannot delete — {used} order(s) use this panel.',
        }), 400

    # Remove parameter links, then panel
    PanelParameter.query.filter_by(panel_id=panel.id).delete()
    db.session.delete(panel)
    db.session.commit()

    return jsonify({'ok': True, 'id': panel_id})


# ============================================================
# Tab 5 — Bulk (stub)
# ============================================================
@test_settings_bp.route('/bulk')
def bulk():
    return render_template(
        'test_settings/coming_soon.html',
        active_tab='bulk',
        tab_name='Bulk Actions',
        tab_icon='bi-upload',
        description='Import from Excel/CSV, export the catalog, run cleanup tools.',
    )