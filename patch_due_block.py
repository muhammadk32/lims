"""
Block PDF reports when order has balance due.
Patches:
  modules/reports/routes.py  → order_pdf, view_pdf
  modules/orders/routes.py   → print_order
"""
import re

GUARD = """    # Block report if balance is due
    if order.balance_due > 0.01:
        from flask import flash
        flash(
            f'Report blocked - Rs {order.balance_due:.0f} balance due. '
            f'Please record payment first.',
            'warning',
        )
        from flask import redirect, url_for
        return redirect(url_for('orders.view_order', order_id=order.id))

"""


def patch(path, targets):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    patched = 0
    for anchor in targets:
        if anchor not in src:
            print(f'  SKIP: anchor not found in {path}: {anchor[:60]}')
            continue
        if GUARD in src.split(anchor)[1][:400]:
            print(f'  SKIP: guard already present before {anchor[:40]}')
            continue
        src = src.replace(anchor, anchor + '\n' + GUARD, 1)
        patched += 1

    if patched:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(src)
    print(f'  {path}: {patched} function(s) guarded')


print('Patching reports + orders routes...')
patch('modules/reports/routes.py', [
    'def order_pdf(order_id):\n    order = _get_order_or_404(order_id)\n',
    'def view_pdf(order_id):\n    order = _get_order_or_404(order_id)\n',
])
patch('modules/orders/routes.py', [
    'def print_order(order_id):\n    order = _get_order_or_404(order_id)\n',
])
print('Done.')
