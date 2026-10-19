import sqlite3
c = sqlite3.connect("instance/database.db")
cols = [r[1] for r in c.execute("pragma table_info(tests)")]
print("specimen_id present:", "specimen_id" in cols)
print("all columns:", cols)

# what alembic thinks is applied
print("alembic_version:", c.execute("select version_num from alembic_version").fetchall())
