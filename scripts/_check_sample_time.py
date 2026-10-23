import sqlite3
c = sqlite3.connect("instance/database.db")
for r in c.execute("""
  select t.code, t.name, t.specimen_id, t.sample_type, t.turnaround_hours
  from tests t where t.id in (select test_id from rate_category_tests where rate_category_id=2) limit 10
"""):
    print(r)
