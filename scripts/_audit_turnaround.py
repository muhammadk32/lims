import json, os, sqlite3
DATA = os.path.join("scripts", "adamlab_import")
with open(os.path.join(DATA, "labtestdetail.json"), "r", encoding="utf-8") as f:
    lt = json.load(f)

# tests with NO TestDays in source
no_testdays = [r for r in lt if r.get("TestDays") is None]
print(f"AdamLab tests with NO TestDays value: {len(no_testdays)}")
for r in no_testdays[:10]:
    print(f"  code={r['testcode']:6} {r['testname'][:40]!r}")

# distribution of TestDays values
from collections import Counter
dist = Counter(r.get("TestDays") for r in lt)
print(f"\nTestDays distribution:")
for val, cnt in sorted(dist.items(), key=lambda x: -x[1])[:10]:
    print(f"  TestDays={val}: {cnt} tests")

# how many in DB have turnaround_hours = 24
c = sqlite3.connect("instance/database.db")
n24 = c.execute("select count(*) from tests where turnaround_hours=24 and adamlab_id is not null").fetchone()[0]
total = c.execute("select count(*) from tests where adamlab_id is not null").fetchone()[0]
print(f"\nDB: {n24}/{total} tests have turnaround_hours=24")
