from app import create_app
from extensions import db
app = create_app()
ctx = app.app_context()
ctx.push()
from modules.orders.models import Order
o = Order.query.get(447)
print("Order status:", o.status)
print("all_results_done:", o.all_results_done)
for t in o.top_level_items:
    print(f"  item {t.id} {t.test.name}: has_result={t.has_result} is_verifiable={t.is_verifiable} children={len(t.children)}")
    for c in t.children:
        print(f"    child {c.id} {c.test.name}: value={c.result_value!r}")
