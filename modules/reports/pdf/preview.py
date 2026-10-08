"""Sample report PDF for the admin preview — uses real header/branding."""
import io

from reportlab.lib.pagesizes import A4, LETTER, LEGAL
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors


def _page_dims(name):
    return {
        'A4': A4,
        'Letter': LETTER,
        'Legal': LEGAL,
        'A5': (A4[0] / 2, A4[1] / 2),
    }.get(name, A4)


def build_preview_pdf():
    from core.models import LabSettings
    s = LabSettings.get()
    buf = io.BytesIO()

    page_w, page_h = _page_dims(getattr(s, 'report_page_size', 'A4') or 'A4')
    if (getattr(s, 'report_orientation', 'portrait') or 'portrait').lower() == 'landscape':
        page_w, page_h = page_h, page_w

    left   = (getattr(s, 'report_margin_left', 0.8) or 0.8) * inch
    right  = (getattr(s, 'report_margin_right', 0.8) or 0.8) * inch
    top    = (getattr(s, 'report_margin_top', 0.6) or 0.6) * inch
    bottom = (getattr(s, 'report_margin_bottom', 0.6) or 0.6) * inch
    font   = getattr(s, 'report_font_family', 'Helvetica') or 'Helvetica'
    size   = int(getattr(s, 'report_base_font_size', 8) or 8)

    doc = SimpleDocTemplate(
        buf, pagesize=(page_w, page_h),
        leftMargin=left, rightMargin=right,
        topMargin=top, bottomMargin=bottom,
        title='Report Preview',
    )

    title_style = ParagraphStyle('PreviewTitle', fontName=font, fontSize=size + 6,
                                 leading=size + 8, alignment=1)
    body = ParagraphStyle('PreviewBody', fontName=font, fontSize=size,
                          leading=size + 3)
    lbl = ParagraphStyle('PreviewLbl', fontName=font, fontSize=size - 1,
                         leading=size + 1, textColor=colors.HexColor('#6c757d'))

    story = []

    # ---- Real header from branding ----
    try:
        from modules.reports.pdf.header import _header_table
        story.append(_header_table())
        story.append(Spacer(1, 2))
        if getattr(s, 'header_show_divider', True):
            story.append(HRFlowable(width='100%', thickness=1.5,
                                    color=colors.HexColor(getattr(s, 'primary_color', '#0d6efd') or '#0d6efd')))
        story.append(Spacer(1, 4))
    except Exception as e:
        story.append(Paragraph(f'(header unavailable: {e})', lbl))

    # ---- Sample patient box (visual only) ----
    # ---- Sample 4-column patient box + QR (visual only) ----
    lbl_s = ParagraphStyle('PvLbl', fontName=font, fontSize=size - 1.5,
                           leading=size + 0.5,
                           textColor=colors.HexColor('#495057'))
    val_s = ParagraphStyle('PvVal', fontName=font, fontSize=size + 0.5,
                           leading=size + 2)
    def _blk(l, v):
        return [Paragraph(l, lbl_s), Paragraph(v, val_s)]

    from reportlab.platypus import Table, TableStyle, Image
    sample_rows = [
        [_blk('Patient Name:', 'SAMPLE PATIENT')[0], _blk('Registered At:', 'CURE CLINICAL LAB')[0],
         _blk('Reference:', 'Walk-in')[0],            _blk('Patient No:', 'P99999')[0]],
        [_blk('Patient Name:', 'SAMPLE PATIENT')[1], _blk('Registered At:', 'CURE CLINICAL LAB')[1],
         _blk('Reference:', 'Walk-in')[1],            _blk('Patient No:', 'P99999')[1]],
        [_blk('Age/Gender:', '35 / Male')[0],         _blk('Registered On:', '08-Oct-2026 12:00 PM')[0],
         _blk('Consultant:', 'DR SAMPLE')[0],         _blk('Case No:', '1026-999')[0]],
        [_blk('Age/Gender:', '35 / Male')[1],         _blk('Registered On:', '08-Oct-2026 12:00 PM')[1],
         _blk('Consultant:', 'DR SAMPLE')[1],         _blk('Case No:', '1026-999')[1]],
    ]

    # QR (only if enabled)
    show_qr = bool(getattr(s, 'report_show_qr', True))
    qr_cell = ''
    if show_qr:
        try:
            from .qr import qr_png_bytes
            qbuf = qr_png_bytes('1026-999')
            if qbuf:
                img = Image(qbuf, width=22 * mm, height=22 * mm)
                img.hAlign = 'CENTER'
                qr_cell = img
        except Exception:
            pass

    for i, r in enumerate(sample_rows):
        r.append(qr_cell if i == 0 else '')

    col_widths = [42*mm, 42*mm, 42*mm, 30*mm]
    if show_qr:
        col_widths.append(26*mm)

    tbl = Table(sample_rows, colWidths=col_widths)
    tbl_style = [
        ('BOX', (0,0), (-1,-1), 0.4, colors.HexColor('#adb5bd')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ]
    if show_qr:
        tbl_style += [
            ('SPAN', (4, 0), (4, 3)),
            ('VALIGN', (4, 0), (4, 3), 'MIDDLE'),
            ('ALIGN', (4, 0), (4, 3), 'CENTER'),
        ]
    tbl.setStyle(TableStyle(tbl_style))
    story.append(tbl)
    story.append(Spacer(1, 10))

    # ---- Layout info ----
    story.append(Paragraph('REPORT PREVIEW', title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f'Page: {page_w/inch:.2f} x {page_h/inch:.2f} inches', lbl))
    story.append(Paragraph(f'Margins: T {top/inch:.2f}"  B {bottom/inch:.2f}"  L {left/inch:.2f}"  R {right/inch:.2f}"', lbl))
    story.append(Paragraph(f'Font: {font} @ {size}pt', lbl))
    story.append(Spacer(1, 10))

    # ---- Sample body ----
    story.append(Paragraph('<b>Sample Body Text</b>', body))
    story.append(Spacer(1, 4))
    story.append(Paragraph('The quick brown fox jumps over the lazy dog. ' * 4, body))
    story.append(Spacer(1, 10))
    story.append(Paragraph('<b>Sample Test Result Table</b>', body))
    story.append(Spacer(1, 4))
    story.append(Paragraph('Hemoglobin: 13.5 g/dL &nbsp;|&nbsp; WBC: 7.2 x10^9/L', body))
    story.append(Paragraph('Platelets: 250 x10^9/L &nbsp;|&nbsp; RBC: 4.8 x10^12/L', body))

    # ---- Footer note ----
    if getattr(s, 'footer_note', None):
        story.append(Spacer(1, 14))
        story.append(HRFlowable(width='100%', thickness=0.4,
                                color=colors.HexColor('#adb5bd')))
        story.append(Spacer(1, 4))
        story.append(Paragraph(s.footer_note, lbl))

    doc.build(story)
    buf.seek(0)
    return buf
