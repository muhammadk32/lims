# ============================================================
# Fix 1: payment_status when final_total = 0 (100% discount)
# Fix 2: flash warning for 100% discount (in the route, not service)
# ============================================================
import re

# ---------- Fix 1: models.py payment_status ----------
mpath = 'modules/orders/models.py'
with open(mpath, 'r', encoding='utf-8') as f:
    m = f.read()

old_ps = '''    @property
    def payment_status(self):
        if self.paid_amount <= 0.001:
            return 'unpaid'
        if self.is_fully_paid:
            return 'paid'
        return 'partial''''

new_ps = '''    @property
    def payment_status(self):
        # Nothing is owed (100%% discount or free order) -> treat as paid
        if (self.final_total or 0) <= 0.001:
            return 'paid'
        if self.paid_amount <= 0.001:
            return 'unpaid'
        if self.is_fully_paid:
            return 'paid'
        return 'partial''''

if 'Nothing is owed' in m:
    print('SKIP - payment_status already fixed')
elif old_ps in m:
    m = m.replace(old_ps, new_ps, 1)
    with open(mpath, 'w', encoding='utf-8') as f:
        f.write(m)
    print('OK - payment_status fixed in models.py')
else:
    # Try regex-based fallback
    pattern = r'(@property\s+def payment_status\(self\):\s+)(if self\.paid_amount <= 0\.001:\s+return \'unpaid\')'
    match = re.search(pattern, m)
    if match:
        m = re.sub(
            pattern,
            r'\1if (self.final_total or 0) <= 0.001:\n            return \'paid\'\n        \2',
            m, count=1,
        )
        with open(mpath, 'w', encoding='utf-8') as f:
            f.write(m)
        print('OK - payment_status fixed via regex')
    else:
        print('WARN - payment_status pattern not matched; check models.py manually')


# ---------- Fix 2: flash 100%% discount warning in routes.py ----------
rpath = 'modules/orders/routes.py'
with open(rpath, 'r', encoding='utf-8') as f:
    r = f.read()

if '100% discount' in r or '100 percent discount' in r:
    print('SKIP - routes.py flash already present')
else:
    # Find the success flash that mentions 'created for'
    anchor = "    flash(\n        f'Lab # {order.order_code} created for {patient.full_name} '"
    if anchor in r:
        warning = '''    # Warn receptionist if the discount wiped the full amount
    if order.subtotal > 0 and order.final_total <= 0.01:
        flash(
            f'Note: order {order.order_code} has a 100% discount - '
            f'Rs 0 is due from the patient.',
            'warning',
        )

'''
        r = r.replace(anchor, warning + anchor, 1)
        with open(rpath, 'w', encoding='utf-8') as f:
            f.write(r)
        print('OK - flash warning added in routes.py')
    else:
        print('WARN - could not find success flash anchor in routes.py')
        print('       showing the create_order flash area for manual edit:')
        idx = r.find('created for')
        if idx > 0:
            print(r[max(0, idx-200):idx+200])


print()
print('Done. Restart Flask and test:')
print('  Order 0926-19 -> should show "Paid" (green)')
print('  New 100% discount order -> should show yellow warning')
