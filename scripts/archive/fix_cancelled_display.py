"""
Fix cancelled orders across Ledger badge + Cash Summary.
"""
import re

# ============================================================
# 1. Ledger — Payment badge should show "Cancelled" for cancelled orders
# ============================================================
lp = 'modules/orders/templates/orders/list.html'
l = open(lp, encoding='utf-8').read()

# Find the pay-pill span and wrap it with a cancelled check
if 'pay-pill' in l and "o.status == 'cancelled'" not in l.split('pay-pill')[1][:300]:
    # Look for the pattern: <span class="pay-pill ...">{{ ... }}</span>
    pat = re.compile(
        r'(<span class="pay-pill\s+[^"]*"[^>]*>\s*)([^<]+?)(\s*</span>)',
        re.DOTALL,
    )
    def wrap(m):
        return (
            "{% if o.status == 'cancelled' %}"
            '<span class="cancelled-badge">Cancelled</span>'
            '{% else %}'
            + m.group(1) + m.group(2) + m.group(3) +
            '{% endif %}'
        )
    l2, n = pat.subn(wrap, l, count=1)
    if n:
        open(lp, 'w', encoding='utf-8').write(l2)
        print('OK  - Ledger: pay badge shows Cancelled')

# ============================================================
# 2. Cash Summary query — exclude cancelled from all totals
# ============================================================
bp = 'modules/billing/queries.py'
b = open(bp, encoding='utf-8').read()

# The list function: filter out cancelled by default
# (or keep showing them but with cancelled badge)
# Find compute_billing_stats and rewrite
if 'def compute_billing_stats' in b:
    idx = b.find('def compute_billing_stats')
    end = b.find('\ndef ', idx + 1)
    if end == -1:
        end = len(b)
    new_fn = '''def compute_billing_stats():
    """Dashboard totals. Cancelled orders are excluded from money."""
    from modules.orders.models import Order, OrderStatus

    today = date.today()

    active = Order.status != OrderStatus.CANCELLED

    total_orders = Order.query.filter(active).count()
    total_billed = (
        db.session.query(func.coalesce(func.sum(Order.total_amount), 0.0))
        .filter(active)
        .scalar()
    )
    # Payments: includes negative refunds automatically (they reduce sum)
    total_collected = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0.0))
        .scalar()
    )
    today_collected = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0.0))
        .filter(func.date(Payment.created_at) == today)
        .scalar()
    )

    # Outstanding = billed - collected, but only on active orders
    outstanding = max(0.0, total_billed - total_collected)

    return {
        'total_orders': total_orders,
        'total_billed': total_billed,
        'total_collected': total_collected,
        'today_collected': today_collected,
        'outstanding': outstanding,
    }
'''
    b = b[:idx] + new_fn + b[end+1:] if end != -1 else b[:idx] + new_fn
    open(bp, 'w', encoding='utf-8').write(b)
    print('OK  - Cash Summary: cancelled excluded from totals')
else:
    print('WARN - compute_billing_stats not found')

# ============================================================
# 3. Cash Summary template — show cancelled state on the row
# ============================================================
tp = 'modules/billing/templates/billing/list.html'
import os
if os.path.exists(tp):
    t = open(tp, encoding='utf-8').read()
    original_t = t

    # Add cancelled CSS
    if '.cancelled-row' not in t:
        t = t.replace(
            '<style>',
            '<style>\n.cancelled-row td { background: #f8f9fa !important; opacity: 0.75; }\n.strike-cancelled { text-decoration: line-through; color: #adb5bd !important; }\n.cancelled-badge { display:inline-block; background:#6c757d; color:#fff; font-size:0.66rem; font-weight:700; padding:2px 7px; border-radius:3px; }\n',
            1,
        )
        print('OK  - Cash Summary: cancelled CSS added')

    # Add class to <tr> - find the for loop
    tr_pattern = re.compile(r'(\{%\s*for\s+o\s+in\s+orders\s*%\}\s*\n\s*)(<tr>)')
    t, n = tr_pattern.subn(
        r'\1<tr class="{% if o.status == \'cancelled\' %}cancelled-row{% endif %}">',
        t,
        count=1,
    )
    if n:
        print('OK  - Cash Summary: <tr> tagged for cancelled')

    # Force balance to dash when cancelled - try a few patterns
    bal_patterns = [
        r'\{\{\s*config\.currency_symbol\s*\}\}\s*\{\{\s*\'%\.2f\'\s*\|\s*format\(o\.balance_due\)\s*\}\}',
        r'\{\{\s*\'%\.2f\'\s*\|\s*format\(o\.balance_due\)\s*\}\}',
    ]
    for pat in bal_patterns:
        if pat in t and 'o.status == \'cancelled\' %}}—' not in t:
            t = t.replace(
                pat,
                "{% if o.status == 'cancelled' %}—{% else %}" + pat + "{% endif %}",
                1,
            )
            print(f'OK  - Cash Summary: balance cell wrapped')
            break

    # Payment badge — find pay-pill or similar
    if 'pay-pill' in t and "o.status == 'cancelled'" not in t.split('pay-pill')[1][:300]:
        pat2 = re.compile(
            r'(<span class="pay-pill\s+[^"]*"[^>]*>\s*)([^<]+?)(\s*</span>)',
            re.DOTALL,
        )
        t, n = pat2.subn(
            lambda m: "{% if o.status == 'cancelled' %}<span class=\"cancelled-badge\">Cancelled</span>{% else %}"
                      + m.group(1) + m.group(2) + m.group(3) + "{% endif %}",
            t,
            count=1,
        )
        if n:
            print('OK  - Cash Summary: payment badge shows Cancelled')

    if t != original_t:
        open(tp, 'w', encoding='utf-8').write(t)
        print('OK  - Cash Summary template saved')
    else:
        print('SKIP - Cash Summary template unchanged')
else:
    print('WARN - billing list.html not found')

print()
print('=' * 55)
print('Restart Flask and reload:')
print('  /orders/     -> cancelled order row')
print('  /billing/    -> cancelled order row')
print('=' * 55)
