"""Tag package tests with result_format='package'."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests.models import Test
import json

def run():
    app = create_app()
    with app.app_context():
        DATA = os.path.join(HERE, "adamlab_import")
        with open(os.path.join(DATA, "packagetestdetail.json"), "r", encoding="utf-8") as f:
            pkg = json.load(f)
        codes = {r["packagecode"] for r in pkg}

        n = 0
        for t in Test.query.filter(Test.adamlab_id.in_(codes)).all():
            t.result_format = 'package'
            t.is_panel = True
            n += 1
        db.session.commit()
        print(f"tagged {n} tests as packages")

        for t in Test.query.filter_by(result_format='package').all():
            print(f"  {t.code} {t.name}")

if __name__ == "__main__":
    run()
