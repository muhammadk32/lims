# Add date range to Test Reports filters + query
import os

# ---------- 1. Route — accept date_from / date_to ----------
rp = 'modules/reports/routes.py'
r = open(rp, encoding='utf-8').read()

# Add date parsing right after the other params
old = """    status = request.args.get('status', 'approved').strip()
    q = request.args.get('q', '').strip()
    phone = request.args.get('phone', '').strip()
    test = request.args.get('test', '').strip()

    query = Order.query"""

new = """    status = request.args.get('status', 'approved').strip()
    q = request.args.get('q', '').strip()
    phone = request.args.get('phone', '').strip()
    test = request.args.get('test', '').strip()
    date_from_str = request.args.get('date_from', '').strip()
    date_to_str = request.args.get('date_to', '').strip()

    from datetime import datetime as _dt, date as _d

    today = _d.today()
    date_from = None
    date_to = None
    if date_from_str:
        try:
            date_from = _dt.strptime(date_from_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            date_from = None
    if date_to_str:
        try:
            date_to = _dt.strptime(date_to_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            date_to = None

    query = Order.query"""

if old in r:
    r = r.replace(old, new, 1)
    print('OK  - route: date params parsed')
else:
    print('WARN - route params anchor not found')

# Add date filter to query (after status filter block)
old_q = """    from modules.patients.models import Patient   # ← lazy
    from sqlalchemy import or_
"""
new_q = """    if date_from:
        query = query.filter(func.date(Order.created_at) >= date_from)
    if date_to:
        query = query.filter(func.date(Order.created_at) <= date_to)

    from modules.patients.models import Patient   # ← lazy
    from sqlalchemy import or_
"""
if old_q in r:
    r = r.replace(old_q, new_q, 1)
    print('OK  - route: date filter applied')
else:
    print('WARN - date filter anchor not found')

# Add func import at top if missing
if 'from sqlalchemy import func' not in r:
    r = r.replace(
        'from extensions import db',
        'from extensions import db\nfrom sqlalchemy import func',
        1,
    )
    print('OK  - route: sqlalchemy.func imported')

# Pass new params to template
r = r.replace(
    "return render_template('reports/list.html', orders=orders, status=status, q=q, phone=phone, test=test)",
    "return render_template('reports/list.html', orders=orders, status=status, q=q, phone=phone, test=test, date_from=date_from_str, date_to=date_to_str, today=today.strftime('%Y-%m-%d'))",
    1,
)

open(rp, 'w', encoding='utf-8').write(r)


# ---------- 2. Template — add date inputs ----------
tp = 'modules/reports/templates/reports/list.html'
t = open(tp, encoding='utf-8').read()

# 2a. Add date fields before the Search field
old_filter_start = '''  <form method="GET" class="tr-filter">
    <div class="tr-field">
      <label>Search</label>'''
new_filter_start = '''  <form method="GET" class="tr-filter">
    <div class="tr-field">
      <label>From</label>
      <input type="date" name="date_from" value="{{ date_from or '' }}">
    </div>
    <div class="tr-field">
      <label>To</label>
      <input type="date" name="date_to" value="{{ date_to or today }}">
    </div>
    <div class="tr-field">
      <label>Search</label>'''
if old_filter_start in t:
    t = t.replace(old_filter_start, new_filter_start, 1)
    print('OK  - template: date inputs added')
else:
    print('WARN - filter form anchor not found')

# 2b. Wider grid for 7 fields
t = t.replace(
    '  grid-template-columns: 2fr 1.5fr 1.5fr 1fr auto;',
    '  grid-template-columns: 1fr 1fr 1.6fr 1.2fr 1.2fr 1fr auto;',
    1,
)
# Fallback if the 5-col version wasn't applied
t = t.replace(
    '  grid-template-columns: 2fr 1fr auto;',
    '  grid-template-columns: 1fr 1fr 1.6fr 1.2fr 1.2fr 1fr auto;',
    1,
)

open(tp, 'w', encoding='utf-8').write(t)

print()
print('=' * 55)
print('Done. Restart Flask.')
print('  Date range + phone + test + status all work together.')
print('=' * 55)
