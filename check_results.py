from app import create_app
from extensions import db
from modules.orders.models import Order, OrderItem
from modules.results.validators import check_result

app = create_app()
with app.app_context():
    print("Orders:", Order.query.count())
    print(
        "Items with results:",
        OrderItem.query.filter(OrderItem.result_value.isnot(None)).count(),
    )
    print(
        "Completed orders:",
        Order.query.filter_by(status="completed").count(),
    )
    print()

    # Test the validator
    cases = [
        ("70 - 100", "85", "normal"),
        ("70 - 100", "250", "abnormal"),
        ("< 5",      "3",  "normal"),
        ("< 5",      "12", "abnormal"),
        ("> 40",     "55", "normal"),
        ("> 40",     "30", "abnormal"),
    ]
    for rng, val, expect in cases:
        got = check_result(rng, val)
        flag = "OK" if got == expect else "FAIL"
        print(f"  [{flag}] check_result({rng!r}, {val!r}) = {got}  (expected {expect})")