# From date defaults to today
import os

# ---------- 1. Route: default date_from to today ----------
rp = 'modules/reports/routes.py'
r = open(rp, encoding='utf-8').read()

old = """    date_from_str = request.args.get('date_from', '').strip()
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
            date_to = None"""

new = """    from datetime import datetime as _dt, date as _d

    today = _d.today()
    date_from_str = request.args.get('date_from', '').strip() or today.strftime('%Y-%m-%d')
    date_to_str = request.args.get('date_to', '').strip() or today.strftime('%Y-%m-%d')

    date_from = None
    date_to = None
    try:
        date_from = _dt.strptime(date_from_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        date_from = today
    try:
        date_to = _dt.strptime(date_to_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        date_to = today"""

if old in r:
    r = r.replace(old, new, 1)
    open(rp, 'w', encoding='utf-8').write(r)
    print('OK  - route: from date defaults to today')
else:
    print('WARN - route anchor not found')
