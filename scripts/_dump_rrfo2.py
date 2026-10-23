"""Debug: what does _rrfo return for LFTs children?"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from modules.orders.models import Order
from modules.tests.ranges import resolve_range_for_order as _rrfo

app = create_app()
with app.app_context():
    o = Order.query.get(456)
    for item in o.top_level_items:
        if item.test and 'Liver' in (item.test.name or ''):
            for child in item.children:
                rng = _rrfo(child.test, o) or '-'
                print(f"{child.test.name}: {rng!r}")
                # show repr to see exact bytes
                print(f"  bytes: {rng.encode('utf-8')[:200]}")
