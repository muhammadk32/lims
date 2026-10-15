"""Import AdamLab testreferencevalue + bkreferencevalue -> TestReferenceRange."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from app import create_app
from extensions import db
from modules.tests import models as M

DATA = os.path.join(HERE, "adamlab_import")
def load(n):
    with open(os.path.join(DATA, n+".json"),"r",encoding="utf-8") as f: return json.load(f)
def i(v):
    try: return int(v)
    except (TypeError, ValueError): return None
def fl(v):
    try: return float(v)
    except (TypeError, ValueError): return None
def s(v):
    if v is None: return None
    v = str(v).strip()
    return v or None
def gender_map(g):
    g = i(g)
    if g == 1: return "male"
    if g == 2: return "female"
    return "any"
def age_unit(u):
    u = (u or "").strip().lower()
    if u.startswith("day"): return "days"
    if u.startswith("week"): return "weeks"
    if u.startswith("month"): return "months"
    if u.startswith("year"): return "years"
    return "years"
def fmt_range(mn, mx, other):
    if other: return str(other)[:120]
    a = "" if mn is None else (f"{mn:g}")
    b = "" if mx is None else (f"{mx:g}")
    if not a and not b: return ""
    return f"{a} - {b}".strip(" -")

def upsert(r, seen):
    testcode = i(r.get("testcode"))
    gcode = i(r.get("gendercode"))
    rcode = i(r.get("referencecode"))
    key = (testcode, rcode, gcode)
    if key in seen: return False
    seen.add(key)

    t = M.Test.query.filter_by(adamlab_id=testcode).first()
    if not t: return False

    # skip if this test already has a matching range from THIS import
    existing = (M.TestReferenceRange.query
                .filter_by(test_id=t.id,
                           gender=gender_map(gcode),
                           range_text=fmt_range(fl(r.get("minivalue")),
                                               fl(r.get("maxvalue")),
                                               s(r.get("othervalue"))))
                .first())
    if existing: return False

    mn = fl(r.get("minivalue"))
    mx = fl(r.get("maxvalue"))
    other = s(r.get("othervalue"))
    range_text = fmt_range(mn, mx, other)

    min_age_v = i(r.get("minageval")); max_age_v = i(r.get("maxageval"))
    min_u = age_unit(r.get("minunit")); max_u = age_unit(r.get("maxunit"))

    age_min_years = age_max_years = age_min_days = age_max_days = None
    if min_u == "days": age_min_days = min_age_v
    else: age_min_years = min_age_v
    if max_u == "days": age_max_days = max_age_v
    else: age_max_years = max_age_v

    lo = fl(r.get("CriticalValueLowerBound")); hi = fl(r.get("CriticalValueUpperBound"))
    crit = None
    if (lo or hi) and (lo != 0 or hi != 0):
        parts = []
        if lo: parts.append(f"<{lo:g}")
        if hi: parts.append(f">{hi:g}")
        crit = " or ".join(parts)

    rr = M.TestReferenceRange(
        test_id=t.id,
        gender=gender_map(gcode),
        age_min_years=age_min_years,
        age_max_years=age_max_years,
        age_min_days=age_min_days,
        age_max_days=age_max_days,
        age_min_value=min_age_v if min_u != "days" else None,
        age_min_unit=min_u if min_u != "days" else None,
        age_max_value=max_age_v if max_u != "days" else None,
        age_max_unit=max_u if max_u != "days" else None,
        range_text=range_text or "—",
        unit=s(r.get("maxunit")) if s(r.get("maxunit")) not in (None,"Days","Years","Months","Weeks") else None,
        critical_value=crit,
        notes=other,
        sort_order=i(r.get("referencecode")) or 0,
        is_active=(s(r.get("status")) or "A").upper() == "A",
    )
    db.session.add(rr)
    return True

def run():
    app = create_app()
    with app.app_context():
        seen = set()
        n1 = n2 = 0
        for r in load("testreferencevalue"):
            if upsert(r, seen): n1 += 1
        for r in load("bkreferencevalue"):
            if upsert(r, seen): n2 += 1
        db.session.commit()
        total = M.TestReferenceRange.query.count()
        print(f"testreferencevalue: {n1} inserted")
        print(f"bkreferencevalue:   {n2} inserted")
        print(f"TestReferenceRange total: {total}")

if __name__ == "__main__":
    run()
