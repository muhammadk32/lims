import sqlite3
c = sqlite3.connect("instance/database.db")
print("=== All RateCategoryRate rows with rate_percent > 0 ===")
for r in c.execute("""
  select rc.code, rc.name, rcr.section_code, rcr.rate_percent, rcr.commission
  from rate_category_rates rcr
  join rate_categories rc on rc.id = rcr.rate_category_id
  where rcr.rate_percent > 0
  order by rcr.rate_percent desc
"""):
    print(r)

print()
print("=== First rate row for each category ===")
for r in c.execute("""
  select rc.code, rc.name,
    (select rcr.rate_percent from rate_category_rates rcr where rcr.rate_category_id=rc.id order by rcr.section_code, rcr.id limit 1) as first_pct,
    (select rcr.commission from rate_category_rates rcr where rcr.rate_category_id=rc.id order by rcr.section_code, rcr.id limit 1) as first_comm
  from rate_categories rc order by rc.code
"""):
    print(r)
