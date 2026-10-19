import sqlite3
c = sqlite3.connect("instance/database.db")
print("laboratories cols:", [r[1] for r in c.execute("pragma table_info(laboratories)")])
print("alembic_version:", c.execute("select version_num from alembic_version").fetchall())
