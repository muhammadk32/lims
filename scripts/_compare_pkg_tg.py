import json, os
DATA = os.path.join("scripts", "adamlab_import")
def load(n):
    with open(os.path.join(DATA, f"{n}.json"), "r", encoding="utf-8") as f:
        return json.load(f)

pkg = load("packagetestdetail")
tg = load("testgroupdetail")

pkg_links = {(r["packagecode"], r["testcode"]) for r in pkg}
tg_links = {(r["groupcode"], r["testcode"]) for r in tg}

overlap = pkg_links & tg_links
pkg_only = pkg_links - tg_links
print(f"packagetestdetail links: {len(pkg_links)}")
print(f"testgroupdetail links:   {len(tg_links)}")
print(f"overlap:                 {len(overlap)}")
print(f"package only (not in tg): {len(pkg_only)}")
print()
print("Package-only sample:")
for l in list(pkg_only)[:10]:
    print(f"  {l}")

# Which are the 11 package codes?
codes = {r["packagecode"] for r in pkg}
print(f"\n11 package codes: {sorted(codes)}")
# Are any of these in testgroupdetail's groupcodes?
tg_codes = {r["groupcode"] for r in tg}
print(f"of these, in testgroupdetail: {len(codes & tg_codes)}")
