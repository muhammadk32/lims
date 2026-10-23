import sqlite3
c = sqlite3.connect("instance/database.db")
for code in ("1143", "21158", "21159"):
    row = c.execute("select id, code, name from tests where code=?", (code,)).fetchone()
    if not row: 
        print(f"{code}: not found"); continue
    tid = row[0]
    in_panel = c.execute("select 1 from panel_parameters where test_id=? limit 1", (tid,)).fetchone()
    is_param = c.execute("select 1 from test_parameters where test_id=? limit 1", (tid,)).fetchone()
    parent_tests = c.execute("""
      select distinct parent_t.id, parent_t.name from test_parameters tp
      join tests parent_t on parent_t.id = tp.test_id where tp.test_id=?
    """, (tid,)).fetchall()
    print(f"{code} {row[2]!r}: in_panel={bool(in_panel)} has_parameters={bool(is_param)}")
