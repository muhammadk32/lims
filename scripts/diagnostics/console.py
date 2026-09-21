import sqlite3, os, sys

# Flask resolves "sqlite:///database.db" to <project>/instance/database.db
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "instance", "database.db")

def _con():
    if not os.path.exists(DB_PATH):
        print(f"!! DB not found: {DB_PATH}")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)

def tables():
    con = _con(); cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    for (n,) in cur.fetchall():
        print(" -", n)
    con.close()

def schema(table):
    con = _con(); cur = con.cursor()
    cur.execute("SELECT sql FROM sqlite_master WHERE name=?", (table,))
    row = cur.fetchone()
    print(row[0] if row else f"(no such table: {table})")
    con.close()

def count(table):
    con = _con(); cur = con.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    print(cur.fetchone()[0])
    con.close()

def audit(n=10):
    con = _con(); cur = con.cursor()
    try:
        cur.execute("SELECT id, action, entity_type, entity_id, description, created_at "
                    "FROM audit_logs ORDER BY id DESC LIMIT ?", (n,))
        rows = cur.fetchall()
        if not rows:
            print("(audit_logs is empty)")
        for r in rows:
            print(r)
    except sqlite3.OperationalError as e:
        print("(audit_logs missing?):", e)
    con.close()

def sql(q):
    con = _con(); cur = con.cursor()
    cur.execute(q)
    for row in cur.fetchall():
        print(row)
    con.close()

def shell():
    import code
    con = _con()
    code.interact(banner="LIMS console — `con`, `cur` ready. Type exit() to quit.",
                  local={"con": con, "cur": con.cursor()})

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:            tables()
    elif args[0] == "tables":  tables()
    elif args[0] == "schema":  schema(args[1])
    elif args[0] == "count":   count(args[1])
    elif args[0] == "audit":   audit(int(args[1]) if len(args) > 1 else 10)
    elif args[0] == "sql":     sql(args[1])
    elif args[0] == "shell":   shell()
    else:
        print("usage: python console.py [tables|schema T|count T|audit N|sql Q|shell]")