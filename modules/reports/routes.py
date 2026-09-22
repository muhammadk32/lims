"""
Reports routes.

IMPORTANT: Cross-module imports are done INSIDE functions (lazy imports).
This prevents circular-import chains at startup.
"""
from flask import (
    render_template, send_file, abort, request, redirect, url_for, flash
)
from flask_login import login_required
from extensions import db
from core.decorators import permission_required
from . import reports_bp


# ---------- Helpers ----------
def _get_order_or_404(order_id):
    from modules.orders.models import Order   # ← lazy
    o = Order.query.get(order_id)
    if not o:
        abort(404)
    return o


# ---------- Reports List ----------
@reports_bp.route('/')
@login_required
@permission_required('view_reports')
def index():
    """List approved orders with download links.

    Default view shows only APPROVED reports — those are final and
    ready to be handed to the patient. `?status=all` shows every
    non-cancelled order regardless of state.
    """
    from modules.orders.models import Order, OrderStatus   # ← lazy

    status = request.args.get('status', 'approved').strip()
    q = request.args.get('q', '').strip()

    query = Order.query

    if status == 'all':
        query = query.filter(Order.status != OrderStatus.CANCELLED)
    elif status in OrderStatus.CHOICES:
        query = query.filter(Order.status == status)
    else:
        # Default fallback: approved only
        query = query.filter(Order.status == OrderStatus.APPROVED)

    if q:
        from modules.patients.models import Patient   # ← lazy
        from sqlalchemy import or_
        like = f'%{q}%'
        query = query.join(Patient).filter(
            or_(
                Order.order_code.ilike(like),
                Patient.full_name.ilike(like),
                Patient.patient_code.ilike(like),
            )
        )

    orders = query.order_by(Order.id.desc()).limit(100).all()

    return render_template('reports/list.html', orders=orders, status=status, q=q)


# ---------- HTML Preview ----------
@reports_bp.route('/order/<int:order_id>/preview')
@login_required
@permission_required('view_reports')
def preview(order_id):
    order = _get_order_or_404(order_id)

    from .pdf_generator import (                                          # ← lazy
        LAB_NAME, LAB_TAGLINE, LAB_ADDRESS, LAB_PHONE, LAB_EMAIL, LAB_WEBSITE
    )
    from modules.results.validators import check_result                   # ← lazy

    return render_template(
        'reports/preview.html',
        order=order,
        lab={
            'name': LAB_NAME,
            'tagline': LAB_TAGLINE,
            'address': LAB_ADDRESS,
            'phone': LAB_PHONE,
            'email': LAB_EMAIL,
            'website': LAB_WEBSITE,
        },
        check_result=check_result,
    )


# ---------- PDF Download ----------
@reports_bp.route('/order/<int:order_id>/pdf')
@login_required
@permission_required('view_reports')
def order_pdf(order_id):
    order = _get_order_or_404(order_id)

    # Block report if balance is due
    if order.balance_due > 0.01:
        from flask import flash
        flash(
            f'Report blocked - Rs {order.balance_due:.0f} balance due. '
            f'Please record payment first.',
            'warning',
        )
        from flask import redirect, url_for
        return redirect(url_for('orders.view_order', order_id=order.id))


    if not order.items:
        flash('Order has no tests — nothing to report.', 'warning')
        return redirect(url_for('orders.view_order', order_id=order.id))

    from .pdf_generator import generate_report_pdf   # ← lazy
    buffer = generate_report_pdf(order)
    filename = f'report_{order.order_code}.pdf'

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf',
    )


# ---------- View PDF in browser ----------
@reports_bp.route('/order/<int:order_id>/view-pdf')
@login_required
@permission_required('view_reports')
def view_pdf(order_id):
    order = _get_order_or_404(order_id)

    # Block report if balance is due
    if order.balance_due > 0.01:
        from flask import flash
        flash(
            f'Report blocked - Rs {order.balance_due:.0f} balance due. '
            f'Please record payment first.',
            'warning',
        )
        from flask import redirect, url_for
        return redirect(url_for('orders.view_order', order_id=order.id))

    from .pdf_generator import generate_report_pdf   # ← lazy
    buffer = generate_report_pdf(order)
    return send_file(
        buffer,
        mimetype='application/pdf',
        download_name=f'report_{order.order_code}.pdf',
        as_attachment=False,
    )