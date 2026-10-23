import sqlite3
c = sqlite3.connect("instance/database.db")
for r in c.execute("""
  select t.code, t.name, t.is_active, t.result_format
  from tests t where t.result_format='package'
  order by t.name
"""):
    print(r)
