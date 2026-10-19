import sqlite3
c = sqlite3.connect("instance/database.db")
print("=== Rate categories ===")
for r in c.execute("select id, name, code from rate_categories order by id"):
    print(r)

print("\n=== Test link counts per rate category ===")
for r in c.execute("""
  select rc.id, rc.name,
         count(*) as total_rows,
         count(distinct rct.test_id) as distinct_tests
  from rate_categories rc
  left join rate_category_tests rct on rct.rate_category_id = rc.id
  group by rc.id order by rc.id
"""):
    print(r)

print("\n=== Talha: rows pointing to inactive / child tests? ===")
for r in c.execute("""
  select t.is_active, count(*) from rate_category_tests rct
  join tests t on t.id = rct.test_id
  join rate_categories rc on rc.id = rct.rate_category_id
  where rc.name like 'Talha%'
  group by t.is_active
"""):
    print(r)
