# Attach pending_items to each order in verify_queue
p = 'modules/lab/routes.py'
s = open(p, encoding='utf-8').read()

old = """    items = q.get_verify_queue_items(search, date_from, date_to)
    orders = q.group_by_order(items)

    return render_template("""

new = """    items = q.get_verify_queue_items(search, date_from, date_to)
    orders = q.group_by_order(items)

    # Attach the pending items to each order so the template can expand them
    for order in orders:
        order.pending_items = [i for i in items if i.order_id == order.id]

    return render_template("""

if old in s:
    s = s.replace(old, new, 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('OK  - verify_queue: pending_items attached to each order')
elif 'order.pending_items = [i for i in items' in s:
    print('SKIP - already patched')
else:
    print('WARN - anchor not found')
