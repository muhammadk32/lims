"""Find which item has the bad range for order 456."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from modules.orders.models import Order

app = create_app()
with app.app_context():
    o = Order.query.get(456)
    import re
    for it in o.top_level_items:
        print(f"\n=== {it.test.name} ===")
        print(f"  has_children: {it.has_children}")
        # check children
        for child in it.children:
            from modules.tests.ranges import resolve_range_for_order as rr
            rng = rr(child.test, o) or '-'
            print(f"  child {child.test.name}: {rng!r}")
