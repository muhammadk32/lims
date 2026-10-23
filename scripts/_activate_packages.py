"""Activate all package tests."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests.models import Test

def run():
    app = create_app()
    with app.app_context():
        n = 0
        for t in Test.query.filter_by(result_format='package').all():
            if not t.is_active:
                t.is_active = True
                n += 1
        db.session.commit()
        print(f"activated {n} packages")
        for t in Test.query.filter_by(result_format='package').order_by(Test.name).all():
            print(f"  {t.code} {t.name} active={t.is_active}")

if __name__ == "__main__":
    run()
