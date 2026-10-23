"""Force result_format='package' on all 11 package parent tests."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests.models import Test

CODES = [47765,47766,47767,47768,47769,47770,47771,47772,47775,47776,47783]

def run():
    app = create_app()
    with app.app_context():
        n = 0
        for aid in CODES:
            t = Test.query.filter_by(adamlab_id=aid).first()
            if t:
                t.result_format = 'package'
                t.is_panel = True
                n += 1
        db.session.commit()
        print(f"tagged {n} packages")
        for t in Test.query.filter_by(result_format='package').order_by(Test.name).all():
            print(f"  {t.code} {t.name}")

if __name__ == "__main__":
    run()
