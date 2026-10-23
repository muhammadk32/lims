"""Reproduce 25 Hydroxy Vitamin D3 failure with full traceback."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from modules.orders.models import Order
from modules.reports.pdf.generator import generate_report_pdf

app = create_app()
with app.app_context():
    o = Order.query.get(456)
    # Get the D3 item
    d3 = [it for it in o.top_level_items if 'Hydroxy' in (it.test.name or '')]
    if d3:
        item = d3[0]
        print("D3 test:", item.test.name)
        try:
            pdf = generate_report_pdf(o, item_id=item.id)
            print("PDF OK:", len(pdf), "bytes")
        except Exception:
            import traceback
            traceback.print_exc()
