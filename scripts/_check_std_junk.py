import sqlite3
c = sqlite3.connect("instance/database.db")
# Standard rate list
std = c.execute("select id from rate_categories where name='Standard Rate List'").fetchone()[0]
rows = c.execute("""
  select t.id, t.code, t.name, t.price, t.is_active
  from rate_category_tests rct
  join tests t on t.id = rct.test_id
  where rct.rate_category_id=?
  order by t.name
""", (std,)).fetchall()
print(f"Standard has {len(rows)} tests")
print("\nSamples with price=0 (likely junk):")
n_zero = 0
for r in rows:
    if (r[3] or 0) == 0:
        print(f"  {r[1]:8} {r[2][:50]:50} active={r[4]}")
        n_zero += 1
        if n_zero > 20: break
print(f"\ntotal zero-price: {sum(1 for r in rows if (r[3] or 0)==0)}")
