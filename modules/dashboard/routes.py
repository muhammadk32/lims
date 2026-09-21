"""
Dashboard routes.

IMPORTANT: All cross-module model imports are done INSIDE functions
(lazy imports). This prevents circular-import chains at startup.
"""
from flask import render_template, request
from flask_login import login_required
from sqlalchemy import or_
from . import dashboard_bp
from . import charts


@dashboard_bp.route('/')
@login_required
def index():
    stats = charts.kpi_cards()

    rev_labels, rev_values = charts.revenue_last_days(14)
    ord_labels, ord_values = charts.orders_last_days(14)

    return render_template(
        'dashboard/index.html',
        stats=stats,
        rev_labels=rev_labels,
        rev_values=rev_values,
        ord_labels=ord_labels,
        ord_values=ord_values,
        top_tests=charts.top_tests(5),
        top_patients=charts.top_patients(5),
        status_breakdown=charts.order_status_breakdown(),
        pending_orders=charts.pending_orders(5),
    )


@dashboard_bp.route('/search')
@login_required
def global_search():
    # Lazy imports — only run when this function is called
    from modules.patients.models import Patient
    from modules.orders.models import Order

    q = request.args.get('q', '').strip()

    patients = []
    orders = []

    if q:
        like = f'%{q}%'
        patients = (
            Patient.query.filter(
                or_(
                    Patient.full_name.ilike(like),
                    Patient.patient_code.ilike(like),
                    Patient.phone.ilike(like),
                )
            ).limit(20).all()
        )
        orders = (
            Order.query.filter(
                or_(
                    Order.order_code.ilike(like),
                )
            ).limit(20).all()
        )

    return render_template(
        'dashboard/search.html',
        q=q,
        patients=patients,
        orders=orders,
    )