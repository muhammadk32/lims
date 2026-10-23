import sqlite3
c = sqlite3.connect("instance/database.db")
print("Package codes from source (11):")
for r in c.execute("""
  select t.code, t.name, t.result_format, t.is_panel
  from tests t where t.adamlab_id in (47765,47766,47767,47768,47769,47770,47771,47772,47775,47776,47783)
  order by t.adamlab_id
"""):
    print(r)
