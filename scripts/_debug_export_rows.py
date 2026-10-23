import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests.models import RateCategoryTest, RateCategoryDeptRate, Test, TestCategory, Specimen

def fmt_time(hours):
    if not hours or hours <= 0: return 'SAME DAY'
    if hours <= 24: return 'SAME DAY'
    if hours < 48: return 'AFTER ONE DAY'
    days = round(hours / 24)
    if days < 7: return f'AFTER {days} DAYS'
    weeks = round(days / 7)
    return f'AFTER {weeks} WEEK' + ('S' if weeks > 1 else '')

app = create_app()
with app.app_context():
    cat_id = 2
    dept_rates = {d.department_id: d for d in RateCategoryDeptRate.query.filter_by(rate_category_id=cat_id).all()}
    q = RateCategoryTest.query.filter_by(rate_category_id=cat_id).order_by(RateCategoryTest.sort_order.asc()).limit(5)
    for rct in q.all():
        t = Test.query.get(rct.test_id)
        if not t: continue
        spec = Specimen.query.get(t.specimen_id) if t.specimen_id else None
        row = {
            'code': t.code, 'name': t.name,
            'specimen': spec.name if spec else (t.sample_type or '—'),
            'reporting_time': fmt_time(t.turnaround_hours),
            'sample_type_raw': t.sample_type,
            'specimen_id': t.specimen_id,
            'turnaround_hours': t.turnaround_hours,
        }
        print(row)
