"""Bottom-of-page footer stack + abnormal-results note."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer

from .base import _now, _fmt_dt
from .branding import _get_lab

BOTTOM_PANEL_HEIGHT = 55 * mm


def _get_active_signatures():
    """Active ReportSignature rows, or [] if unavailable."""
    try:
        from core.models import ReportSignature
        return ReportSignature.active_ordered()
    except Exception as e:
        print(f'[pdf.footer] _get_active_signatures failed: {e}')
        return []


def _draw_page_bottom(canvas, doc):
    """Draw the full bottom footer stack on EVERY page."""
    sigs = _get_active_signatures()
    lab = _get_lab()

    canvas.saveState()

    page_width, page_height = A4
    left_margin = 20 * mm
    right_margin = 20 * mm
    usable_width = page_width - left_margin - right_margin

    COLS = 4
    ROW_HEIGHT = 14 * mm

    if sigs:
        row_count = (len(sigs) + COLS - 1) // COLS
    else:
        row_count = 0

    disclaimer_height = 10 * mm
    separator_block = 5 * mm
    verified_block = 8 * mm
    top_rule_block = 4 * mm

    stack_height = (
        top_rule_block +
        verified_block +
        row_count * ROW_HEIGHT +
        separator_block +
        disclaimer_height
    )

    stack_bottom = 12 * mm
    stack_top = stack_bottom + stack_height

    # 1. Top rule
    canvas.setStrokeColor(colors.HexColor('#adb5bd'))
    canvas.setLineWidth(0.5)
    canvas.line(left_margin, stack_top, page_width - right_margin, stack_top)

    # 2. Verified line
    y = stack_top - 5 * mm
    canvas.setFont('Helvetica-Bold', 8.5)
    canvas.setFillColor(colors.HexColor('#212529'))
    canvas.drawCentredString(
        page_width / 2, y,
        'Electronically verified report. No signature(s) required.'
    )

    # 3. Signature grid
    if sigs:
        col_width = usable_width / COLS
        sig_grid_top = y - 5 * mm

        for i, sig in enumerate(sigs):
            col = i % COLS
            row = i // COLS

            x = left_margin + col * col_width + 3 * mm
            base_y = sig_grid_top - row * ROW_HEIGHT

            canvas.setFont('Helvetica-Bold', 9)
            canvas.setFillColor(colors.HexColor('#212529'))
            canvas.drawString(x, base_y, sig.name or '—')

            current_offset_mm = 4
            if sig.qualifications:
                canvas.setFont('Helvetica', 8)
                canvas.setFillColor(colors.HexColor('#495057'))
                for line in (sig.qualifications or '').split('\n'):
                    canvas.drawString(
                        x, base_y - current_offset_mm * mm, line.strip()
                    )
                    current_offset_mm += 3.2
                current_offset_mm += 0.8

            if sig.designation:
                canvas.setFont('Helvetica', 7.5)
                canvas.setFillColor(colors.HexColor('#6c757d'))
                canvas.drawString(
                    x, base_y - current_offset_mm * mm, sig.designation
                )

    # 4. Separator
    y = (stack_bottom + disclaimer_height) + 2 * mm
    canvas.setStrokeColor(colors.HexColor('#dee2e6'))
    canvas.setLineWidth(0.5)
    canvas.line(left_margin, y, page_width - right_margin, y)

    # 5. Disclaimer
    y -= 4 * mm
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#6c757d'))

    disclaimer_line = (
        'This report is computer-generated and is intended for medical use only. '
        'Results should be interpreted by a qualified healthcare professional. '
        f'Generated on {_fmt_dt(_now())}.'
    )
    max_chars = 110
    if len(disclaimer_line) > max_chars:
        mid = disclaimer_line.rfind(' ', 0, max_chars)
        if mid < 20:
            mid = max_chars
        line1 = disclaimer_line[:mid].strip()
        line2 = disclaimer_line[mid:].strip()
        canvas.drawCentredString(page_width / 2, y, line1)
        canvas.drawCentredString(page_width / 2, y - 3.5 * mm, line2)
        y -= 3.5 * mm
    else:
        canvas.drawCentredString(page_width / 2, y, disclaimer_line)

    # 6. Custom footer note
    if lab.get('footer_note'):
        y -= 4 * mm
        canvas.setFont('Helvetica-Oblique', 8)
        canvas.setFillColor(colors.HexColor('#6c757d'))
        canvas.drawCentredString(page_width / 2, y, lab['footer_note'])

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

    if abnormal_count:
        elements.append(Paragraph(
            f'<font color="#b02a37"><b>Note:</b></font> '
            f'{abnormal_count} result(s) flagged as <b>abnormal</b>. '
            f'Please consult your physician.',
            small,
        ))
    else:
        elements.append(Paragraph(
            '<font color="#198754"><b>✓</b></font> All results are within normal ranges.',
            small,
        ))

    return elements
