import sqlite3
c = sqlite3.connect("instance/database.db")
print("=== Laboratories and their rate categories ===")
rows = c.execute("""
  select l.id, l.name, l.rate_category_id, rc.code, rc.name
  from laboratories l
  left join rate_categories rc on rc.id = l.rate_category_id
  order by l.id
""").fetchall()
for r in rows:
    print(r)
print()
print("=== Latest 5 orders with their commissions ===")
for r in c.execute("""
  select o.id, o.order_code, o.company_id, o.commission_amount, o.total_amount,
         (select count(*) from order_items oi where oi.order_id=o.id and oi.parent_item_id is null) as items
  from orders o order by o.id desc limit 5
"""):
    print(r)
print()
print("=== Latest 5 order_items with rate_category source ===")
for r in c.execute("""
  select oi.id, oi.order_id, oi.test_id, oi.price,
         oi.applied_discount_pct, oi.applied_discount_amount, oi.discount_source
  from order_items oi
  where oi.discount_source = 'rate_category'
  order by oi.id desc limit 5
"""):
    print(r)
