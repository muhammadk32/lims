import sqlite3
c = sqlite3.connect("instance/database.db")
print("=== order_items for order 455 ===")
for r in c.execute("""
  select oi.id, oi.test_id, oi.price, oi.applied_discount_pct,
         oi.applied_discount_amount, oi.discount_source
  from order_items oi
  where oi.order_id = 455 and oi.parent_item_id is null
"""):
    print(r)
print()
print("=== order 455 details ===")
r = c.execute("select id, order_code, company_id, subtotal if 0 else total_amount, commission_amount, discount_type, discount_percent, discount_amount from orders where id=455").fetchone()
print(r)
