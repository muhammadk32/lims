"""
Order / Patient Registration routes.

IMPORTANT: Cross-module model imports are done INSIDE functions
(lazy imports). This prevents circular-import chains at startup.
"""
from datetime import datetime, timedelta
from flask import (
    render_template, request, redirect, url_for, flash, abort, jsonify
)
from flask_login import login_required, current_user
from sqlalchemy import or_, func
from extensions import db
from core.decorators import permission_required
from core.audit import log_action
from . import orders_bp
from .models import Order, OrderItem, OrderStatus   # same module — safe


# ---------- Helpers ----------
def _get_order_or_404(order_id):
    o = Order.query.get(order_id)
    if not o:
        abort(404)
    return o


def _generate_order_code():
    """Per-month serial: MMYY-N (e.g. 0926-1, 0926-2)."""
    now = datetime.now()
    prefix = now.strftime('%m%y')
    pattern = f'{prefix}-%'

    max_code = (
        db.session.query(func.max(Order.order_code))
        .filter(Order.order_code.like(pattern))
        .scalar()
    )

    if max_code:
        try:
            last_serial = int(max_code.split('-', 1)[1])
        except (ValueError, IndexError):
            last_serial = 0
    else:
        last_serial = 0

    next_serial = last_serial + 1
    while Order.query.filter_by(order_code=f'{prefix}-{next_serial}').first():
        next_serial += 1

    return f'{prefix}-{next_serial}'


def _generate_patient_code():
    """Sequential 6-char patient code: P00001, P00002, ..."""
    from modules.patients.models import Patient

    import re
    pattern = re.compile(r'^P(\d{1,5})$')

    rows = (
        db.session.query(Patient.patient_code)
        .filter(Patient.patient_code.like('P%'))
        .all()
    )

    highest = 0
    for (code,) in rows:
        if not code:
            continue
        m = pattern.match(code)
        if m:
            try:
                n = int(m.group(1))
                if n > highest:
                    highest = n
            except ValueError:
                pass

    next_num = highest + 1
    code = f'P{next_num:05d}'

    while Patient.query.filter_by(patient_code=code).first():
        next_num += 1
        code = f'P{next_num:05d}'

    return code


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def _round_money(n):
    try:
        return float(round(float(n or 0)))
    except (ValueError, TypeError):
        return 0.0


# ============================================================
# DAILY LEDGER
# ============================================================
@orders_bp.route('/')
@login_required
def list_orders():
    from datetime import date
    from modules.patients.models import Patient

    q = request.args.get('q', '').strip()
    status = request.args.get('status', '').strip()
    paid_filter = request.args.get('paid', '').strip()

    today = date.today()
    date_from_str = request.args.get('date_from', '').strip()
    date_to_str = request.args.get('date_to', '').strip()

    if not date_from_str:
        date_from_str = today.strftime('%Y-%m-%d')
    if not date_to_str:
        date_to_str = today.strftime('%Y-%m-%d')

    try:
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        date_from = today
        date_from_str = today.strftime('%Y-%m-%d')

    try:
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        date_to = today
        date_to_str = today.strftime('%Y-%m-%d')

    query = Order.query.filter(
        Order.status != OrderStatus.CANCELLED,
        func.date(Order.created_at) >= date_from,
        func.date(Order.created_at) <= date_to,
    )

    if q:
        like = f'%{q}%'
        query = query.join(Patient).filter(
            or_(
                Order.order_code.ilike(like),
                Patient.full_name.ilike(like),
                Patient.patient_code.ilike(like),
                Patient.phone.ilike(like),
            )
        )

    if status in OrderStatus.CHOICES:
        query = query.filter(Order.status == status)

    orders_all = query.order_by(Order.id.desc()).all()

    if paid_filter == 'yes':
        orders_all = [o for o in orders_all if o.payment_status == 'paid']
    elif paid_filter == 'no':
        orders_all = [o for o in orders_all if o.payment_status == 'unpaid']
    elif paid_filter == 'partial':
        orders_all = [o for o in orders_all if o.payment_status == 'partial']

    total_amount = _round_money(sum(o.subtotal for o in orders_all))
    total_discount = _round_money(sum(o.discount_value for o in orders_all))
    net_amount = _round_money(sum(o.final_total for o in orders_all))
    paid_amount = _round_money(sum(o.paid_amount for o in orders_all))
    due_amount = _round_money(sum(o.balance_due for o in orders_all))

    stats = {
        'total_amount':   total_amount,
        'total_discount': total_discount,
        'net_amount':     net_amount,
        'paid_amount':    paid_amount,
        'due_amount':     due_amount,
        'case_count':     len(orders_all),
    }

    return render_template(
        'orders/list.html',
        orders=orders_all,
        q=q,
        status=status,
        paid_filter=paid_filter,
        statuses=OrderStatus.CHOICES,
        date_from=date_from_str,
        date_to=date_to_str,
        stats=stats,
        today=today.strftime('%Y-%m-%d'),
    )


# ============================================================
# NEW ORDER
# ============================================================
@orders_bp.route('/new', methods=['GET', 'POST'])
@login_required
@permission_required('create_order')
def new_order():
    from modules.billing.models import PaymentMethod
    from modules.form_settings.helpers import get_form_config

    if request.method == 'POST':
        return _handle_new_order_post()

    form_config = get_form_config()
    doctors = _get_doctors()

    return render_template(
        'orders/new.html',
        config=form_config,
        doctors=doctors,
        payment_methods=PaymentMethod.CHOICES,
        payment_method_labels=PaymentMethod.LABELS,
        now=datetime.now(),
    )


def _handle_new_order_post():
    """Handle unified order creation."""
    from modules.patients.models import Patient
    from modules.tests.models import Test
    from modules.billing.models import Payment, PaymentMethod

    form = request.form

    # ---------- 1. Patient ----------
    patient_id = form.get('patient_id', type=int)
    patient = None

    if patient_id:
        patient = Patient.query.get(patient_id)
        if not patient:
            flash('Patient not found.', 'danger')
            return redirect(url_for('orders.new_order'))
    else:
        full_name = (
            form.get('patient_name')
            or form.get('full_name')
            or ''
        ).strip()
        if not full_name:
            flash('Patient name is required.', 'danger')
            return redirect(url_for('orders.new_order'))

        age_val = form.get('age', type=float)
        if not age_val:
            v = form.get('age_value', type=float) or 0
            unit = (form.get('age_unit') or 'years').strip()

            if not v:
                years = form.get('age_years', type=int) or 0
                months = form.get('age_months', type=int) or 0
                days = form.get('age_days', type=int) or 0
                if years or months or days:
                    age_val = years + round((months * 30 + days) / 365.0, 2)
            else:
                if unit == 'years':
                    age_val = v
                elif unit == 'months':
                    age_val = v / 12.0
                elif unit == 'days':
                    age_val = v / 365.0

        patient = Patient(
            patient_code=_generate_patient_code(),
            full_name=full_name,
            age=int(round(age_val)) if age_val else None,
            date_of_birth=_parse_date(form.get('date_of_birth')),
            gender=(form.get('gender') or form.get('patient_gender') or '').strip() or None,
            phone=(form.get('phone') or form.get('patient_phone') or '').strip() or None,
            email=(form.get('email') or form.get('patient_email') or '').strip() or None,
            address=(form.get('address') or form.get('patient_address') or '').strip() or None,
            blood_group=(form.get('blood_group') or form.get('patient_blood_group') or '').strip() or None,
            notes=None,
        )

        db.session.add(patient)
        db.session.flush()

        log_action('create', 'patient', patient.id,
                   f'Created patient {patient.full_name} ({patient.patient_code}) via reception')

    # ---------- 2. Tests ----------
    test_ids = form.getlist('test_ids', type=int)
    if not test_ids:
        flash('Please select at least one test.', 'danger')
        db.session.rollback()
        return redirect(url_for('orders.new_order'))

    tests = Test.query.filter(
        Test.id.in_(test_ids),
        Test.is_active == True,   # noqa: E712
    ).all()
    if not tests:
        flash('No valid tests selected.', 'danger')
        db.session.rollback()
        return redirect(url_for('orders.new_order'))

    # ---------- 3. Referral ----------
    referred_by = (form.get('referred_by') or '').strip() or None
    doctor_id = None
    if referred_by:
        try:
            doctor_id = int(referred_by)
        except (ValueError, TypeError):
            doctor_id = None

    # ---------- 4. Sample date ----------
    sample_date_str = form.get('sample_date') or ''
    sample_collected_at = None
    if sample_date_str:
        try:
            sample_collected_at = datetime.strptime(
                sample_date_str.replace('T', ' ')[:16], '%Y-%m-%d %H:%M'
            )
        except (ValueError, TypeError):
            sample_collected_at = None
    if not sample_collected_at:
        sample_collected_at = datetime.utcnow()

    # ---------- 5. Create order ----------
    order = Order(
        order_code=_generate_order_code(),
        patient_id=patient.id,
        doctor_id=doctor_id or current_user.id,
        status=OrderStatus.PENDING,
        sample_collected_at=sample_collected_at,
        notes=(form.get('notes') or '').strip() or None,
    )

    if referred_by and doctor_id is None:
        ext_note = f'Referred by: {referred_by}'
        order.notes = (order.notes + '\n' + ext_note) if order.notes else ext_note

    db.session.add(order)
    db.session.flush()

    # ---------- 6. Order items ----------
    for t in tests:
        if t.is_panel:
            parent = OrderItem(
                order_id=order.id,
                test_id=t.id,
                price=t.price,
                parent_item_id=None,
                sort_order=0,
            )
            db.session.add(parent)
            db.session.flush()
            params = t.get_parameters()
            for idx, param in enumerate(params):
                db.session.add(OrderItem(
                    order_id=order.id,
                    test_id=param.id,
                    price=0.0,
                    parent_item_id=parent.id,
                    sort_order=idx,
                ))
        else:
            db.session.add(OrderItem(
                order_id=order.id,
                test_id=t.id,
                price=t.price,
                parent_item_id=None,
                sort_order=0,
            ))

    db.session.flush()

    # ---------- 7. Discount ----------
    discount_type = (form.get('discount_type') or 'amount').strip()
    if discount_type not in ('amount', 'percent'):
        discount_type = 'amount'

    order.discount_type = discount_type
    order.discount_reason = (form.get('discount_reason') or '').strip() or None

    if discount_type == 'percent':
        try:
            pct = max(0.0, min(100.0, float(form.get('discount_percent') or 0)))
        except (ValueError, TypeError):
            pct = 0.0
        order.discount_percent = pct
        order.discount_amount = 0.0
    else:
        try:
            amt = max(0.0, float(form.get('discount_amount') or 0))
        except (ValueError, TypeError):
            amt = 0.0
        order.discount_amount = _round_money(amt)
        order.discount_percent = 0.0

    # ---------- 8. Recompute subtotal ----------
    order.recompute_total()

    # ---------- 9. Payment ----------
    try:
        pay_amount = float(form.get('payment_amount') or 0)
    except (ValueError, TypeError):
        pay_amount = 0.0

    pay_amount = _round_money(pay_amount)

    if pay_amount > 0.001:
        method = (form.get('payment_method') or PaymentMethod.CASH).strip()
        if method not in PaymentMethod.CHOICES:
            method = PaymentMethod.CASH

        pay_amount = min(pay_amount, order.final_total)

        payment = Payment(
            order_id=order.id,
            amount=pay_amount,
            method=method,
            reference=(form.get('payment_reference') or '').strip() or None,
            notes=None,
            received_by_id=current_user.id,
        )
        db.session.add(payment)
        db.session.flush()
        order.paid = order.is_fully_paid

    db.session.commit()

    log_action(
        'create', 'order', order.id,
        f'Created order {order.order_code} for {patient.full_name} — '
        f'subtotal {order.subtotal:.2f}, discount {order.discount_value:.2f}, '
        f'total {order.final_total:.2f}'
    )

    flash(
        f'Lab # {order.order_code} created for {patient.full_name} '
        f'— Total: {order.final_total:.2f}',
        'success'
    )
    return redirect(url_for('orders.view_order', order_id=order.id))


# ============================================================
# AJAX APIs
# ============================================================
@orders_bp.route('/api/patient-lookup')
@login_required
def api_patient_lookup():
    from modules.patients.models import Patient

    phone = request.args.get('phone', '').strip()
    query = request.args.get('q', '').strip()

    if not phone and not query:
        return jsonify([])

    pat_q = Patient.query.filter(Patient.is_active == True)   # noqa: E712

    if phone:
        like = f'%{phone}%'
        pat_q = pat_q.filter(Patient.phone.ilike(like))

    if query:
        like = f'%{query}%'
        pat_q = pat_q.filter(or_(
            Patient.full_name.ilike(like),
            Patient.patient_code.ilike(like),
            Patient.phone.ilike(like),
        ))

    results = pat_q.order_by(Patient.id.desc()).limit(10).all()

    return jsonify([
        {
            'id': p.id,
            'patient_code': p.patient_code,
            'full_name': p.full_name,
            'age': p.compute_age(),
            'gender': p.gender,
            'phone': p.phone,
            'email': p.email,
            'address': p.address,
            'blood_group': p.blood_group,
        }
        for p in results
    ])


@orders_bp.route('/api/test-search')
@login_required
def api_test_search():
    from modules.tests.models import Test

    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify([])

    like = f'%{q}%'
    tests = (
        Test.query
        .filter(
            Test.is_active == True,                        # noqa: E712
            or_(Test.name.ilike(like), Test.code.ilike(like)),
        )
        .order_by(Test.is_panel.desc(), Test.name.asc())
        .limit(15)
        .all()
    )

    results = []
    for t in tests:
        row = {
            'id': t.id,
            'code': t.code,
            'name': t.name,
            'price': t.price,
            'unit': t.unit,
            'normal_range': t.normal_range,
            'is_panel': t.is_panel,
            'category': t.category_ref.name if t.category_ref else None,
            'format': t.result_format,
        }
        if t.is_panel:
            params = t.get_parameters()
            row['parameter_count'] = len(params)
            row['parameters'] = [p.name for p in params]
        results.append(row)

    return jsonify(results)


@orders_bp.route('/api/doctors')
@login_required
def api_doctors():
    return jsonify(_get_doctors())


def _get_doctors():
    from core.models import User
    doctors = (
        User.query
        .filter(User.role == 'doctor', User.is_active_flag == True)   # noqa: E712
        .order_by(User.full_name.asc())
        .all()
    )
    return [
        {'id': u.id, 'name': u.full_name, 'username': u.username}
        for u in doctors
    ]


# ============================================================
# VIEW / PRINT / STATUS / CANCEL
# ============================================================
@orders_bp.route('/<int:order_id>')
@login_required
def view_order(order_id):
    order = _get_order_or_404(order_id)
    return render_template('orders/view.html', order=order, statuses=OrderStatus.CHOICES)


@orders_bp.route('/<int:order_id>/print')
@login_required
def print_order(order_id):
    order = _get_order_or_404(order_id)

    copy = request.args.get('copy', 'both').strip().lower()
    if copy not in ('patient', 'lab', 'both'):
        copy = 'both'

    auto = request.args.get('auto', '0') == '1'

    return render_template(
        'orders/print.html',
        order=order,
        timedelta=timedelta,
        copy=copy,
        auto=auto,
    )


@orders_bp.route('/<int:order_id>/status', methods=['POST'])
@login_required
@permission_required('update_order_status')
def change_status(order_id):
    order = _get_order_or_404(order_id)
    new_status = request.form.get('status', '').strip()

    if new_status not in OrderStatus.CHOICES:
        flash('Invalid status.', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))

    order.status = new_status
    if new_status == OrderStatus.COLLECTED and not order.sample_collected_at:
        order.sample_collected_at = datetime.utcnow()

    db.session.commit()
    log_action('status', 'order', order.id, f'Order {order.order_code} → {new_status}')
    flash(f'Lab # {order.order_code} status updated to "{new_status}".', 'success')
    return redirect(url_for('orders.view_order', order_id=order.id))


@orders_bp.route('/<int:order_id>/pay', methods=['POST'])
@login_required
@permission_required('record_payment')
def mark_paid(order_id):
    order = _get_order_or_404(order_id)
    order.paid = True
    db.session.commit()
    log_action('payment', 'order', order.id, f'Marked {order.order_code} paid (legacy flag)')
    flash('Payment flag set.', 'success')
    return redirect(url_for('orders.view_order', order_id=order.id))


@orders_bp.route('/<int:order_id>/unpay', methods=['POST'])
@login_required
@permission_required('record_payment')
def mark_unpaid(order_id):
    order = _get_order_or_404(order_id)
    order.paid = False
    db.session.commit()
    flash('Payment flag removed.', 'info')
    return redirect(url_for('orders.view_order', order_id=order.id))


@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
@permission_required('cancel_order')
def cancel_order(order_id):
    order = _get_order_or_404(order_id)
    order.status = OrderStatus.CANCELLED
    db.session.commit()
    log_action('delete', 'order', order.id, f'Cancelled order {order.order_code}')
    flash(f'Lab # {order.order_code} cancelled.', 'info')
    return redirect(url_for('orders.view_order', order_id=order.id))


# ============================================================
# PATHOLOGIST APPROVAL / CORRECTION
# ============================================================
def _can_approve():
    """Only admin and doctor roles may approve or send back."""
    return current_user.is_authenticated and current_user.role in ('admin', 'doctor')


@orders_bp.route('/<int:order_id>/approve', methods=['POST'])
@login_required
def approve_report(order_id):
    """Pathologist approves the report → sets reported_at/by and status=approved."""
    if not _can_approve():
        flash('Only a pathologist or admin can approve reports.', 'danger')
        return redirect(url_for('orders.view_order', order_id=order_id))

    order = _get_order_or_404(order_id)

    if order.status not in (OrderStatus.COMPLETED, OrderStatus.CORRECTION):
        flash('Only completed or correction orders can be approved.', 'warning')
        return redirect(url_for('orders.view_order', order_id=order.id))

    if not order.all_results_done:
        flash('Cannot approve — some results are still missing.', 'warning')
        return redirect(url_for('orders.view_order', order_id=order.id))

    order.status = OrderStatus.APPROVED
    order.reported_at = datetime.utcnow()
    order.reported_by_id = current_user.id
    # Clear any previous correction note
    order.correction_note = None

    db.session.commit()

    log_action('approve', 'order', order.id,
               f'Approved report {order.order_code}')

    flash(f'Report {order.order_code} approved.', 'success')
    return redirect(url_for('orders.view_order', order_id=order.id))


@orders_bp.route('/<int:order_id>/send-back', methods=['POST'])
@login_required
def send_back(order_id):
    """Pathologist sends the report back for correction."""
    if not _can_approve():
        flash('Only a pathologist or admin can send back reports.', 'danger')
        return redirect(url_for('orders.view_order', order_id=order_id))

    order = _get_order_or_404(order_id)

    if order.status not in (OrderStatus.COMPLETED, OrderStatus.APPROVED):
        flash('Only completed or approved orders can be sent back.', 'warning')
        return redirect(url_for('orders.view_order', order_id=order.id))

    reason = (request.form.get('reason') or '').strip()
    if not reason:
        flash('Please provide a reason for sending back.', 'warning')
        return redirect(url_for('orders.view_order', order_id=order.id))

    order.status = OrderStatus.CORRECTION
    order.correction_note = reason
    order.correction_at = datetime.utcnow()
    order.correction_by_id = current_user.id
    # Clear approval so re-approval is required
    order.reported_at = None
    order.reported_by_id = None

    db.session.commit()

    log_action('correction', 'order', order.id,
               f'Sent back {order.order_code} for correction: {reason[:80]}')

    flash(f'Report {order.order_code} sent back for correction.', 'info')
    return redirect(url_for('orders.view_order', order_id=order.id))


@orders_bp.route('/api/test-prices')
@login_required
def api_test_prices():
    from modules.tests.models import Test
    tests = Test.query.filter_by(is_active=True).all()
    return jsonify({str(t.id): t.price for t in tests})