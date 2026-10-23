import json, os
DATA = os.path.join("scripts", "adamlab_import")
with open(os.path.join(DATA, "ratelist.json"), "r", encoding="utf-8") as f:
    rl = json.load(f)
print(f"AdamLab ratelist rows: {len(rl)}")
print(f"distinct tests: {len({r['testcode'] for r in rl})}")
print("\nsample:")
for r in rl[:10]:
    print(f"  code={r['testcode']} name={r['testname']!r} rate={r['rate']}")

# how many are > 0
n_priced = sum(1 for r in rl if (r['rate'] or 0) > 0)
print(f"\npriced > 0: {n_priced}")
print(f"price = 0: {len(rl) - n_priced}")
