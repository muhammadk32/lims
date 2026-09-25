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
from sqlalchemy import func
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
    """List one row per top-level test (approved or pending).

    Filters:
      ?status=approved (default) | pending | all
      ?q=       search lab # / patient name
      ?date_from / ?date_to   YYYY-MM-DD
      ?test=    test name/code filter
    """
    from modules.orders.models import Order, OrderItem, OrderStatus
    from modules.patients.models import Patient
    from datetime import datetime as _dt, date as _d
    from sqlalchemy import or_

    status      = request.args.get('status', 'approved').strip()
    q           = request.args.get('q', '').strip()
    phone       = request.args.get('phone', '').strip()
    test_q      = request.args.get('test', '').strip()
    today       = _d.today()
    date_from_s = request.args.get('date_from', '').strip() or today.strftime('%Y-%m-%d')
    date_to_s   = request.args.get('date_to', '').strip() or today.strftime('%Y-%m-%d')

    try:    date_from = _dt.strptime(date_from_s, '%Y-%m-%d').date()
    except (ValueError, TypeError): date_from = today
    try:    date_to   = _dt.strptime(date_to_s,   '%Y-%m-%d').date()
    except (ValueError, TypeError): date_to   = today

    # Top-level items (no parent)
    query = (OrderItem.query
             .join(Order, OrderItem.order_id == Order.id)
             .filter(OrderItem.parent_item_id.is_(None))
             .filter(Order.status != OrderStatus.CANCELLED)
             .filter(func.date(Order.created_at) >= date_from)
             .filter(func.date(Order.created_at) <= date_to))

    if q or phone:
        query = query.join(Patient, Order.patient_id == Patient.id)
        if q:
            like = f'%{q}%'
            query = query.filter(or_(
                Order.order_code.ilike(like),
                Patient.full_name.ilike(like),
                Patient.patient_code.ilike(like),
            ))
        if phone:
            query = query.filter(Patient.phone.ilike(f'%{phone}%'))

    if test_q:
        from modules.tests.models import Test
        query = query.join(Test, OrderItem.test_id == Test.id)
        like = f'%{test_q}%'
        query = query.filter(or_(Test.name.ilike(like), Test.code.ilike(like)))

    items = query.order_by(OrderItem.id.desc()).all()

    # Filter by verify status
    if status == 'approved':
        items = [i for i in items if i.is_verified]
    elif status == 'pending':
        items = [i for i in items if not i.is_verified]
    # 'all' ? no filter

    return render_template(
        'reports/list.html',
        items=items,
        status=status,
        q=q,
        phone=phone,
        test_q=test_q,
        date_from=date_from_s,
        date_to=date_to_s,
    )



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
    buffer = generate_report_pdf(order, item_id=item_id)
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
    item_id = request.args.get('item', type=int)

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