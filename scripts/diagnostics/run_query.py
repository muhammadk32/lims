import os
import sqlite3
import sys

DB = os.path.join("instance", "database.db")
sql = sys.argv[1] if len(sys.argv) > 1 else "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"

con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute(sql)
for row in cur.fetchall():
    print(row)
con.close()
