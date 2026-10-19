import sqlite3
c = sqlite3.connect("instance/database.db")
# assign "Special Test" (category code 2) to the first lab
cat_id = c.execute("select id from rate_categories where code=2").fetchone()[0]
lab_id = c.execute("select id from laboratories limit 1").fetchone()[0]
c.execute("update laboratories set rate_category_id=? where id=?", (cat_id, lab_id))
c.commit()
print("lab", lab_id, "-> rate category", cat_id)
