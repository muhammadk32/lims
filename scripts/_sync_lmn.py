import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.laboratories.models import Laboratory
from modules.laboratories.services import sync_lab_rate_list

app = create_app()
with app.app_context():
    lab = Laboratory.query.filter_by(name="LMN").first()
    if not lab:
        print("LMN not found"); sys.exit()
    try:
        cat = sync_lab_rate_list(lab, force=True)
        print(f"Synced → {cat.name if cat else 'FAILED'}")
    except Exception as e:
        import traceback; traceback.print_exc()
