import sqlite3
c = sqlite3.connect("instance/database.db")
for r in c.execute("""
  select rc.id, rc.name, count(*) rows, count(distinct rct.test_id) distinct_tests
  from rate_categories rc left join rate_category_tests rct on rct.rate_category_id = rc.id
  group by rc.id order by rc.id
"""):
    print(r)
