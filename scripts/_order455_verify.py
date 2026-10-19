import sqlite3
c = sqlite3.connect("instance/database.db")
# Check that TALHA LAB's rate category really drove commission
# Manually recompute for order 455:
row = c.execute("""
  select o.id, o.subtotal if 0 else o.total_amount, o.commission_amount, l.rate_category_id,
         rc.code, rc.name
  from orders o
  join laboratories l on l.id = o.company_id
  left join rate_categories rc on rc.id = l.rate_category_id
  where o.id = 455
""").fetchone() if False else None
# simpler:
for r in c.execute("""
  select o.id, o.total_amount, o.commission_amount, l.name, l.rate_category_id, rc.name,
         (select commission from rate_category_rates where rate_category_id=l.rate_category_id order by section_code, id limit 1) as first_commission
  from orders o
  join laboratories l on l.id = o.company_id
  left join rate_categories rc on rc.id = l.rate_category_id
  where o.id = 455
"""):
    print("order:", r)
    print(f"expected commission = total {r[1]} x {r[6] or 0}% = {(r[1] or 0) * (r[6] or 0) / 100:.2f}")
