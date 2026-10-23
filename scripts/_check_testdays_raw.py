import json, os
DATA = os.path.join("scripts", "adamlab_import")
with open(os.path.join(DATA, "labtestdetail.json"), "r", encoding="utf-8") as f:
    lt = json.load(f)
sample = [r for r in lt if r.get("testcode") in (2, 4, 9, 13, 15, 17)]
for r in sample:
    print(f"  testcode={r['testcode']:6} name={r['testname'][:40]:40} TestDays={r.get('TestDays')}")
