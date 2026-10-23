"""Inspect packagetestdetail structure."""
import json, os
DATA = os.path.join("scripts", "adamlab_import")
with open(os.path.join(DATA, "packagetestdetail.json"), "r", encoding="utf-8") as f:
    pkg = json.load(f)
print(f"packagetestdetail rows: {len(pkg)}")
print("sample:")
for r in pkg[:5]:
    print(r)

# how many distinct package codes?
codes = {r["packagecode"] for r in pkg}
print(f"\ndistinct package codes: {len(codes)}")
print(f"sample codes: {list(codes)[:10]}")

# do those codes map to tests?
import json
with open(os.path.join(DATA, "labtestdetail.json"), "r", encoding="utf-8") as f:
    lt = json.load(f)
testcodes = {r["testcode"] for r in lt}
matched = codes & testcodes
print(f"\npackage codes that are also tests: {len(matched)}/{len(codes)}")
