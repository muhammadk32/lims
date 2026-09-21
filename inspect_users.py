import os
import sqlite3

DB = os.path.join("instance", "database.db")

con = sqlite3.connect(DB)
cur = con.cursor()

# Table schema
cur.execute("PRAGMA table_info(users)")
print("Columns in `users`:")
for cid, name, ctype, notnull, default, pk in cur.fetchall():
    pk_flag = " (PK)" if pk else ""
    print(f"  {name:<16} {ctype:<12} notnull={notnull}{pk_flag}")

# Row count
cur.execute("SELECT COUNT(*) FROM users")
print(f"\nRows in `users`: {cur.fetchone()[0]}")

# Show users
cur.execute("SELECT id, username, email, role FROM users")
print("\nUsers:")
for row in cur.fetchall():
    print(f"  {row}")

con.close()