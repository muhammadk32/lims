import sqlite3
c = sqlite3.connect("instance/database.db")

# find the failing order via lab/verify context — most recent order for patient
orders = c.execute("""
  select o.id, o.order_code from orders o
  where o.id in (
    select oi.order_id from order_items oi
    where oi.test_id in (1893, 1894, 1895)  -- LFTs ids
  ) order by o.id desc limit 3
""").fetchall()
print("orders with LFTs:", orders)

for oid, code in orders:
    print(f"\n=== Order {code} (id={oid}) ===")
    for r in c.execute("""
      select oi.id, oi.test_id, t.name, oi.result_value, oi.result_notes
      from order_items oi join tests t on t.id = oi.test_id
      where oi.order_id = ? and (oi.test_id = 1893 or oi.parent_item_id in (select id from order_items where order_id=? and test_id=1893))
    """, (oid, oid)).fetchall():
        print(f"  item={r[0]} test={r[2][:30]:30} val={r[3]} notes={r[4]}")
        # check results table
        for rr in c.execute("select * from results where order_item_id=?", (r[0],)).fetchall():
            cols = [d[0] for d in c.execute("select * from results limit 0").description]
            for k, v in zip(cols, rr):
                if v and isinstance(v, str) and ('para' in v.lower() or 'br' in v.lower()):
                    print(f"      {k} = {v[:200]}")
