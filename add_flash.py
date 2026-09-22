"""Add the discount warning flash to orders/services.py."""
import re

path = 'modules/orders/services.py'

with open(path, 'r', encoding='utf-8') as f:
    src = f.read()

if '_warn_full_discount:' in src:
    print('SKIP - flash already present')
    raise SystemExit(0)

# Find the create_order function's return statement
# The pattern is: after 'order.recompute_total()' there's a pay amount block,
# then db.session.commit(), then log_action(...), then 'return order'

# Find the first 'return order' AFTER '_warn_full_discount'
flag_pos = src.find('_warn_full_discount = ')
if flag_pos == -1:
    print('ERR - flag not found')
    raise SystemExit(1)

ret_pos = src.find('    return order', flag_pos)
if ret_pos == -1:
    print('ERR - return order not found after flag')
    raise SystemExit(1)

# Insert the flash block right before 'return order'
flash_block = '''    # Flash a warning if the discount wiped the full amount
    if _warn_full_discount:
        try:
            from flask import flash
            flash(
                'Note: order ' + order.order_code +
                ' has a 100 percent discount - Rs 0 is due from the patient.',
                'warning',
            )
        except Exception:
            pass

'''

src = src[:ret_pos] + flash_block + src[ret_pos:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(src)

print('OK - flash warning inserted')
