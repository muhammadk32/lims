from app import create_app
from extensions import db
from modules.orders.models import Order, OrderItem

app = create_app()
with app.app_context():
    print("Total orders:", Order.query.count())
    print("Total order items:", OrderItem.query.count())
    print()

    for o in Order.query.limit(5):
        name = o.patient.full_name if o.patient else "(no patient)"
        print(f"  {o.order_code}  {name[:20]:20}  items={o.item_count}  "
              f"${o.total_amount:.2f}  {o.status}  paid={o.paid}")

    total_revenue = (
        db.session.query(db.func.coalesce(db.func.sum(Order.total_amount), 0.0))
        .filter(Order.paid == True)  # noqa: E712
        .scalar()
    )
    print()
    print(f"Total revenue (paid): ${total_revenue:.2f}")