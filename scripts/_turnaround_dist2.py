import sqlite3
c = sqlite3.connect("instance/database.db")
print("\nDistinct turnaround_hours after backfill:")
for r in c.execute("""
  select turnaround_hours, count(*) from tests where adamlab_id is not null
  group by turnaround_hours order by count(*) desc
"""):
    print(r)
