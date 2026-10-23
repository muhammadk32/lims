import sqlite3
c = sqlite3.connect("instance/database.db")
# find LFTs test
t = c.execute("select id, name from tests where name like '%Liver Function%' or name like '%LFT%'").fetchall()
print("tests:", t)
# get the order
o = c.execute("""
  select oi.id, oi.result_value, oi.result_notes
  from order_items oi where oi.test_id = ? order by oi.id desc limit 3
""", (t[0][0],)).fetchall() if t else []
print("order_items:", o)
# check result table
r = c.execute("""
  select r.* from results r
  join order_items oi on oi.id = r.order_item_id
  where oi.test_id = ?
""" , (t[0][0],)).fetchall() if t else []
print("results rows:", len(r))
if r:
    cols = [d[0] for d in c.execute("select * from results limit 0").description]
    for row in r[:3]:
        for k, v in zip(cols, row):
            if v and isinstance(v, str) and ('<' in v or 'para' in v.lower()):
                print(f"  {k} = {v[:200]}")
