import sqlite3
c = sqlite3.connect("instance/database.db")
n = c.execute("select count(*) from test_reference_ranges where range_text='0 - 0' and (notes is null or notes='')").fetchone()[0]
print("empty 0-0 ranges:", n)
c.execute("delete from test_reference_ranges where range_text='0 - 0' and (notes is null or notes='')")
c.commit()
print("remaining:", c.execute("select count(*) from test_reference_ranges").fetchone()[0])
