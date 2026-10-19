import sqlite3
c = sqlite3.connect("instance/database.db")
c.execute("delete from rate_category_tests where rate_category_id in (select id from rate_categories where name like '%(copy)%')")
c.execute("delete from rate_category_rates where rate_category_id in (select id from rate_categories where name like '%(copy)%')")
c.execute("delete from rate_categories where name like '%(copy)%'")
c.commit()
print("cleaned copies")
