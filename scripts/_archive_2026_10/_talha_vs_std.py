import sqlite3
c = sqlite3.connect("instance/database.db")
std = {r[0] for r in c.execute("select test_id from rate_category_tests where rate_category_id=1")}
tal = {r[0] for r in c.execute("select test_id from rate_category_tests where rate_category_id=2")}
extra = tal - std
print("Standard count:", len(std))
print("Talha count:", len(tal))
print("Talha has but Standard doesn't:", len(extra))

print("\nSample extras:")
for tid in list(extra)[:15]:
    r = c.execute("select t.code, t.name, t.is_active, t.is_panel from tests t where t.id=?", (tid,)).fetchone()
    print(f"  id={tid} {r}")

# Are these child tests (in panel_parameters)?
print("\nAre extras child tests?")
n_child = 0
for tid in extra:
    is_child = c.execute("select 1 from panel_parameters where test_id=? limit 1", (tid,)).fetchone()
    if is_child: n_child += 1
print(f"  {n_child} of {len(extra)} extras are children of panels")

# Talha has fewer than Standard?
missing = std - tal
print("\nStandard has but Talha doesn't:", len(missing))
for tid in list(missing)[:5]:
    r = c.execute("select code, name from tests where id=?", (tid,)).fetchone()
    print(f"  {r}")
