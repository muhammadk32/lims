"""Barcode label routes."""
from flask import send_file, request, abort
from flask_login import login_required

from extensions import db
from modules.orders.models import Order
from . import labels_bp
from .pdf import build_grid_pdf, build_single_pdf


def _get_order_or_404(order_id):
    o = Order.query.get(order_id)
    if not o:
        abort(404)
    return o


@labels_bp.route('/order/<int:order_id>')
@login_required
def print_labels(order_id):
    """Print sample labels for an order.

    ?mode=grid    — A4 sheet, 3x8 labels per page (default)
    ?mode=single  — one label per page (thermal printer)
    """
    order = _get_order_or_404(order_id)
    mode = (request.args.get('mode') or 'grid').strip().lower()
    if mode not in ('grid', 'single'):
        mode = 'grid'

    buf = build_single_pdf(order) if mode == 'single' else build_grid_pdf(order)
    return send_file(
        buf,
        mimetype='application/pdf',
        download_name=f'labels_{order.order_code}_{mode}.pdf',
        as_attachment=False,
    )
