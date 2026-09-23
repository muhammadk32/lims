"""Entry point — assembles the PDF from header, patient box, results, footer."""
import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Spacer, HRFlowable

from .header import _header_table
from .patient_box import _patient_info_table
from .results_table import _results_table
from .footer import _draw_page_bottom, _footer_flowables, BOTTOM_PANEL_HEIGHT
from .branding import _get_lab, _hex


def generate_report_pdf(order) -> io.BytesIO:
    """Generate a professional PDF report for an order."""
    lab = _get_lab()
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm + BOTTOM_PANEL_HEIGHT,
        title=f'Lab Report — {order.order_code}',
        author=lab['name'],
    )

    primary = _hex(lab['primary_color'])

    story = []
    story.append(_header_table())
    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width='100%', thickness=1.5, color=primary))
    story.append(Spacer(1, 6 * mm))

    story.append(_patient_info_table(order))
    story.append(Spacer(1, 8 * mm))

    # Build previous-results map for this patient (last 2 prior visits)
    previous_map = {}
    date_labels = []
    try:
        from modules.reports.queries import build_previous_map
        previous_map, date_labels = build_previous_map(order.patient_id, order.id, limit=2)
    except Exception as e:
        print(f'[pdf.generator] previous_map failed: {e}')

    results_table, abnormal_count = _results_table(
        order,
        previous_map=previous_map,
        date_labels=date_labels,
    )
    story.append(results_table)

    story.extend(_footer_flowables(abnormal_count))

    doc.build(
        story,
        onFirstPage=_draw_page_bottom,
        onLaterPages=_draw_page_bottom,
    )
    buffer.seek(0)
    return buffer
