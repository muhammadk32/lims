import sqlite3
c = sqlite3.connect("instance/database.db")
print("panels (is_panel=1):", c.execute("select count(*) from tests where is_panel=1").fetchone()[0])
print("total panel links:", c.execute("select count(*) from panel_parameters").fetchone()[0])
print("orphan links (panel or child missing):", c.execute("select count(*) from panel_parameters pp left join tests p on p.id=pp.panel_id left join tests t on t.id=pp.test_id where p.id is null or t.id is null").fetchone()[0])
