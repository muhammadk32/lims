import json, os
DATA = os.path.join("scripts","adamlab_import")
def load(n):
    with open(os.path.join(DATA, n+".json"),"r",encoding="utf-8") as f: return json.load(f)

trv = load("testreferencevalue")
bkr = load("bkreferencevalue")
print("testreferencevalue rows:", len(trv))
print("bkreferencevalue rows:", len(bkr))

trv_tests = {r["testcode"] for r in trv}
bkr_tests = {r["testcode"] for r in bkr}
print("distinct testcodes in trv:", len(trv_tests))
print("distinct testcodes in bkr:", len(bkr_tests))
print("only in trv:", len(trv_tests - bkr_tests))
print("only in bkr:", len(bkr_tests - trv_tests))
print("overlap:", len(trv_tests & bkr_tests))

# sample
print("--- trv samples ---")
for r in trv[:3]: print(r)

# your model columns
from modules.tests.models import TestReferenceRange as RR
print()
print("TestReferenceRange columns:")
for c in RR.__table__.columns:
    print(" ", c.name, c.type)
