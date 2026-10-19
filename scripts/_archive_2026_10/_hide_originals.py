import sqlite3
c = sqlite3.connect("instance/database.db")
cur = c.cursor()
cur.execute("update tests set is_active=0 where adamlab_id is null")
c.commit()
print("original tests now inactive:", cur.rowcount)
print("active tests:", c.execute("select count(*) from tests where is_active=1").fetchone()[0])
