import json, os, sqlite3
DATA = os.path.join("scripts","adamlab_import")
def load(n):
    with open(os.path.join(DATA, n+".json"),"r",encoding="utf-8") as f: return json.load(f)

lt = {r["testcode"]: r for r in load("labtestdetail")}
rl = {r["testcode"]: r for r in load("ratelist")}    # testcode -> rate
rl1 = {r["code"]: r for r in load("ratelist1")}      # code -> newrate

c = sqlite3.connect("instance/database.db")
sample = c.execute("select adamlab_id, code, name, price from tests where adamlab_id is not null and price=0 and is_active=1 limit 15").fetchall()
print("active tests with price=0:")
for aid, code, name, price in sample:
    src = lt.get(aid)
    rate_field = src.get("Rate") if src else None
    rl_row = rl.get(aid)
    rl1_row = rl1.get(aid)
    print(f"  aid={aid} name={name[:40]:40} srcRate={rate_field} ratelist={rl_row and rl_row.get('rate')} ratelist1={rl1_row and (rl1_row.get('rate'), rl1_row.get('newrate'))}")

print()
print("counts in source:")
print("  labtestdetail with Rate>0:", sum(1 for r in load('labtestdetail') if (r.get('Rate') or 0) > 0))
print("  labtestdetail with Rate=0:", sum(1 for r in load('labtestdetail') if (r.get('Rate') or 0) == 0))
print("  ratelist rows:", len(rl))
print("  ratelist1 rows:", len(rl1))
