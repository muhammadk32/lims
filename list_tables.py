import os
import sqlite3

DB = os.path.join("instance", "database.db")

if not os.path.exists(DB):
    print(f"DB not found: {DB}")
else:
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    print([r[0] for r in cur.fetchall()])
    con.close()