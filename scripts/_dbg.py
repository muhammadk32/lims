import sqlite3
c = sqlite3.connect('instance/database.db')
print("--- lookup by name ---")
for r in c.execute("select id, adamlab_id, code, name, price from tests where name like '%ABNORMAL%' limit 5"):
    print(r)
print("--- first 5 rows by id ---")
for r in c.execute("select id, adamlab_id, code, name, price from tests order by id limit 5"):
    print(r)