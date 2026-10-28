"""Bottom-of-page footer stack + abnormal-results note."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer

from .base import _now, _fmt_dt
from .branding import _get_lab

BOTTOM_PANEL_HEIGHT = 80  # footer measured max y=72.7pt + 8pt buffer


def _get_active_signatures(dept_ids=None):
    """Active ReportSignature rows, or [] if unavailable."""
    try:
        from core.models import ReportSignature
        return ReportSignature.for_departments(dept_ids)
    except Exception as e:
        print(f'[pdf.footer] _get_active_signatures failed: {e}')
        return []


def _draw_page_bottom(canvas, doc, dept_ids=None):
    """Referral-style footer — pixel-accurate from measured referral PDF."""
    sigs = _get_active_signatures(dept_ids)
    lab = _get_lab()

    canvas.saveState()

    page_width, page_height = A4

    # --- Column X positions (measured from referral PDF) ---
    # Spread signature columns evenly across the A4 page width
    PAGE_LEFT = 8.7
    PAGE_RIGHT = page_width - 8.7
    n_sigs = len(sigs) if sigs else 0
    if n_sigs > 0:
        gap = (PAGE_RIGHT - PAGE_LEFT) / n_sigs
        COL_X = [PAGE_LEFT + i * gap for i in range(n_sigs)]
    else:
        COL_X = []
    RIGHT_EDGE_X = page_width - 8.7
    DATE_X = RIGHT_EDGE_X - 72  # 1 inch left of right edge for date

    # Column width (for centering sigs within their column)
    COL_W = (PAGE_RIGHT - PAGE_LEFT) / max(n_sigs, 1) if n_sigs > 0 else 0

    # --- Font sizes (measured) ---
    SZ_DISCLAIMER1 = 9.7
    SZ_BAND_TEXT = 7.8
    SZ_SIG_NAME = 7.5
    SZ_SIG_QUALS = 7.1
    SZ_SIG_DESIG = 7.1
    SZ_BOTTOM = 8.9

    # --- Y positions (from page bottom, measured) ---
    Y_DISCLAIMER1 = 72.7
    Y_BAND_TEXT = 59.6
    Y_SIG_NAME = 44.6
    Y_SIG_QUALS = 31.2
    Y_SIG_DESIG = 20.7
    Y_BOTTOM_ROW = 5.9

    # Grey band rectangle (roughly y=55 to y=68, height 13pt)
    band_x0 = 8.0
    band_x1 = page_width - 8.0
    band_y0 = 55.0
    band_y1 = 68.0

    # --- 1. Disclaimer line 1 (above grey band) ---
    canvas.setFont('Helvetica-Bold', SZ_DISCLAIMER1)
    canvas.setFillColor(colors.HexColor('#000000'))
    canvas.drawCentredString(
        page_width / 2, Y_DISCLAIMER1,
        'All results should be interpreted and correlated with clinical history.'
    )

    # --- 2. Grey band with second disclaimer line ---
    canvas.setFillColor(colors.HexColor('#ced4da'))
    canvas.rect(band_x0, band_y0, band_x1 - band_x0, band_y1 - band_y0, fill=1, stroke=0)

    canvas.setFont('Helvetica-Bold', SZ_BAND_TEXT)
    canvas.setFillColor(colors.HexColor('#212529'))
    canvas.drawCentredString(
        page_width / 2, Y_BAND_TEXT,
        'Electronically Verified Report, No Signature(s) required. Not valid for any court of law.'
    )

    # --- 3. Signature grid (4 cols × N rows) ---
    if sigs:
        for i, sig in enumerate(sigs):
            col = i % 4
            row = i // 4
            x = COL_X[col]
            row_offset = row * 35.0  # ~35pt between rows

            # Column center X for this sig
            col_center = x + COL_W / 2

            # Name (centered in column)
            canvas.setFont('Helvetica-Bold', SZ_SIG_NAME)
            canvas.setFillColor(colors.HexColor('#000000'))
            canvas.drawCentredString(col_center, Y_SIG_NAME - row_offset, sig.name or '-')

            # Qualifications (centered)
            if sig.qualifications:
                canvas.setFont('Helvetica', SZ_SIG_QUALS)
                canvas.setFillColor(colors.HexColor('#000000'))
                canvas.drawCentredString(
                    col_center, Y_SIG_QUALS - row_offset,
                    (sig.qualifications or '').replace('\n', ', ')[:80]
                )

            # Designation (centered)
            if sig.designation:
                canvas.setFont('Helvetica', SZ_SIG_DESIG)
                canvas.setFillColor(colors.HexColor('#000000'))
                canvas.drawCentredString(col_center, Y_SIG_DESIG - row_offset, sig.designation)

    # --- 4. Bottom row: Guest | Page N of M | date | time ---
    from datetime import datetime
    now = datetime.now()
    date_str = now.strftime('%m/%d/%Y')
    hour = now.hour % 12 or 12
    ampm = 'AM' if now.hour < 12 else 'PM'
    time_str = f'{hour}:{now.minute:02d}:{now.second:02d}{ampm}'

    try:
        page_num = canvas.getPageNumber()
    except Exception:
        page_num = 1
    total_pages = getattr(canvas, '_total_pages', page_num)

    canvas.setFont('Helvetica', SZ_BOTTOM)
    canvas.setFillColor(colors.HexColor('#000000'))
    canvas.drawString(10.2, Y_BOTTOM_ROW, 'Guest')
    canvas.drawCentredString(page_width / 2 - 15, Y_BOTTOM_ROW, f'Page {page_num} of {total_pages}')
    canvas.drawRightString(DATE_X, Y_BOTTOM_ROW, date_str)
    canvas.drawRightString(RIGHT_EDGE_X, Y_BOTTOM_ROW, time_str)

    canvas.restoreState()

def _footer_flowables(abnormal_count):
    """The abnormal-results note (flows right after the table)."""
    styles = getSampleStyleSheet()
    small = ParagraphStyle(
        'Small', parent=styles['Normal'], fontSize=8,
        textColor=colors.HexColor('#6c757d'),
    )

    elements = []
    elements.append(Spacer(1, 6 * mm))

        # abnormal-note flag removed
    # Normal-range positive flag removed — it was misleading on PCR/qualitative reports.

    return elements
