import sqlite3
c = sqlite3.connect("instance/database.db")
print("ranges with test linked:", c.execute("select count(*) from test_reference_ranges trr join tests t on t.id=trr.test_id where t.adamlab_id is not null").fetchone()[0])
print("tests with >=1 range:", c.execute("select count(distinct test_id) from test_reference_ranges").fetchone()[0])
print()
print("sample: LDH ranges")
for r in c.execute("""
  select t.name, trr.gender, trr.age_min_years, trr.age_max_years,
         trr.age_min_days, trr.age_max_days, trr.range_text, trr.critical_value
  from test_reference_ranges trr join tests t on t.id=trr.test_id
  where t.name like 'LDH%' limit 10
"""): print(r)
