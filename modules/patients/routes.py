"""
Patient Directory routes.

IMPORTANT: Cross-module model imports are done INSIDE functions
(lazy imports). This prevents circular-import chains at startup.
"""
from datetime import datetime
from io import StringIO
import csv

from flask import (
    render_template, request, redirect, url_for, flash, abort,
    Response, send_file,
)
from flask_login import login_required, current_user
from sqlalchemy import or_, func
from extensions import db
from core.decorators import permission_required
from core.audit import log_action
from . import patients_bp
from .models import Patient


# ---------- Helpers ----------
def _generate_patient_code():
    return f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"


def _get_or_404(patient_id):
    p = Patient.query.get(patient_id)
    if not p:
        abort(404)
    return p


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def _patient_stats(patient_id):
    """Return (order_count, total_billed, last_visit)."""
    from modules.orders.models import Order, OrderStatus   # ← lazy import

    q = (
        db.session.query(
            func.count(Order.id),
            func.coalesce(func.sum(Order.total_amount), 0.0),
            func.max(Order.created_at),
        )
        .filter(
            Order.patient_id == patient_id,
            Order.status != OrderStatus.CANCELLED,
        )
        .first()
    )
    if not q:
        return (0, 0.0, None)
    return (q[0] or 0, float(q[1] or 0.0), q[2])


# ============================================================
# PATIENT DIRECTORY (read-only list, search, filter)
# ============================================================
@patients_bp.route('/')
@login_required
def list_patients():
    q = request.args.get('q', '').strip()
    gender_filter = request.args.get('gender', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Patient.query.filter(Patient.is_active == True)   # noqa: E712

    if q:
        like = f'%{q}%'
        query = query.filter(or_(
            Patient.full_name.ilike(like),
            Patient.patient_code.ilike(like),
            Patient.phone.ilike(like),
            Patient.email.ilike(like),
        ))

    if gender_filter in ('Male', 'Female', 'Other'):
        query = query.filter(Patient.gender == gender_filter)

    patients = (
        query.order_by(Patient.id.desc())
        .paginate(page=page, per_page=25, error_out=False)
    )

    rows = []
    for p in patients.items:
        order_count, total_billed, last_visit = _patient_stats(p.id)
        rows.append({
            'patient': p,
            'order_count': order_count,
            'total_billed': total_billed,
            'last_visit': last_visit,
        })

    total_patients = Patient.query.filter(Patient.is_active == True).count()   # noqa: E712
    this_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_this_month = Patient.query.filter(
        Patient.is_active == True,                                          # noqa: E712
        Patient.created_at >= this_month_start,
    ).count()

    return render_template(
        'patients/list.html',
        rows=rows,
        pagination=patients,
        q=q,
        gender_filter=gender_filter,
        total_patients=total_patients,
        new_this_month=new_this_month,
    )


# ============================================================
# VIEW PATIENT (with full order history)
# ============================================================
@patients_bp.route('/<int:patient_id>')
@login_required
def view_patient(patient_id):
    from modules.orders.models import Order, OrderStatus   # ← lazy import

    patient = _get_or_404(patient_id)

    orders = (
        Order.query
        .filter_by(patient_id=patient.id)
        .order_by(Order.id.desc())
        .all()
    )

    total_billed = sum(o.total_amount or 0 for o in orders if o.status != OrderStatus.CANCELLED)
    paid_total = sum(o.paid_amount or 0 for o in orders)
    balance = max(0.0, total_billed - paid_total)

    stats = {
        'total_orders': len(orders),
        'total_billed': total_billed,
        'total_paid': paid_total,
        'balance': balance,
    }

    return render_template(
        'patients/view.html',
        patient=patient,
        orders=orders,
        stats=stats,
    )


# ============================================================
# EDIT PATIENT (from directory row)
# ============================================================
@patients_bp.route('/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('edit_patient')
def edit_patient(patient_id):
    patient = _get_or_404(patient_id)

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        if not full_name:
            flash('Full name is required.', 'danger')
            return render_template('patients/form.html', patient=patient, form=request.form)

        patient.full_name = full_name
        patient.age = request.form.get('age', type=int)
        patient.date_of_birth = _parse_date(request.form.get('date_of_birth'))
        patient.gender = request.form.get('gender') or None
        patient.phone = request.form.get('phone', '').strip() or None
        patient.email = request.form.get('email', '').strip() or None
        patient.address = request.form.get('address', '').strip() or None
        patient.blood_group = request.form.get('blood_group') or None
        patient.notes = request.form.get('notes', '').strip() or None

        db.session.commit()

        log_action('update', 'patient', patient.id,
                   f'Updated patient {patient.full_name}')

        flash('Patient updated successfully.', 'success')
        return redirect(url_for('patients.view_patient', patient_id=patient.id))

    return render_template('patients/form.html', patient=patient, form={})


# ============================================================
# ARCHIVE (soft delete)
# ============================================================
@patients_bp.route('/<int:patient_id>/delete', methods=['POST'])
@login_required
@permission_required('delete_patient')
def delete_patient(patient_id):
    patient = _get_or_404(patient_id)
    patient.is_active = False
    db.session.commit()

    log_action('delete', 'patient', patient.id,
               f'Archived patient {patient.full_name}')

    flash(f'Patient "{patient.full_name}" archived.', 'info')
    return redirect(url_for('patients.list_patients'))


# ============================================================
# EXPORT CSV
# ============================================================
@patients_bp.route('/export.csv')
@login_required
def export_csv():
    q = request.args.get('q', '').strip()
    gender_filter = request.args.get('gender', '').strip()

    query = Patient.query.filter(Patient.is_active == True)   # noqa: E712

    if q:
        like = f'%{q}%'
        query = query.filter(or_(
            Patient.full_name.ilike(like),
            Patient.patient_code.ilike(like),
            Patient.phone.ilike(like),
            Patient.email.ilike(like),
        ))

    if gender_filter in ('Male', 'Female', 'Other'):
        query = query.filter(Patient.gender == gender_filter)

    patients = query.order_by(Patient.id.desc()).all()

    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        'Patient Code', 'Full Name', 'Age', 'Gender', 'Phone', 'Email',
        'Address', 'Blood Group', 'Orders', 'Total Billed', 'Last Visit', 'Registered',
    ])

    for p in patients:
        order_count, total_billed, last_visit = _patient_stats(p.id)
        writer.writerow([
            p.patient_code,
            p.full_name,
            p.compute_age() or '',
            p.gender or '',
            p.phone or '',
            p.email or '',
            (p.address or '').replace('\n', ' '),
            p.blood_group or '',
            order_count,
            f'{total_billed:.2f}',
            last_visit.strftime('%Y-%m-%d %H:%M') if last_visit else '',
            p.created_at.strftime('%Y-%m-%d %H:%M') if p.created_at else '',
        ])

    csv_bytes = buf.getvalue().encode('utf-8-sig')

    filename = f'patient_directory_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'

    return Response(
        csv_bytes,
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
        },
    )


# ---------- Legacy route ----------
@patients_bp.route('/new', methods=['GET'])
@login_required
def new_patient():
    """Redirect to reception registration — no more standalone patient creation."""
    flash('Please use Patient Registration to add a new patient.', 'info')
    return redirect(url_for('orders.new_order'))

# ============================================================
# Patient History by Phone / Name / Code
# ============================================================
@patients_bp.route('/history')
@login_required
def history_by_phone():
    """Search patients and show all their visits."""
    from . import queries as pq

    q = request.args.get('q', '').strip()
    patients, visits = pq.search_patients_with_visits(q=q) if q else ([], {})

    return render_template(
        'patients/history.html',
        q=q,
        patients=patients,
        visits=visits,
    )
