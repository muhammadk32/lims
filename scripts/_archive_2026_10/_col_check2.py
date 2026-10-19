import sqlite3
c = sqlite3.connect("instance/database.db")
cols = [r[1] for r in c.execute("pragma table_info(tests)")]
print("sub_department_id in DB:", "sub_department_id" in cols)
print("alembic_version:", c.execute("select version_num from alembic_version").fetchall())
