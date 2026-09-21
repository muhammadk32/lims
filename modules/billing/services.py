"""Business logic for billing — payment recording and deletion.

No HTTP, no flash, no redirect. Pure domain operations.
"""
from extensions import db
from core.audit import log_action
from .models import Payment, PaymentMethod


def sync_order_paid_flag(order):
    """Set order.paid based on payment balance."""
    order.paid = order.is_fully_paid


def record_payment(order, amount, method, reference, notes, user):
    """Create a Payment row + sync the order's paid flag + commit.

    Returns (ok, error_message, payment).
    """
    if amount <= 0:
        return False, 'Payment amount must be greater than 0.', None

    if amount > order.balance_due + 0.001:
        return False, f'Amount exceeds balance due ({order.balance_due:.2f}).', None

    if method not in PaymentMethod.CHOICES:
        method = PaymentMethod.CASH

    payment = Payment(
        order_id=order.id,
        amount=amount,
        method=method,
        reference=(reference or '').strip() or None,
        notes=(notes or '').strip() or None,
        received_by_id=user.id,
    )
    db.session.add(payment)
    db.session.flush()
    sync_order_paid_flag(order)
    db.session.commit()

    log_action(
        'payment', 'payment', payment.id,
        f'Received {amount:.2f} ({method}) for {order.order_code}',
        extra={'order_id': order.id, 'method': method, 'amount': amount},
    )
    return True, None, payment


def delete_payment(payment):
    """Delete a payment and re-sync the parent order's paid flag.

    Returns (order, deleted_amount).
    """
    order = payment.order
    amount = payment.amount

    db.session.delete(payment)
    db.session.flush()
    sync_order_paid_flag(order)
    db.session.commit()

    log_action(
        'delete', 'payment', payment.id,
        f'Deleted payment {amount:.2f} from order {order.order_code}',
    )
    return order, amount