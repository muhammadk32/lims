# Add phone + test search to Test Reports filters and query
import os

# ---------- 1. Update reports/routes.py — accept phone + test params ----------
rp = 'modules/reports/routes.py'
r = open(rp, encoding='utf-8').read()

old_q = """    status = request.args.get('status', 'approved').strip()
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
        )"""

new_q = """    status = request.args.get('status', 'approved').strip()
    q = request.args.get('q', '').strip()
    phone = request.args.get('phone', '').strip()
    test = request.args.get('test', '').strip()

    query = Order.query

    if status == 'all':
        query = query.filter(Order.status != OrderStatus.CANCELLED)
    elif status in OrderStatus.CHOICES:
        query = query.filter(Order.status == status)
    else:
        query = query.filter(Order.status == OrderStatus.APPROVED)

    from modules.patients.models import Patient   # ← lazy
    from sqlalchemy import or_

    if q:
        like = f'%{q}%'
        query = query.join(Patient).filter(
            or_(
                Order.order_code.ilike(like),
                Patient.full_name.ilike(like),
                Patient.patient_code.ilike(like),
            )
        )

    if phone:
        if 'patients' not in [str(m).lower() for m in query.column_descriptions]:
            query = query.join(Patient, Order.patient_id == Patient.id, isouter=True)
        query = query.filter(Patient.phone.ilike(f'%{phone}%'))

    if test:
        from modules.orders.models import OrderItem
        from modules.tests.models import Test
        query = (query
                 .join(OrderItem, OrderItem.order_id == Order.id)
                 .join(Test, Test.id == OrderItem.test_id)
                 .filter(or_(
                     Test.name.ilike(f'%{test}%'),
                     Test.code.ilike(f'%{test}%'),
                 ))
                 .distinct())"""

if old_q in r:
    r = r.replace(old_q, new_q, 1)
    # Pass new params to template
    r = r.replace(
        "return render_template('reports/list.html', orders=orders, status=status, q=q)",
        "return render_template('reports/list.html', orders=orders, status=status, q=q, phone=phone, test=test)",
        1,
    )
    open(rp, 'w', encoding='utf-8').write(r)
    print('OK  - routes.py: phone + test filters added')
else:
    print('WARN - route query block not matched')


# ---------- 2. Update template filters ----------
tp = 'modules/reports/templates/reports/list.html'
t = open(tp, encoding='utf-8').read()

# 2a. Change filter grid to 4 columns
t = t.replace(
    '  grid-template-columns: 2fr 1fr auto;',
    '  grid-template-columns: 2fr 1.5fr 1.5fr 1fr auto;',
    1,
)

# 2b. Add phone + test inputs before the Status field
old = '''    <div class="tr-field">
      <label>Status</label>'''
new = '''    <div class="tr-field">
      <label>Mobile #</label>
      <input type="tel" name="phone" value="{{ phone or '' }}"
             placeholder="0300-1234567">
    </div>
    <div class="tr-field">
      <label>Test</label>
      <input type="text" name="test" value="{{ test or '' }}"
             placeholder="Test name or code">
    </div>
    <div class="tr-field">
      <label>Status</label>'''
if old in t:
    t = t.replace(old, new, 1)
    print('OK  - template: phone + test inputs added')
else:
    print('WARN - template filter anchor not found')

open(tp, 'w', encoding='utf-8').write(t)

print()
print('=' * 55)
print('Done. Restart Flask and try searching by phone or test.')
print('=' * 55)
