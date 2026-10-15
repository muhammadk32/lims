import json, os
from collections import defaultdict, Counter
DATA = os.path.join("scripts","adamlab_import")
def load(n):
    with open(os.path.join(DATA, n+".json"),"r",encoding="utf-8") as f: return json.load(f)

tg = load("testgroupdetail")
print("total testgroupdetail rows:", len(tg))
for r in tg[:10]: print(r)

groups = {r["groupcode"] for r in tg}
print("distinct groupcodes:", len(groups))

lt = load("labtestdetail")
testcodes = {r["testcode"] for r in lt}
matched = groups & testcodes
print("groupcodes also testcodes:", len(matched), "/", len(groups))

pkg = Counter(r["package"] for r in lt if r["testcode"] in groups)
print("package flag of panel parents:", pkg)

by_group = defaultdict(list)
for r in tg: by_group[r["groupcode"]].append(r["testcode"])
sizes = [len(v) for v in by_group.values()]
print("children per group: min", min(sizes), "max", max(sizes), "avg", round(sum(sizes)/len(sizes),2))
