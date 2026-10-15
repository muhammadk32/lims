import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from app import create_app
from modules.tests import models as M
app = create_app()
with app.app_context():
    t = M.Test.query.filter_by(adamlab_id=41516).first()
    if t:
        print("test:", t.code, t.name)
        print("sub_departments:", [sd.name for sd in t.sub_departments])
    print("total SubDepartmentTest rows:", M.SubDepartmentTest.query.count())
    print("distinct tests with sub_dept:", M.SubDepartmentTest.query.with_entities(M.SubDepartmentTest.test_id).distinct().count())
