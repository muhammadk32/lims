"""Entry point — assembles the PDF from header, patient box, results, footer."""
import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, NextPageTemplate, Spacer, HRFlowable

from .header import _header_table
from .patient_box import _patient_info_table
from .results_table import _results_table
from .footer import _draw_page_bottom, _footer_flowables, BOTTOM_PANEL_HEIGHT
from .branding import _get_lab, _hex


def generate_report_pdf(order, item_id=None) -> io.BytesIO:
    """Generate a professional PDF report for an order."""
    lab = _get_lab()
    buffer = io.BytesIO()

    LM = 20 * mm
    RM = 20 * mm
    TOP_PAGE1 = 8 * mm
    TOP_LATER = 20 * mm   # room for strip + single-row patient line
    BOT = 15 * mm + BOTTOM_PANEL_HEIGHT
    content_w = A4[0] - LM - RM

    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=LM,
        rightMargin=RM,
        topMargin=TOP_PAGE1,
        bottomMargin=BOT,
        title=f'Lab Report — {order.order_code}',
        author=lab['name'],
    )

    frame_first = Frame(LM, BOT, content_w, A4[1] - TOP_PAGE1 - BOT, id='first')
    frame_later = Frame(LM, BOT, content_w, A4[1] - TOP_LATER - BOT, id='later')

    primary = _hex(lab['primary_color'])

    story = []


    # Check global header toggle
    try:
        from core.models import LabSettings
        _lab_s = LabSettings.get()
        _hdr_on = bool(getattr(_lab_s, 'header_enabled', True)) if _lab_s else True
    except Exception:
        _lab_s = None
        _hdr_on = True

    # Adjust top margin when header is off
    if not _hdr_on and _lab_s is not None:
        _top_mm = int(getattr(_lab_s, 'header_top_margin_mm', 15) or 15)
        doc.topMargin = _top_mm * mm

    if _hdr_on:
        story.append(_header_table())
        story.append(Spacer(1, 1 * mm))
        if getattr(_lab_s, 'header_show_divider', True) if _lab_s else True:
            story.append(HRFlowable(width='100%', thickness=1.5, color=primary))
        story.append(Spacer(1, 1 * mm))

    from reportlab.platypus import KeepTogether
    story.append(KeepTogether([_patient_info_table(order)]))
    story.append(NextPageTemplate('Later'))    # page 2+ uses 'Later' template
    story.append(Spacer(1, 1 * mm))

    # Build previous-results map for this patient (last 2 prior visits)
    previous_map = {}
    date_labels = []
    try:
        from modules.reports.queries import build_previous_map
        previous_map, date_labels = build_previous_map(order.patient_id, order.id, limit=2)
    except Exception as e:
        print(f'[pdf.generator] previous_map failed: {e}')

    # ---- Item filter: single test print (?item=<id>) ----
    if item_id is not None:
        target = [t for t in order.top_level_items if t.id == item_id]
        items_for_pdf = target or order.top_level_items
        pending = []
    else:
        # ---- PARTIAL REPORT: only verified top-level items are printed ----
        all_top    = order.top_level_items
        verified   = [t for t in all_top if t.is_verified]
        pending    = [t for t in all_top if not t.is_verified]
        items_for_pdf = verified if verified else all_top

    results_table, _notes_flow, abnormal_count, critical_count = _results_table(
        order,
        previous_map=previous_map,
        date_labels=date_labels,
        items_override=items_for_pdf,
    )
    story.append(results_table)
    for _p in _notes_flow:
        story.append(_p)

    story.extend(_footer_flowables(abnormal_count))

    from .header import draw_continuation_header

    def _on_later(canvas, doc):
        draw_continuation_header(canvas, doc, order)
        _draw_page_bottom(canvas, doc)

    doc.addPageTemplates([
        PageTemplate(id='First', frames=[frame_first],
                     onPage=lambda c, d: _draw_page_bottom(c, d)),
        PageTemplate(id='Later', frames=[frame_later],
                     onPage=_on_later),
    ])

    doc.build(story)
    buffer.seek(0)
    return buffer
