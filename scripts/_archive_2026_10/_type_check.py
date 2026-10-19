import sqlite3
c = sqlite3.connect("instance/database.db")
print("tests with analytes (TestParameter):", c.execute("select count(distinct test_id) from test_parameters").fetchone()[0])
print("tests that are panels (PanelParameter rows):", c.execute("select count(distinct panel_id) from panel_parameters").fetchone()[0])
print("both (panel AND has analytes):", c.execute("select count(*) from tests t where exists(select 1 from test_parameters tp where tp.test_id=t.id) and exists(select 1 from panel_parameters pp where pp.panel_id=t.id)").fetchone()[0])
print()
print("sample analytes for CBC:")
for r in c.execute("""
  select t.name, tp.name, tp.unit from test_parameters tp
  join tests t on t.id=tp.test_id
  where t.name like '%CBC%' or t.name like '%Complete Blood%' limit 10
"""): print(r)
