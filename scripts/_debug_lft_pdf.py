"""Manually invoke the PDF for order 456 to get the real traceback."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.orders.models import Order
from modules.reports.pdf.generator import generate_report_pdf

app = create_app()
with app.app_context():
    o = Order.query.get(456)
    print("order:", o.order_code)
    try:
        pdf = generate_report_pdf(o)
        print("PDF generated:", len(pdf) if pdf else 0, "bytes")
    except Exception as e:
        import traceback
        traceback.print_exc()
