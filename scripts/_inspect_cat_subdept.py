import sqlite3
c = sqlite3.connect("instance/database.db")
print("=== TestCategories ===")
for r in c.execute("select id, name from test_categories order by name"):
    print(r)
print("\n=== SubDepartments ===")
for r in c.execute("select id, code, name, is_active from sub_departments order by name"):
    print(r)
