from flask import (
    render_template, request, redirect, url_for, flash, abort
)
from flask_login import login_required, current_user
from sqlalchemy import or_
from extensions import db
from . import tests_bp
from .models import (Test, TestCategory, TestReferenceRange, TestParameter,
                     RateCategory, RateCategoryTest, RateCategoryRate,
                     RateCategoryDeptRate, PanelParameter, Specimen)
from . import services as svc
from core.decorators import permission_required
from core.audit import log_action


# ---------- Helpers ----------
def _labs_for_test_form():
    from modules.laboratories.models import Laboratory
    return (Laboratory.query
        .filter_by(is_partner_lab=True, is_active=True)
        .order_by(Laboratory.name.asc())
        .all())

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

    ?tab=catalog    â†’ test catalog (default)
    ?tab=formats    â†’ test result formats
    ?tab=categories â†’ test categories
    ?tab=panels     â†’ test panels
    ?tab=units      â†’ units stub
    ?tab=bulk       â†’ bulk stub
    """
    from datetime import datetime as _dt
    from modules.tests import (
        RESULT_FORMAT_KEYS, RESULT_FORMATS,
    )
    from modules.test_settings.helpers import (
        catalog_stats, format_counts, format_meta,
    )

    tab = request.args.get('tab', 'catalog').strip().lower()
    valid_tabs = ('catalog', 'formats', 'categories', 'panels', 'units', 'bulk', 'previews', 'rates')
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
        type_filter = request.args.get('type_filter', '').strip()
        specimen_id = request.args.get('specimen', type=int)

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
        if specimen_id:
            query = query.filter(Test.specimen_id == specimen_id)

        if type_filter == 'panel':
            query = query.filter(Test.is_panel == True)  # noqa: E712
        elif type_filter == 'plain':
            from sqlalchemy import exists as _ex
            query = (query.filter(Test.is_panel == False)  # noqa: E712
                          .filter(~_ex().where(_PP.test_id == Test.id))
                          .filter(~_ex().where(_TP.test_id == Test.id)))
        elif type_filter == 'child':
            from sqlalchemy import exists as _ex
            query = (query.filter(Test.is_panel == False)  # noqa: E712
                          .filter(_ex().where(_PP.test_id == Test.id)))
        elif type_filter == 'analyte':
            from sqlalchemy import exists as _ex
            query = query.filter(_ex().where(_TP.test_id == Test.id))
        ctx.update({
            'tests': query.order_by(Test.code.asc()).paginate(page=page, per_page=15, error_out=False),
            'categories': TestCategory.query.order_by(TestCategory.name).all(),
            'specimens': Specimen.query.filter_by(is_active=True).order_by(Specimen.name).all(),
            'q': q,
            'category_id': category_id,
            'status_filter': status_filter,
            'type_filter': type_filter,
            'specimen_id': specimen_id,
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

    elif tab == 'rates':
        from sqlalchemy import func
        # models already imported at module level
        cat_id = request.args.get('cat', type=int)
        edit_id = request.args.get('edit', type=int)
        detail = request.args.get('detail', type=int)
        dept = request.args.get('dept', type=int)

        if edit_id:
            cat = RateCategory.query.get_or_404(edit_id)
            parent_options = (RateCategory.query
                              .filter(RateCategory.id != cat.id,
                                      RateCategory.is_active == True)  # noqa: E712
                              .order_by(RateCategory.code.asc()).all())
            ctx.update({
                'rate_category': cat,
                'parent_options': parent_options,
            })
            return render_template('test_settings/shell.html', **ctx)

        if detail:
            cats = RateCategory.query.order_by(RateCategory.code.asc()).all()
            # for each category: sum of tests + first rate row
            data = []
            for c in cats:
                first_rate = (RateCategoryRate.query
                              .filter_by(rate_category_id=c.id)
                              .order_by(RateCategoryRate.section_code.asc().nulls_last(),
                                        RateCategoryRate.id.asc()).first())
                n_tests = (RateCategoryTest.query
                           .filter_by(rate_category_id=c.id)
                           .with_entities(RateCategoryTest.test_id).distinct().count())
                data.append({
                    'cat': c,
                    'rate': first_rate,
                    'tests': n_tests,
                })
            ctx.update({
                'rate_detail_rows': data,
                'detail_mode': True,
            })
            return render_template('test_settings/shell.html', **ctx)

        if cat_id:
            cat = RateCategory.query.get_or_404(cat_id)
            # main dept grid — always shown for rate_category
            depts = TestCategory.query.order_by(TestCategory.name.asc()).all()
            drs = {d.department_id: d for d in
                   RateCategoryDeptRate.query.filter_by(rate_category_id=cat.id).all()}
            dept_rows = []
            for d in depts:
                dr = drs.get(d.id)
                if not dr:
                    dr = RateCategoryDeptRate(
                        rate_category_id=cat.id, department_id=d.id,
                        discount_percent=0, commission_percent=0,
                    )
                    db.session.add(dr)
                dept_rows.append({'dept': d, 'dr': dr})
            db.session.commit()

            selected_dept = None
            dept_tests = []
            if dept:
                selected_dept = TestCategory.query.get(dept)
                if selected_dept:
                    # get dept rate + commission
                    dr = RateCategoryDeptRate.query.filter_by(
                        rate_category_id=cat.id, department_id=dept).first()
                    disc_pct = (dr.discount_percent or 0) if dr else 0
                    comm_pct = (dr.commission_percent or 0) if dr else 0
                    # tests in this department (via category_id)
                    tests = (Test.query
                             .filter_by(category_id=dept)
                             .filter(Test.is_active == True)  # noqa: E712
                             .order_by(Test.code.asc()).all())
                    # existing rate-list test links for this rate category
                    linked_ids = {r[0] for r in
                        db.session.query(RateCategoryTest.test_id)
                        .filter_by(rate_category_id=cat.id).all()}
                    for t in tests:
                        price = float(t.price or 0)
                        dept_tests.append({
                            'test': t,
                            'discount_amt': round(price * disc_pct / 100.0, 2),
                            'commission_amt': round(price * comm_pct / 100.0, 2),
                            'linked': t.id in linked_ids,
                        })

            ctx.update({
                'rate_category': cat,
                'dept_rows': dept_rows,
                'selected_dept': selected_dept,
                'selected_dept_id': dept,
                'dept_tests': dept_tests,
            })
            return render_template('test_settings/shell.html', **ctx)
            rates = (RateCategoryRate.query
                     .filter_by(rate_category_id=cat.id)
                     .order_by(RateCategoryRate.section_code.asc().nulls_last(),
                               RateCategoryRate.id.asc()).all())
            linked_tests = (RateCategoryTest.query
                            .filter_by(rate_category_id=cat.id)
                            .order_by(RateCategoryTest.sort_order.asc()).all())
            # test picker: active tests not yet in this category
            used_ids = [lt.test_id for lt in linked_tests]
            available = (Test.query
                         .filter(Test.is_active == True)  # noqa: E712
                         .filter(~Test.id.in_(used_ids) if used_ids else Test.id > 0)
                         .order_by(Test.code.asc()).limit(200).all())
            parent_options = (RateCategory.query
                              .filter(RateCategory.id != cat.id,
                                      RateCategory.is_active == True)  # noqa: E712
                              .order_by(RateCategory.code.asc()).all())
            ctx.update({
                'rate_category': cat,
                'rates': rates,
                'linked_tests': linked_tests,
                'available_tests': available,
                'parent_options': parent_options,
            })
        else:
            q = request.args.get('q', '').strip()
            rt = request.args.get('rt', '').strip()
            status_filter = request.args.get('status', 'active').strip()
            desc = request.args.get('desc', '').strip()
            query = RateCategory.query
            if status_filter == 'active':
                query = query.filter(RateCategory.is_active == True)  # noqa: E712
            elif status_filter == 'inactive':
                query = query.filter(RateCategory.is_active == False)  # noqa: E712
            if q:
                query = query.filter(RateCategory.name.ilike(f'%{q}%'))
            if rt:
                query = query.filter(RateCategory.rate_type == rt)
            if desc:
                query = query.filter(RateCategory.description.ilike(f'%{desc}%'))
            cats = query.order_by(RateCategory.code.asc()).all()
            test_counts = dict(
                db.session.query(RateCategoryTest.rate_category_id, func.count(func.distinct(RateCategoryTest.test_id)))
                .group_by(RateCategoryTest.rate_category_id).all()
            )
            ctx.update({
                'rate_categories': cats,
                'rate_test_counts': test_counts,
                'q': q, 'rt': rt, 'status_filter': status_filter, 'desc': desc,
            })

    elif tab == 'panels':
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
    # 'all' â†’ no filter

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

    tests = query.order_by(Test.code.asc()).paginate(page=page, per_page=15, error_out=False)
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
            return render_template('tests/form.html', test=None, categories=categories, form=request.form, labs=_labs_for_test_form(), all_tests=Test.query.filter_by(is_active=True).order_by(Test.name).all())

        # Duplicate check
        if Test.query.filter_by(code=code).first():
            flash(f'A test with code "{code}" already exists.', 'danger')
            return render_template('tests/form.html', test=None, categories=categories, form=request.form, labs=_labs_for_test_form(), all_tests=Test.query.filter_by(is_active=True).order_by(Test.name).all())

        category = None
        cat_id = request.form.get('category_id', type=int)
        if cat_id:
            category = TestCategory.query.get(cat_id)

        # ---- Parameter Only path ----
        if request.form.get('parameter_only'):
            parent_id = request.form.get('parent_test_id', type=int)
            if not parent_id:
                flash('Pick a Parent Test when creating a Parameter.', 'danger')
                return render_template('tests/form.html', test=None, categories=categories,
                                       form=request.form, labs=_labs_for_test_form(),
                                       all_tests=Test.query.filter_by(is_active=True).order_by(Test.name).all())
            parent = Test.query.get(parent_id)
            if not parent:
                flash('Parent test not found.', 'danger')
                return render_template('tests/form.html', test=None, categories=categories,
                                       form=request.form, labs=_labs_for_test_form(),
                                       all_tests=Test.query.filter_by(is_active=True).order_by(Test.name).all())

            from sqlalchemy import func
            max_sort = db.session.query(func.coalesce(func.max(TestParameter.sort_order), 0)) \
                                 .filter(TestParameter.test_id == parent.id).scalar() or 0

            param = TestParameter(
                test_id=parent.id,
                name=name,
                report_name=name,
                unit=request.form.get('unit', '').strip() or None,
                is_editable=True,
                sort_order=max_sort + 1,
                is_active=True,
            )
            db.session.add(param)
            db.session.commit()

            log_action('create', 'test_parameter', param.id,
                       f'Added parameter {param.name} to {parent.code} - {parent.name}')
            flash(f'Parameter "{name}" added to {parent.name}.', 'success')
            return redirect(url_for('tests.view_test', test_id=parent.id))

        # ---- Normal test / panel path ----
        test_type = (request.form.get('test_type') or 'single').strip().lower()
        is_panel = (test_type == 'panel')

        test = Test(
            code=code,
            name=name,
            category_id=category.id if category else None,
            price=request.form.get('price', type=float) or 0.0,
            normal_range=request.form.get('normal_range', '').strip() or None,
            unit=request.form.get('unit', '').strip() or None,
            description=request.form.get('description', '').strip() or None,
            turnaround_hours=request.form.get('turnaround_hours', type=int) or 24,
            is_outsourced=bool(request.form.get('is_outsourced')),
            is_panel=is_panel,
            max_discount_percent=(
                request.form.get('max_discount_percent', type=float)
                if request.form.get('is_outsourced') else None
            ),
            laboratory_id=(
                request.form.get('laboratory_id', type=int)
                if request.form.get('is_outsourced') else None
            ),
        )

        db.session.add(test)
        db.session.commit()

        kind = 'panel' if is_panel else 'test'
        log_action('create', 'test', test.id, f'Created {kind} {test.code} - {test.name}')
        flash(f'{"Panel" if is_panel else "Test"} "{test.name}" created.', 'success')
        if is_panel:
            return redirect(url_for('test_settings.panel_edit', panel_id=test.id))
        return redirect(url_for('tests.list_tests'))

    return render_template('tests/form.html', test=None, categories=categories, form={}, labs=_labs_for_test_form(), all_tests=Test.query.filter_by(is_active=True).order_by(Test.name).all())


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
            return render_template('tests/form.html', test=test, categories=categories, form=request.form, labs=_labs_for_test_form())

        # Duplicate check (excluding self)
        existing = Test.query.filter(Test.code == code, Test.id != test.id).first()
        if existing:
            flash(f'Another test already uses code "{code}".', 'danger')
            return render_template('tests/form.html', test=test, categories=categories, form=request.form, labs=_labs_for_test_form())

        test.code = code
        test.name = name
        cat_id = request.form.get('category_id', type=int)
        test.category_id = cat_id if cat_id else None
        test.price = request.form.get('price', type=float) or 0.0
        test.normal_range = request.form.get('normal_range', '').strip() or None
        test.unit = request.form.get('unit', '').strip() or None
        test.description = request.form.get('description', '').strip() or None
        test.turnaround_hours = request.form.get('turnaround_hours', type=int) or 24
        test.sample_type = request.form.get('sample_type', '').strip() or None
        test.is_outsourced = bool(request.form.get('is_outsourced'))
        test.max_discount_percent = (
            request.form.get('max_discount_percent', type=float)
            if test.is_outsourced else None
        )
        test.laboratory_id = (
            request.form.get('laboratory_id', type=int)
            if test.is_outsourced else None
        )

        db.session.commit()

        log_action('update', 'test', test.id, f'Updated test {test.code}')

        flash('Test updated.', 'success')
        return redirect(url_for('tests.view_test', test_id=test.id))

    return render_template('tests/form.html', test=test, categories=categories, form={}, ranges=test.reference_ranges or [], labs=_labs_for_test_form())


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


# ===== Phase 2: reference ranges save =====


@tests_bp.route('/<int:test_id>/ranges', methods=['GET', 'POST'])
@login_required
@permission_required('manage_tests')
def save_reference_ranges(test_id):
    """Save male / female / other reference ranges for one test."""
    test = _get_test_or_404(test_id)

    if request.method == 'GET':
        return render_template('tests/edit_ranges.html', test=test)

    created, updated, deleted = svc.save_ranges(test, request.form, current_user)

    parts = []
    if created: parts.append(f'{created} added')
    if updated: parts.append(f'{updated} updated')
    if deleted: parts.append(f'{deleted} removed')
    flash('Reference ranges: ' + (', '.join(parts) or 'no change'), 'success')
    return redirect(url_for('tests.view_test', test_id=test.id))

# ============================================================
# Setup Gender Reference Values (ADAM-style)
# ============================================================
@tests_bp.route("/<int:test_id>/ranges/<gender>", methods=["GET", "POST"])
@login_required
@permission_required("manage_tests")
def edit_ranges_gender(test_id, gender):
    test = _get_test_or_404(test_id)
    gender = (gender or "any").lower()
    if gender not in ("male", "female", "any"):
        abort(404)

    if request.method == "POST":
        svc.add_range_row(test, gender, request.form, current_user)
        flash("Reference value added.", "success")
        return redirect(url_for("tests.edit_ranges_gender",
                                test_id=test.id, gender=gender))

    rows = [r for r in (test.reference_ranges or [])
            if r.is_active and (r.gender or "any").lower() == gender]

    editing = None
    edit_id = request.args.get("edit", type=int)
    if edit_id:
        editing = TestReferenceRange.query.get(edit_id)

    return render_template(
        "tests/ranges_gender.html",
        test=test, gender=gender, rows=rows, editing=editing,
    )


@tests_bp.route("/ranges/<int:range_id>/delete", methods=["POST"])
@login_required
@permission_required("manage_tests")
def delete_range_row(range_id):
    r = TestReferenceRange.query.get_or_404(range_id)
    test_id, gender = r.test_id, r.gender or "any"
    svc.delete_range_row(range_id, current_user)
    flash("Reference value removed.", "info")
    return redirect(url_for("tests.edit_ranges_gender",
                            test_id=test_id, gender=gender))

@tests_bp.route("/ranges/<int:range_id>/update", methods=["POST"])
@login_required
@permission_required("manage_tests")
def update_range(range_id):
    r = TestReferenceRange.query.get_or_404(range_id)
    test_id, gender = r.test_id, r.gender or "any"
    svc.update_range_row(range_id, request.form, current_user)
    flash("Reference value updated.", "success")
    return redirect(url_for("tests.edit_ranges_gender",
                            test_id=test_id, gender=gender))



# ============================================================
# Rate list editor routes
# ============================================================
@tests_bp.route('/rate-lists/<int:cat_id>/save', methods=['POST'])
@login_required
@permission_required('manage_tests')
def rate_list_save(cat_id):
    cat = RateCategory.query.get_or_404(cat_id)
    cat.name = (request.form.get('name') or cat.name).strip()
    cat.description = (request.form.get('description') or '').strip() or None
    try:
        _pid = int(request.form.get('parent_rate_category_id') or 0) or None
    except (ValueError, TypeError):
        _pid = None
    cat.parent_rate_category_id = _pid
    cat.is_standard = bool(request.form.get('is_standard'))
    cat.is_active = (request.form.get('is_active') or '1') == '1'
    try:
        cat.code = int(request.form.get('code') or 0) or None
    except (ValueError, TypeError):
        pass
    db.session.commit()
    log_action('update', 'rate_category', cat.id, f'Updated rate list {cat.name}')
    flash('Rate list saved.', 'success')
    return redirect(url_for('tests.index', tab='rates', cat=cat.id))


@tests_bp.route('/rate-lists/<int:cat_id>/add-rate', methods=['POST'])
@login_required
@permission_required('manage_tests')
def rate_list_add_rate(cat_id):
    RateCategory.query.get_or_404(cat_id)
    def _n(k):
        try: return float(request.form.get(k) or 0)
        except: return 0.0
    def _i(k):
        try: return int(request.form.get(k) or 0) or None
        except: return None
    db.session.add(RateCategoryRate(
        rate_category_id=cat_id,
        section_code=_i('section_code'),
        rate_percent=_n('rate_percent'),
        commission=_n('commission'),
    ))
    db.session.commit()
    flash('Rate added.', 'success')
    return redirect(url_for('tests.index', tab='rates', cat=cat_id))


@tests_bp.route('/rate-lists/<int:cat_id>/delete-rate/<int:rate_id>', methods=['POST'])
@login_required
@permission_required('manage_tests')
def rate_list_delete_rate(cat_id, rate_id):
    r = RateCategoryRate.query.filter_by(id=rate_id, rate_category_id=cat_id).first_or_404()
    db.session.delete(r)
    db.session.commit()
    flash('Rate deleted.', 'info')
    return redirect(url_for('tests.index', tab='rates', cat=cat_id))


@tests_bp.route('/rate-lists/<int:cat_id>/add-test', methods=['POST'])
@login_required
@permission_required('manage_tests')
def rate_list_add_test(cat_id):
    RateCategory.query.get_or_404(cat_id)
    q = (request.form.get('test_q') or '').strip()
    if q:
        # first match by code or name
        t = (Test.query
             .filter(or_(Test.code == q, Test.code.ilike(f'%{q}%'), Test.name.ilike(f'%{q}%')))
             .filter(Test.is_active == True)  # noqa: E712
             .first())
        if not t:
            flash(f'No active test matches "{q}".', 'warning')
            return redirect(url_for('tests.index', tab='rates', cat=cat_id))
        exists = RateCategoryTest.query.filter_by(rate_category_id=cat_id, test_id=t.id).first()
        if exists:
            flash(f'Test already in this rate list: {t.code} {t.name}', 'info')
        else:
            db.session.add(RateCategoryTest(
                rate_category_id=cat_id, test_id=t.id,
                sort_order=RateCategoryTest.query.filter_by(rate_category_id=cat_id).count() + 1,
            ))
            db.session.commit()
            flash(f'Added {t.code} - {t.name}.', 'success')
    return redirect(url_for('tests.index', tab='rates', cat=cat_id))


@tests_bp.route('/rate-lists/<int:cat_id>/delete-test/<int:link_id>', methods=['POST'])
@login_required
@permission_required('manage_tests')
def rate_list_delete_test(cat_id, link_id):
    ln = RateCategoryTest.query.filter_by(id=link_id, rate_category_id=cat_id).first_or_404()
    db.session.delete(ln)
    db.session.commit()
    flash('Test removed from rate list.', 'info')
    return redirect(url_for('tests.index', tab='rates', cat=cat_id))


# ============================================================
# Rate list — new / copy / toggle / delete
# ============================================================
@tests_bp.route('/rate-lists/new', methods=['GET', 'POST'])
@login_required
@permission_required('manage_tests')
def rate_list_new():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        if not name:
            flash('Name is required.', 'danger')
            return redirect(url_for('tests.rate_list_new'))
        try:
            code = int(request.form.get('code') or 0) or None
        except (ValueError, TypeError):
            code = None
        cat = RateCategory(
            code=code,
            name=name,
            description=(request.form.get('description') or '').strip() or None,
            rate_type=(request.form.get('rate_type') or '').strip() or None,
            is_active=True,
        )
        db.session.add(cat)
        db.session.commit()
        log_action('create', 'rate_category', cat.id, f'Created rate list {cat.name}')
        flash(f'Rate list "{cat.name}" created.', 'success')
        return redirect(url_for('tests.index', tab='rates', cat=cat.id))
    return render_template('test_settings/shell.html', tab='rates',
                           rate_category_new=True,
                           all_tests=Test.query.filter_by(is_active=True).all())


@tests_bp.route('/rate-lists/<int:cat_id>/copy', methods=['POST'])
@login_required
@permission_required('manage_tests')
def rate_list_copy(cat_id):
    src = RateCategory.query.get_or_404(cat_id)
    new = RateCategory(
        name=f'{src.name} (copy)',
        description=src.description,
        rate_type=src.rate_type,
        is_active=True,
    )
    db.session.add(new)
    db.session.flush()
    seen = set()
    for r in RateCategoryRate.query.filter_by(rate_category_id=src.id).all():
        db.session.add(RateCategoryRate(
            rate_category_id=new.id,
            company_code=r.company_code,
            section_code=r.section_code,
            rate_percent=r.rate_percent,
            commission=r.commission,
        ))
    for t in RateCategoryTest.query.filter_by(rate_category_id=src.id).order_by(RateCategoryTest.sort_order).all():
        if t.test_id in seen: continue
        seen.add(t.test_id)
        db.session.add(RateCategoryTest(
            rate_category_id=new.id, test_id=t.test_id, sort_order=t.sort_order,
        ))
    db.session.commit()
    flash(f'Copied {src.name} → {new.name}.', 'success')
    return redirect(url_for('tests.index', tab='rates', cat=new.id))


@tests_bp.route('/rate-lists/<int:cat_id>/toggle', methods=['POST'])
@login_required
@permission_required('manage_tests')
def rate_list_toggle(cat_id):
    cat = RateCategory.query.get_or_404(cat_id)
    cat.is_active = not cat.is_active
    db.session.commit()
    flash(f'Rate list "{cat.name}" {"enabled" if cat.is_active else "disabled"}.', 'info')
    return redirect(url_for('tests.index', tab='rates'))


@tests_bp.route('/rate-lists/<int:cat_id>/delete', methods=['POST'])
@login_required
@permission_required('manage_tests')
def rate_list_delete(cat_id):
    cat = RateCategory.query.get_or_404(cat_id)
    name = cat.name
    db.session.delete(cat)
    db.session.commit()
    log_action('delete', 'rate_category', cat_id, f'Deleted rate list {name}')
    flash(f'Rate list "{name}" deleted.', 'info')
    return redirect(url_for('tests.index', tab='rates'))

@tests_bp.route('/rate-lists/<int:cat_id>/rate/<int:rate_id>/save-inline', methods=['POST'])
@login_required
@permission_required('manage_tests')
def rate_list_save_inline_rate(cat_id, rate_id):
    r = RateCategoryRate.query.filter_by(id=rate_id, rate_category_id=cat_id).first_or_404()
    try:
        if request.form.get('rate_percent') is not None:
            r.rate_percent = float(request.form.get('rate_percent') or 0)
        if request.form.get('commission') is not None:
            r.commission = float(request.form.get('commission') or 0)
    except (ValueError, TypeError):
        pass
    db.session.commit()
    flash('Rate updated.', 'success')
    return redirect(url_for('tests.index', tab='rates', detail=1))

@tests_bp.route('/rate-lists/<int:cat_id>/dept/<int:dept_id>/save', methods=['POST'])
@login_required
@permission_required('manage_tests')
def rate_dept_save(cat_id, dept_id):
    dr = RateCategoryDeptRate.query.filter_by(
        rate_category_id=cat_id, department_id=dept_id).first()
    if not dr:
        dr = RateCategoryDeptRate(
            rate_category_id=cat_id, department_id=dept_id,
            discount_percent=0, commission_percent=0)
        db.session.add(dr)
    try:
        dr.discount_percent = float(request.form.get('discount_percent') or 0)
    except (ValueError, TypeError):
        pass
    try:
        dr.commission_percent = float(request.form.get('commission_percent') or 0)
    except (ValueError, TypeError):
        pass
    db.session.commit()
    flash('Department rate saved.', 'success')
    return redirect(url_for('tests.index', tab='rates', cat=cat_id))

@tests_bp.route('/rate-lists/<int:cat_id>/toggle-test/<int:test_id>', methods=['POST'])
@login_required
@permission_required('manage_tests')
def rate_list_toggle_test(cat_id, test_id):
    RateCategory.query.get_or_404(cat_id)
    Test.query.get_or_404(test_id)
    ln = RateCategoryTest.query.filter_by(
        rate_category_id=cat_id, test_id=test_id).first()
    if ln:
        db.session.delete(ln)
        db.session.commit()
        flash('Test removed from rate list.', 'info')
    else:
        so = RateCategoryTest.query.filter_by(rate_category_id=cat_id).count() + 1
        db.session.add(RateCategoryTest(
            rate_category_id=cat_id, test_id=test_id, sort_order=so))
        db.session.commit()
        flash('Test added to rate list.', 'success')
    # return to same dept view
    dept = request.form.get('dept') or request.args.get('dept')
    if dept:
        return redirect(url_for('tests.index', tab='rates', cat=cat_id, dept=dept))
    return redirect(url_for('tests.index', tab='rates', cat=cat_id))

@tests_bp.route('/rate-lists/<int:cat_id>/bulk-toggle-dept/<int:dept_id>', methods=['POST'])
@login_required
@permission_required('manage_tests')
def rate_list_bulk_toggle_dept(cat_id, dept_id):
    RateCategory.query.get_or_404(cat_id)
    action = request.form.get('action', 'add')  # 'add' or 'remove'
    tests = (Test.query
             .filter_by(category_id=dept_id)
             .filter(Test.is_active == True).all())  # noqa: E712
    test_ids = [t.id for t in tests]
    if not test_ids:
        flash('No tests in this department.', 'info')
        return redirect(url_for('tests.index', tab='rates', cat=cat_id, dept=dept_id))

    if action == 'add':
        existing = {r[0] for r in
            db.session.query(RateCategoryTest.test_id)
            .filter_by(rate_category_id=cat_id)
            .filter(RateCategoryTest.test_id.in_(test_ids)).all()}
        added = 0
        so = RateCategoryTest.query.filter_by(rate_category_id=cat_id).count()
        for tid in test_ids:
            if tid in existing: continue
            so += 1
            db.session.add(RateCategoryTest(
                rate_category_id=cat_id, test_id=tid, sort_order=so))
            added += 1
        db.session.commit()
        flash(f'Added {added} test(s) to rate list.', 'success')
    elif action == 'remove':
        n = (RateCategoryTest.query
             .filter_by(rate_category_id=cat_id)
             .filter(RateCategoryTest.test_id.in_(test_ids))
             .delete(synchronize_session=False))
        db.session.commit()
        flash(f'Removed {n} test(s) from rate list.', 'info')
    return redirect(url_for('tests.index', tab='rates', cat=cat_id, dept=dept_id))


@tests_bp.route('/rate-lists/<int:cat_id>/test-override/<int:test_id>', methods=['POST'])
@login_required
@permission_required('manage_tests')
def rate_test_save_override(cat_id, test_id):
    from .models import RateCategoryTest, RateCategoryDeptRate, Test as _T
    rct = RateCategoryTest.query.filter_by(rate_category_id=cat_id, test_id=test_id).first()
    if not rct:
        flash('Test not in this rate list.', 'warning')
        return redirect(request.referrer or url_for('tests.index', tab='rates', cat=cat_id))
    t = _T.query.get(test_id)
    # find the dept rate to know default
    dr = RateCategoryDeptRate.query.filter_by(rate_category_id=cat_id, department_id=t.category_id).first() if t and t.category_id else None
    default_pct = (dr.discount_percent or 0) if dr else 0
    raw_amt = (request.form.get('discount_amount_override') or '').strip()
    if raw_amt == '':
        rct.discount_percent = None  # fall back to dept
    else:
        try:
            amt = float(raw_amt)
            price = float(t.price or 0) if t else 0
            pct = (amt / price * 100.0) if price > 0 else 0.0
            rct.discount_percent = round(pct, 2)
        except (ValueError, TypeError):
            pass
    db.session.commit()
    flash('Test override saved.', 'success')
    dept = request.form.get('dept')
    if dept:
        return redirect(url_for('tests.index', tab='rates', cat=cat_id, dept=dept))
    return redirect(url_for('tests.index', tab='rates', cat=cat_id))


@tests_bp.route('/rate-lists/<int:cat_id>/export.csv')
@login_required
@permission_required('manage_tests')
def rate_list_export_csv(cat_id):
    from flask import Response
    from .models import (RateCategory, RateCategoryTest,
                         RateCategoryDeptRate, Test, TestCategory)
    import csv, io

    cat = RateCategory.query.get_or_404(cat_id)
    dept_rates = {d.department_id: d for d in
                  RateCategoryDeptRate.query.filter_by(rate_category_id=cat.id).all()}
    rows = (RateCategoryTest.query
            .filter_by(rate_category_id=cat.id)
            .order_by(RateCategoryTest.sort_order.asc()).all())

    buf = io.StringIO()
    buf.write('\ufeff')  # UTF-8 BOM for Excel
    w = csv.writer(buf)
    w.writerow(['Test Code', 'Test Name', 'Department',
                'Lab Rate', 'Discount %', 'Discount Amt',
                'Net Rate', 'Commission %'])
    for r in rows:
        t = Test.query.get(r.test_id)
        if not t: continue
        dept = TestCategory.query.get(t.category_id) if t.category_id else None
        dr = dept_rates.get(t.category_id) if t.category_id else None
        dept_pct = (dr.discount_percent or 0) if dr else 0
        dept_comm = (dr.commission_percent or 0) if dr else 0
        eff_pct = r.discount_percent if r.discount_percent is not None else dept_pct
        eff_comm = r.commission_percent if r.commission_percent is not None else dept_comm
        price = float(t.price or 0)
        disc_amt = round(price * eff_pct / 100.0, 2)
        net = round(price - disc_amt, 2)
        w.writerow([t.code, t.name, dept.name if dept else '',
                    f'{price:.2f}', f'{eff_pct:.2f}', f'{disc_amt:.2f}',
                    f'{net:.2f}', f'{eff_comm:.2f}'])

    data = buf.getvalue()
    fname = f'rate_list_{cat.name.replace(" ", "_")}.csv'
    return Response(data, mimetype='text/csv',
                    headers={'Content-Disposition': f'attachment; filename={fname}'})


@tests_bp.route('/rate-lists/<int:cat_id>/export', methods=['GET'])
@login_required
@permission_required('manage_tests')
def rate_list_export_preview(cat_id):
    from .models import (RateCategory, RateCategoryTest, RateCategoryDeptRate,
                         Test, TestCategory, Specimen)
    cat = RateCategory.query.get_or_404(cat_id)

    # Filters from query string
    report_type = (request.args.get('report_type') or 'department').lower()
    variant = (request.args.get('variant') or 'with_discount').lower()
    department_id = request.args.get('department', type=int)
    category_id = request.args.get('category', type=int)
    run = bool(request.args.get('run'))

    def _fmt_time(hours):
        if not hours or hours <= 24: return 'SAME DAY'
        if hours < 48: return 'AFTER ONE DAY'
        days = round(hours / 24)
        if days < 7: return f'AFTER {days} DAYS'
        weeks = round(days / 7)
        return f'AFTER {weeks} WEEK' + ('S' if weeks > 1 else '')

    # Departments = TestCategory
    departments = TestCategory.query.order_by(TestCategory.name.asc()).all()

    rows = []
    if run:
        dept_rates = {d.department_id: d for d in
                      RateCategoryDeptRate.query.filter_by(rate_category_id=cat.id).all()}
        q = (RateCategoryTest.query
             .filter_by(rate_category_id=cat.id)
             .order_by(RateCategoryTest.sort_order.asc()))
        for rct in q.all():
            t = Test.query.get(rct.test_id)
            if not t: continue
            if department_id and t.category_id != department_id: continue
            if category_id and t.category_id != category_id: continue
            dept = TestCategory.query.get(t.category_id) if t.category_id else None
            dr = dept_rates.get(t.category_id) if t.category_id else None
            dept_pct = (dr.discount_percent or 0) if dr else 0
            dept_comm = (dr.commission_percent or 0) if dr else 0
            eff_pct = rct.discount_percent if rct.discount_percent is not None else dept_pct
            eff_comm = rct.commission_percent if rct.commission_percent is not None else dept_comm
            price = float(t.price or 0)
            disc_amt = round(price * eff_pct / 100.0, 2)
            net = round(price - disc_amt, 2)
            spec = Specimen.query.get(t.specimen_id) if t.specimen_id else None
            rows.append({
                'code': t.code, 'name': t.name,
                'department': dept.name if dept else '',
                'specimen': spec.name if spec else (t.sample_type or '—'),
                'reporting_time': _fmt_time(t.turnaround_hours),
                'price': price, 'discount_pct': eff_pct,
                'discount_amt': disc_amt, 'net': net,
                'commission_pct': eff_comm,
            })

    ctx = {
        'tab': 'rates',
        'rate_category': cat,
        'departments': departments,
        'report_type': report_type,
        'variant': variant,
        'department_id': department_id,
        'category_id': category_id,
        'rows': rows,
        'run': run,
    }
    # DEBUG
    if rows:
        print('DEBUG first row keys:', list(rows[0].keys()))
        print('DEBUG first row:', rows[0])
    return render_template('test_settings/_rate_list_export.html', **ctx)
