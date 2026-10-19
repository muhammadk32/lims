import sqlite3
c = sqlite3.connect("instance/database.db")
print("RateCategoryTest rows for cat 1:", c.execute("select count(*) from rate_category_tests where rate_category_id=1").fetchone()[0])
print("distinct test_id:", c.execute("select count(distinct test_id) from rate_category_tests where rate_category_id=1").fetchone()[0])
print()
print("active tests:", c.execute("select count(*) from tests where is_active=1").fetchone()[0])
print("active non-child tests:", c.execute("""
  select count(*) from tests t
  where t.is_active=1
    and not exists(select 1 from panel_parameters pp where pp.test_id=t.id)
""").fetchone()[0])
print()
print("sample linked (first 5):")
for r in c.execute("""
  select t.code, t.name, t.is_active from rate_category_tests rct
  join tests t on t.id=rct.test_id where rct.rate_category_id=1
  order by rct.sort_order limit 5
"""):
    print(r)
print()
print("count by active status:")
print(c.execute("""
  select t.is_active, count(*) from rate_category_tests rct
  join tests t on t.id=rct.test_id
  where rct.rate_category_id=1 group by t.is_active
""").fetchall())
