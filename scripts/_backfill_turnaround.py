"""Backfill Test.turnaround_hours from labtestdetail.json.TestDays → test_days."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests.models import Test, TestDay

DATA = os.path.join(HERE, "adamlab_import")
def load(n):
    with open(os.path.join(DATA, f"{n}.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def run():
    app = create_app()
    with app.app_context():
        lt = load("labtestdetail")
        # TestDays.ID -> days (from our test_days table)
        day_map = {}
        for td in TestDay.query.all():
            if td.adamlab_id and td.report_date:
                try:
                    d = int(td.report_date)
                    day_map[td.adamlab_id] = max(d, 1)  # at least 1 day
                except (ValueError, TypeError):
                    pass
        print(f"loaded {len(day_map)} day definitions")

        # adamlab testcode -> TestDays.ID
        code_to_days = {}
        for r in lt:
            tc = r.get("testcode")
            td = r.get("TestDays")
            if tc is not None and td is not None:
                code_to_days[int(tc)] = int(td)

        n = 0
        for t in Test.query.filter(Test.adamlab_id.isnot(None)).all():
            days = code_to_days.get(t.adamlab_id)
            if days is None:
                continue
            real_days = day_map.get(days, 1)
            new_hours = real_days * 24
            if t.turnaround_hours != new_hours:
                t.turnaround_hours = new_hours
                n += 1
        db.session.commit()
        print(f"updated {n} tests' turnaround_hours")

        # sample
        print("\nSample:")
        for t in Test.query.filter(Test.adamlab_id.isnot(None)).limit(10).all():
            print(f"  {t.code} {t.name[:40]:40} → {t.turnaround_hours}h")

if __name__ == "__main__":
    run()
