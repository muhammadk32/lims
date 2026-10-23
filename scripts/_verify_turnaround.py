import sqlite3
c = sqlite3.connect("instance/database.db")
print("Samples after backfill:")
for r in c.execute("""
  select t.code, t.name, t.turnaround_hours, td.description, td.report_date
  from tests t
  left join test_days td on td.adamlab_id = (
    select cast(value as integer) from json_each('{}')
  )
  where t.adamlab_id in (2, 4, 13, 15, 20, 42, 200)
"""):
    print(r)
