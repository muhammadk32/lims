"""
Lab Test Settings — routes.

All routes are admin-only via the 'manage_test_settings' permission.

Routes are thin: parse request → call service → flash → redirect.
Business logic lives in services.py; query building in queries.py.
"""
from flask import (
    render_template, request, redirect, url_for, flash, jsonify,
)
from flask_login import login_required

from core.decorators import manage_test_settings_required
from modules.tests import (
    Test, TestCategory, RESULT_FORMAT_KEYS, RESULT_FORMATS,
)
from . import test_settings_bp
from .helpers import catalog_stats, format_counts, format_meta
from . import queries as q
from . import services as svc


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
    search = request.args.get('q', '').strip()
    fmt_filter = request.args.get('format', '').strip()
    cat_filter = request.args.get('category', '').strip()

    if fmt_filter and fmt_filter not in RESULT_FORMAT_KEYS:
        fmt_filter = ''

    tests = q.list_formats(q=search, fmt_filter=fmt_filter, cat_filter=cat_filter)

    return render_template(
        'test_settings/formats.html',
        active_tab='formats',
        tests=tests,
        categories=q.list_categories(),
        result_formats=RESULT_FORMATS,
        format_counts=format_counts(),
        format_meta=format_meta,
        stats=catalog_stats(),
        q=search,
        fmt_filter=fmt_filter,
        cat_filter=cat_filter,
    )


@test_settings_bp.route('/formats/<int:test_id>/update', methods=['POST'])
def format_update(test_id):
    test = Test.query.get_or_404(test_id)

    data = request.get_json(silent=True) or {}
    new_format = (data.get('result_format') or '').strip()

    result = svc.update_test_format(test, new_format)
    if result is None:
        return jsonify({'ok': False, 'error': 'Invalid format'}), 400

    return jsonify(result)


# ============================================================
# Tab 2 — Categories
# ============================================================
@test_settings_bp.route('/categories')
def categories():
    cats, counts, uncategorized = q.list_categories_with_counts()

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
    ok, error, cat = svc.create_category(
        data.get('name', ''), data.get('description', '')
    )
    if not ok:
        return jsonify({'ok': False, 'error': error}), 400

    return jsonify({
        'ok': True, 'id': cat.id, 'name': cat.name,
        'description': cat.description or '',
    })


@test_settings_bp.route('/categories/<int:cat_id>/update', methods=['POST'])
def category_update(cat_id):
    cat = TestCategory.query.get_or_404(cat_id)

    data = request.get_json(silent=True) or {}
    ok, error = svc.update_category(
        cat, data.get('name', ''), data.get('description', '')
    )
    if not ok:
        return jsonify({'ok': False, 'error': error}), 400

    return jsonify({
        'ok': True, 'id': cat.id, 'name': cat.name,
        'description': cat.description or '',
    })


@test_settings_bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
def category_delete(cat_id):
    cat = TestCategory.query.get_or_404(cat_id)

    ok, error, _count = svc.delete_category(cat)
    if not ok:
        return jsonify({'ok': False, 'error': error}), 400

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
        description='Manage units (mg/dL, mmol/L, ...) and age/gender-specific reference ranges.',
    )


# ============================================================
# Tab 4 — Panels
# ============================================================
@test_settings_bp.route('/panels')
def panels():
    """List all panels with their parameter counts."""
    search = request.args.get('q', '').strip()

    panels = q.list_panels(q=search)

    return render_template(
        'test_settings/panels.html',
        active_tab='panels',
        panels=panels,
        param_counts=q.param_counts_by_panel(),
        categories=q.list_categories(),
        standalone_tests=q.list_standalone_tests(),
        total_panels=len(panels),
    )


@test_settings_bp.route('/panels/new', methods=['GET'])
def panel_new():
    """Create-panel page."""
    return render_template(
        'test_settings/panel_edit.html',
        active_tab='panels',
        panel=None,
        selected_ids=[],
        categories=q.list_categories(),
        standalone_tests=q.list_standalone_tests(),
        mode='create',
    )


@test_settings_bp.route('/panels/<int:panel_id>/edit', methods=['GET'])
def panel_edit(panel_id):
    """Edit-panel page."""
    panel = Test.query.get_or_404(panel_id)
    if not panel.is_panel:
        flash('That test is not a panel.', 'warning')
        return redirect(url_for('test_settings.panels'))

    params = q.get_panel_parameters(panel.id)

    return render_template(
        'test_settings/panel_edit.html',
        active_tab='panels',
        panel=panel,
        selected_ids=[p.test_id for p in params],
        selected_tests=[p.test for p in params],
        categories=q.list_categories(),
        standalone_tests=q.list_standalone_tests(),
        mode='edit',
    )


@test_settings_bp.route('/panels/create', methods=['POST'])
def panel_create():
    """Create a new panel (form POST)."""
    ok, errors, panel = svc.create_panel(request.form)

    if not ok:
        for e in errors:
            flash(e, 'danger')
        return redirect(url_for('test_settings.panel_new'))

    flash(f'Panel "{panel.name}" created.', 'success')
    return redirect(url_for('test_settings.panels'))


@test_settings_bp.route('/panels/<int:panel_id>/update', methods=['POST'])
def panel_update(panel_id):
    """Update an existing panel (form POST)."""
    panel = Test.query.get_or_404(panel_id)
    if not panel.is_panel:
        flash('Not a panel.', 'danger')
        return redirect(url_for('test_settings.panels'))

    ok, errors = svc.update_panel(panel, request.form)
    if not ok:
        for e in errors:
            flash(e, 'danger')
        return redirect(url_for('test_settings.panel_edit', panel_id=panel.id))

    flash(f'Panel "{panel.name}" updated.', 'success')
    return redirect(url_for('test_settings.panels'))


@test_settings_bp.route('/panels/<int:panel_id>/delete', methods=['POST'])
def panel_delete(panel_id):
    """Delete a panel (only if it has no order items)."""
    panel = Test.query.get_or_404(panel_id)

    ok, error = svc.delete_panel(panel)
    if not ok:
        return jsonify({'ok': False, 'error': error}), 400

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
