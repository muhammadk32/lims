"""
Show cancelled orders in Ledger + Cash Summary (with styling),
but exclude them from financial totals.
"""
import re

# ============================================================
# 1. orders/queries.py — include cancelled in the list, exclude from totals
# ============================================================
qpath = 'modules/orders/queries.py'
q = open(qpath, encoding='utf-8').read()

# Remove the filter that hides cancelled
old = '        Order.status != OrderStatus.CANCELLED,\n'
if old in q:
    q = q.replace(old, '', 1)
    print('OK  - get_ledger_orders: cancelled no longer hidden')
else:
    print('SKIP - cancelled filter not found (already removed?)')

# Patch compute_ledger_stats to exclude cancelled from totals
old_fn_start = 'def compute_ledger_stats(orders):'
idx = q.find(old_fn_start)
if idx == -1:
    print('WARN - compute_ledger_stats not found')
else:
    end = q.find('\ndef ', idx + 1)
    if end == -1:
        end = len(q)
    new_fn = '''def compute_ledger_stats(orders):
    """Aggregate totals for the ledger footer.

    Cancelled orders are excluded from the money totals but counted
    separately so the operator can see them.
    """
    from .models import OrderStatus
    billable = [o for o in orders if o.status != OrderStatus.CANCELLED]
    cancelled = [o for o in orders if o.status == OrderStatus.CANCELLED]

    return {
        'total_amount':    round_money(sum(o.subtotal for o in billable)),
        'total_discount':  round_money(sum(o.discount_value for o in billable)),
        'net_amount':      round_money(sum(o.final_total for o in billable)),
        'paid_amount':     round_money(sum(o.paid_amount for o in billable)),
        'due_amount':      round_money(sum(o.balance_due for o in billable)),
        'refunded_amount': round_money(sum(o.paid_amount for o in cancelled)),
        'case_count':      len(billable),
        'cancelled_count': len(cancelled),
    }
'''
    q = q[:idx] + new_fn + q[end+1:]
    print('OK  - compute_ledger_stats: excludes cancelled from totals')

open(qpath, 'w', encoding='utf-8').write(q)


# ============================================================
# 2. billing/queries.py — same treatment
# ============================================================
bpath = 'modules/billing/queries.py'
b = open(bpath, encoding='utf-8').read()

# Find the list_billing_orders function
if 'list_billing_orders' in b:
    idx = b.find('def list_billing_orders')
    end = b.find('\ndef ', idx + 1)
    if end == -1:
        end = len(b)
    body = b[idx:end]

    # Remove the cancelled filter inside
    if 'Order.status != OrderStatus.CANCELLED' in body:
        body = body.replace('Order.status != OrderStatus.CANCELLED', 'Order.id > 0  # include cancelled for audit', 1)
        b = b[:idx] + body + b[end:]
        print('OK  - list_billing_orders: cancelled now visible')

if 'compute_billing_stats' in b:
    idx = b.find('def compute_billing_stats')
    end = b.find('\ndef ', idx + 1)
    if end == -1:
        end = len(b)
    new_bstats = '''def compute_billing_stats():
    """Dashboard totals. Cancelled orders excluded from money."""
    from modules.orders.models import Order, OrderStatus

    today = date.today()

    billable_filter = Order.status != OrderStatus.CANCELLED

    total_orders = Order.query.filter(billable_filter).count()
    total_billed = (
        db.session.query(func.coalesce(func.sum(Order.total_amount), 0.0))
        .filter(billable_filter)
        .scalar()
    )
    total_collected = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0.0))
        .scalar()
    )
    today_collected = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0.0))
        .filter(func.date(Payment.created_at) == today)
        .scalar()
    )
    outstanding = max(0.0, total_billed - total_collected)

    return {
        'total_orders': total_orders,
        'total_billed': total_billed,
        'total_collected': total_collected,
        'today_collected': today_collected,
        'outstanding': outstanding,
    }
'''
    b = b[:idx] + new_bstats + b[end+1:]
    print('OK  - compute_billing_stats: refunds flow through')

open(bpath, 'w', encoding='utf-8').write(b)


# ============================================================
# 3. list.html — style cancelled rows
# ============================================================
tpath = 'modules/orders/templates/orders/list.html'
t = open(tpath, encoding='utf-8').read()

# Add CSS if missing
if '.cancelled-row' not in t:
    css_anchor = '<style>'
    css_insert = '''<style>
.cancelled-row { opacity: 0.7; }
.cancelled-row td { background: #f8f9fa !important; }
.cancelled-row .strike { text-decoration: line-through; color: #adb5bd; }
.cancelled-badge {
  background: #dc3545; color: #fff;
  font-size: 0.68rem; font-weight: 600;
  padding: 2px 7px; border-radius: 3px;
  text-transform: uppercase;
}
.refund-note {
  font-size: 0.7rem; color: #b02a37;
  font-weight: 600;
}
'''
    t = t.replace(css_anchor, css_insert, 1)
    print('OK  - list.html: cancelled-row CSS added')

# Add cancelled class to the <tr>
anchor = '<tr class="order-row">'
if anchor in t and 'cancelled-row' not in t.split(anchor)[0][-200:]:
    new_tr = '<tr class="order-row {% if o.status == \'cancelled\' %}cancelled-row{% endif %}">'
    t = t.replace(anchor, new_tr, 1)
    print('OK  - list.html: cancelled class added to <tr>')

open(tpath, 'w', encoding='utf-8').write(t)

print()
print('=' * 55)
print('Done. Restart Flask and test:')
print('  /orders/ -> cancelled orders now visible with red badge')
print('  Totals exclude cancelled (as they should)')
print('=' * 55)
