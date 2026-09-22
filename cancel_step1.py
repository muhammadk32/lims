"""
Cancel-with-auto-refund, one click.
- Adds Order.cancel_reason, cancelled_at, cancelled_by_id, refunded_at
- Rewrites cancel_order() to auto-refund the full paid amount
- Adds /orders/<id>/cancel POST route
- Adds Cancel button + modal to order view
"""
import os, re

# ============================================================
# 1. Order model — add fields if missing
# ============================================================
mpath = 'modules/orders/models.py'
with open(mpath, encoding='utf-8') as f:
    m = f.read()

added_model = False
if 'cancel_reason' not in m:
    # Insert after correction_note block
    anchor = "    correction_note = db.Column(db.Text, nullable=True)"
    if anchor in m:
        block = anchor + """

    # ---- Cancellation + auto-refund ----
    cancel_reason = db.Column(db.String(255), nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancelled_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    refunded_at = db.Column(db.DateTime, nullable=True)
    cancelled_by = db.relationship('User', foreign_keys=[cancelled_by_id])
"""
        m = m.replace(anchor, block, 1)
        with open(mpath, 'w', encoding='utf-8') as f:
            f.write(m)
        added_model = True
        print('OK  - Order model: cancel fields added')
    else:
        print('WARN - anchor not found in Order model')
else:
    print('SKIP - Order model already has cancel fields')

# ============================================================
# 2. ALTER TABLE — add columns (SQLite-safe)
# ============================================================
print()
print('Adding columns to DB...')
from app import app
from extensions import db
from sqlalchemy import text

new_cols = [
    ('cancel_reason',   'VARCHAR(255)'),
    ('cancelled_at',    'DATETIME'),
    ('cancelled_by_id', 'INTEGER'),
    ('refunded_at',     'DATETIME'),
]

with app.app_context():
    for col, typ in new_cols:
        try:
            db.session.execute(text(f'ALTER TABLE orders ADD COLUMN {col} {typ}'))
            db.session.commit()
            print(f'  + {col}')
        except Exception as e:
            if 'duplicate column' in str(e).lower():
                print(f'  = {col} already exists')
            else:
                print(f'  ! {col}: {e}')

# ============================================================
# 3. Services — rewrite cancel_order with auto-refund
# ============================================================
spath = 'modules/orders/services.py'
with open(spath, encoding='utf-8') as f:
    s = f.read()

# Find existing cancel_order and replace it
old_pattern = re.compile(
    r"def cancel_order\(order, user\):.*?(?=\n\ndef |\Z)",
    re.DOTALL,
)

new_cancel = '''def cancel_order(order, reason, user):
    """Cancel an order and automatically refund any amount already paid.

    Creates a negative Payment row so the refund is deducted from the
    Cash Summary on the date of cancellation.

    Returns (ok, error_message, refund_amount).
    """
    from modules.billing.models import Payment, PaymentMethod
    from modules.orders.models import OrderStatus

    if order.status == OrderStatus.CANCELLED:
        return False, 'Order is already cancelled.', 0.0

    reason = (reason or '').strip()
    if not reason:
        return False, 'Please provide a reason for cancellation.', 0.0

    now = datetime.utcnow()
    refund_amount = round_money(order.paid_amount or 0)

    # 1. Cancel the order
    order.status = OrderStatus.CANCELLED
    order.cancel_reason = reason
    order.cancelled_at = now
    order.cancelled_by_id = user.id if user else None

    # 2. Auto-refund whatever was paid
    if refund_amount > 0.001:
        db.session.add(Payment(
            order_id=order.id,
            amount=-refund_amount,               # negative = refund
            method=PaymentMethod.CASH,
            reference='Auto-refund on cancellation',
            notes=f'Cancelled: {reason[:120]}',
            received_by_id=user.id if user else None,
        ))
        order.refunded_at = now

    db.session.commit()

    log_action(
        'cancel', 'order', order.id,
        f'Cancelled order {order.order_code} — refunded Rs {refund_amount:.2f} '
        f'({reason[:80]})',
    )
    return True, None, refund_amount
'''

if 'Auto-refund on cancellation' in s:
    print('SKIP - services.py already has auto-refund')
else:
    s2 = old_pattern.sub(new_cancel, s, count=1)
    if s2 != s:
        with open(spath, 'w', encoding='utf-8') as f:
            f.write(s2)
        print('OK  - services.py: cancel_order rewritten with auto-refund')
    else:
        print('WARN - could not find cancel_order in services.py')

# ============================================================
# 4. Route — POST /orders/<id>/cancel
# ============================================================
rpath = 'modules/orders/routes.py'
with open(rpath, encoding='utf-8') as f:
    r = f.read()

if 'auto_refund_on_cancel' in r or 'cancel_reason' in r:
    print('SKIP - routes.py already has new cancel route')
else:
    # Find the existing cancel route
    old_route = re.compile(
        r"@orders_bp\.route\('/<int:order_id>/cancel'.*?return redirect\(url_for\('orders\.view_order', order_id=order\.id\)\)",
        re.DOTALL,
    )
    new_route = '''@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
@permission_required('cancel_order')
def cancel_order(order_id):
    """Cancel an order and auto-refund any amount paid."""
    order = _get_order_or_404(order_id)
    reason = (request.form.get('reason') or '').strip()

    ok, error, refund = svc.cancel_order(order, reason, current_user)
    if not ok:
        flash(error, 'warning')
    else:
        if refund > 0:
            flash(
                f'Order {order.order_code} cancelled. '
                f'Refunded {refund:.2f} to patient.',
                'info',
            )
        else:
            flash(f'Order {order.order_code} cancelled. Nothing to refund.', 'info')
    return redirect(url_for('orders.view_order', order_id=order.id))'''

    r2 = old_route.sub(new_route, r, count=1)
    if r2 != r:
        with open(rpath, 'w', encoding='utf-8') as f:
            f.write(r2)
        print('OK  - routes.py: cancel route rewritten')
    else:
        print('WARN - could not find cancel route in routes.py')

print()
print('=' * 55)
print('Model + DB + service + route done.')
print('Now run script 2 for the UI (view template + modal).')
print('=' * 55)
