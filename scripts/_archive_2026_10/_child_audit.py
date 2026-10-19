import sqlite3
c = sqlite3.connect("instance/database.db")
print("=== Check Platelet Count (aid=92) ===")
row = c.execute("select id, name, is_panel, price from tests where adamlab_id=92").fetchone()
print("test row:", row)
if row:
    parents = c.execute("""
      select t.name, t.adamlab_id from panel_parameters pp
      join tests t on t.id = pp.panel_id where pp.test_id=?
    """, (row[0],)).fetchall()
    print("child of panels:", parents)
    kids = c.execute("select count(*) from panel_parameters where panel_id=?", (row[0],)).fetchone()[0]
    print("its own children:", kids)

print()
print("=== Sample across zero-price T rows ===")
for aid in (92, 107, 108, 109, 176, 179, 186, 188, 217, 221):
    r = c.execute("select id, name, is_panel from tests where adamlab_id=?", (aid,)).fetchone()
    if not r: continue
    tid, name, is_panel = r
    par = c.execute("select count(*) from panel_parameters where test_id=?", (tid,)).fetchone()[0]
    kids = c.execute("select count(*) from panel_parameters where panel_id=?", (tid,)).fetchone()[0]
    print(f"aid={aid} name={name[:30]:30} is_panel={is_panel} in_panels={par} children={kids}")
