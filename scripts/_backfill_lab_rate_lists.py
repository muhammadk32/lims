"""Backfill rate lists for all labs that don't have one."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.laboratories.models import Laboratory
from modules.laboratories.services import sync_lab_rate_list

def run():
    app = create_app()
    with app.app_context():
        for lab in Laboratory.query.all():
            if not lab.rate_category_id:
                cat = sync_lab_rate_list(lab)
                print(f"  {lab.name}: created '{cat.name if cat else 'FAILED'}'")

if __name__ == "__main__":
    run()
