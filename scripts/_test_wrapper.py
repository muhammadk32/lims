import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from modules.orders.models import Order
from modules.reports.pdf import results_table as rt

app = create_app()
with app.app_context():
    o = Order.query.get(456)
    d3 = [it for it in o.top_level_items if 'Hydroxy' in (it.test.name or '')]
    if d3:
        item = d3[0]
        rng = rt._rrfo(item.test, o)
        print("_rrfo result:", repr(rng))
        print("bytes:", rng.encode('utf-8')[:300])
