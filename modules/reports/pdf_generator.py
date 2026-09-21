"""
Professional lab report PDF generator using ReportLab.
Produces A4 PDF with:
  - Lab header (logo + name + address + contact) — DB-driven
  - Patient info box
  - Results table with abnormal highlighting (panels grouped)
  - Full footer stack pinned to the BOTTOM of every page:
        top rule
        "Electronically verified report..."
        signature panel (4-column grid)
        separator
        disclaimer text
        custom footer note

Timezone: Asia/Karachi (Pakistan)
"""
import io
import os
from datetime import datetime
from zoneinfo import ZoneInfo


from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image,
)


# ============================================================
# Timezone helper — Pakistan
# ============================================================
TIMEZONE_NAME = 'Asia/Karachi'


def _now():
    """Current time in the lab timezone."""
    try:
        from flask import current_app
        tz_name = current_app.config.get('TIMEZONE', TIMEZONE_NAME)
    except Exception:
        tz_name = TIMEZONE_NAME

    try:
        return datetime.now(ZoneInfo(tz_name))
    except Exception:
        return datetime.now()


def _fmt_dt(dt, fmt='%Y-%m-%d %H:%M'):
    """Format a datetime in local timezone."""
    if not dt:
        return '—'
    try:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo('UTC'))
        return dt.astimezone(ZoneInfo(TIMEZONE_NAME)).strftime(fmt)
    except Exception:
        try:
            return dt.strftime(fmt)
        except Exception:
            return '—'


def _fmt_dt_pretty(dt):
    """Format a datetime in the lab timezone — pretty format used on the report.

    Example: 19-Sep-2026 01:11 PM
    """
    if not dt:
        return None
    try:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo('UTC'))
        return dt.astimezone(ZoneInfo(TIMEZONE_NAME)).strftime('%d-%b-%Y %I:%M %p')
    except Exception:
        try:
            return dt.strftime('%d-%b-%Y %I:%M %p')
        except Exception:
            return None


# ============================================================
# Lab identity — DB-driven with safe fallbacks
# ============================================================
_DEFAULT_LAB = {
    'name': 'Laboratory Management System',
    'tagline': '',
    'address': '',
    'phone': '',
    'email': '',
    'website': '',
    'license_no': '',
    'logo_filename': None,
    'logo_path': None,
    'primary_color': '#0d6efd',
    'footer_note': '',
}


def _logo_abs_path(filename):
    """Absolute filesystem path to the logo, or None."""
    if not filename:
        return None
    try:
        from flask import current_app
        path = os.path.join(
            current_app.root_path, 'static', 'uploads', 'branding', filename
        )
        return path if os.path.exists(path) else None
    except Exception:
        return None


def _lab_dict_from_settings(s):
    """Build the lab dict from a LabSettings row."""
    return {
        'name': s.lab_name or _DEFAULT_LAB['name'],
        'tagline': s.tagline or '',
        'address': s.address or '',
        'phone': s.phone or '',
        'email': s.email or '',
        'website': s.website or '',
        'license_no': s.license_no or '',
        'logo_filename': s.logo_filename,
        'logo_path': _logo_abs_path(s.logo_filename),
        'primary_color': s.primary_color or '#0d6efd',
        'footer_note': s.footer_note or '',
    }


def _get_lab():
    """Return current lab branding from DB (or defaults on failure)."""
    try:
        from flask import has_app_context
        from core.models import LabSettings
        from extensions import db

        if has_app_context():
            s = LabSettings.get()
            if s:
                return _lab_dict_from_settings(s)

        try:
            from app import app as _app
            with _app.app_context():
                s = LabSettings.get()
                if s:
                    return _lab_dict_from_settings(s)
        except Exception:
            pass

    except Exception as e:
        print(f'[pdf_generator] _get_lab failed: {e}')

    return dict(_DEFAULT_LAB)


def _hex(color_str, fallback='#0d6efd'):
    """Safely convert hex string to reportlab color."""
    try:
        return colors.HexColor(color_str or fallback)
    except Exception:
        return colors.HexColor(fallback)


# ---------- Backwards-compat constants ----------
_initial = _get_lab()
LAB_NAME = _initial['name']
LAB_TAGLINE = _initial['tagline']
LAB_ADDRESS = _initial['address']
LAB_PHONE = _initial['phone']
LAB_EMAIL = _initial['email']
LAB_WEBSITE = _initial['website']


# ============================================================
# Helpers
# ============================================================
def _flag_result(normal_range, result_value):
    """Return 'normal' | 'abnormal' | 'unknown'."""
    try:
        from modules.results.validators import check_result
        return check_result(normal_range, result_value)
    except Exception:
        return 'unknown'


def _logo_flowable(lab, max_height_mm=22, max_width_mm=60):
    """Return an Image flowable for the logo, or None."""
    if not lab.get('logo_path'):
        return None
    try:
        img = Image(lab['logo_path'])
        iw, ih = img.imageWidth, img.imageHeight
        if not iw or not ih:
            return None
        max_h = max_height_mm * mm
        max_w = max_width_mm * mm
        scale = min(max_w / iw, max_h / ih, 1.0)
        img.drawWidth = iw * scale
        img.drawHeight = ih * scale
        img.hAlign = 'CENTER'
        return img
    except Exception:
        return None


def _get_active_signatures():
    """Active ReportSignature rows, or [] if unavailable."""
    try:
        from core.models import ReportSignature
        return ReportSignature.active_ordered()
    except Exception as e:
        print(f'[pdf_generator] _get_active_signatures failed: {e}')
        return []


# ============================================================
# Header
# ============================================================
def _header_table():
    """Return a table with lab info at top, DB-driven."""
    lab = _get_lab()
    styles = getSampleStyleSheet()
    primary = _hex(lab['primary_color'])

    name_style = ParagraphStyle(
        'LabName', parent=styles['Heading1'],
        fontSize=18, textColor=primary, alignment=1, spaceAfter=2,
    )
    tag_style = ParagraphStyle(
        'Tagline', parent=styles['Normal'],
        fontSize=9, textColor=colors.HexColor('#6c757d'),
        alignment=1, spaceAfter=4,
    )
    contact_style = ParagraphStyle(
        'Contact', parent=styles['Normal'],
        fontSize=8, alignment=1, textColor=colors.HexColor('#495057'),
    )
    license_style = ParagraphStyle(
        'License', parent=styles['Normal'],
        fontSize=7.5, alignment=1, textColor=colors.HexColor('#6c757d'),
    )

    contact_parts = [p for p in [
        lab['address'], lab['phone'], lab['email'], lab['website']
    ] if p]
    contact_line = ' · '.join(contact_parts) if contact_parts else ''

    rows = []

    logo = _logo_flowable(lab, max_height_mm=22, max_width_mm=60)
    if logo is not None:
        rows.append([logo])
        rows.append([Spacer(1, 3 * mm)])

    rows.append([Paragraph(lab['name'], name_style)])

    if lab['tagline']:
        rows.append([Paragraph(lab['tagline'], tag_style)])

    if contact_line:
        rows.append([Paragraph(contact_line, contact_style)])

    if lab['license_no']:
        rows.append([Paragraph(f"License #: {lab['license_no']}", license_style)])

    t = Table(rows, colWidths=[170 * mm])
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    return t


# ============================================================
# Patient / Order info box
# ============================================================
def _patient_info_table(order):
    """Two-column info box with patient details.

    Order Information column now shows:
      - Order Code
      - Registered On   (order.created_at)
      - Reporting Date  (order.reported_at, or "Pending Approval")
      - Doctor
      - Status
    """
    lab = _get_lab()
    primary = _hex(lab['primary_color'])
    header_bg = colors.HexColor('#e7f1ff')

    styles = getSampleStyleSheet()
    label_style = ParagraphStyle(
        'Lbl', parent=styles['Normal'], fontSize=8,
        textColor=colors.HexColor('#6c757d'),
    )
    value_style = ParagraphStyle(
        'Val', parent=styles['Normal'], fontSize=10, textColor=colors.black,
    )
    pending_style = ParagraphStyle(
        'Pending', parent=styles['Normal'], fontSize=10,
        textColor=colors.HexColor('#adb5bd'), fontName='Helvetica-Oblique',
    )

    def cell(label, value):
        return [
            Paragraph(label.upper(), label_style),
            Paragraph(str(value if value is not None else '—'), value_style),
        ]

    def cell_pending(label, value, is_pending=False):
        """Cell variant that renders 'Pending Approval' in muted italic."""
        return [
            Paragraph(label.upper(), label_style),
            Paragraph(str(value), pending_style if is_pending else value_style),
        ]

    left = [
        [Paragraph('<b>Patient Information</b>', styles['Heading4']), ''],
        cell('Name', order.patient.full_name),
        cell('Patient Code', order.patient.patient_code),
        cell('Gender', order.patient.gender),
        cell('Age', order.patient.compute_age()),
        cell('Phone', order.patient.phone),
    ]

    # ---- Reporting date ----
    registered_pretty = _fmt_dt_pretty(order.created_at) or '—'
    if order.reported_at:
        reporting_value = _fmt_dt_pretty(order.reported_at) or '—'
        reporting_pending = False
    else:
        reporting_value = 'Pending Approval'
        reporting_pending = True

    # ---- Status label ----
    from modules.orders.models import OrderStatus
    status_label = OrderStatus.LABELS.get(order.status, order.status.capitalize())

    right = [
        [Paragraph('<b>Order Information</b>', styles['Heading4']), ''],
        cell('Order Code', order.order_code),
        cell('Registered On', registered_pretty),
        cell_pending('Reporting Date', reporting_value, reporting_pending),
        cell('Doctor', order.doctor.full_name if order.doctor else '—'),
        cell('Status', status_label),
    ]

    rows = []
    for i in range(len(left)):
        l = left[i]
        r = right[i]
        if i == 0:
            rows.append([l[0], '', r[0], ''])
        else:
            rows.append([l[0], l[1], r[0], r[1]])

    col_widths = [25 * mm, 60 * mm, 25 * mm, 60 * mm]
    t = Table(rows, colWidths=col_widths)

    style = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (2, 0), (3, 0)),
        ('BACKGROUND', (0, 0), (1, 0), header_bg),
        ('BACKGROUND', (2, 0), (3, 0), header_bg),
        ('BOX', (0, 0), (1, -1), 0.5, colors.HexColor('#ced4da')),
        ('BOX', (2, 0), (3, -1), 0.5, colors.HexColor('#ced4da')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#e9ecef')),
    ]
    t.setStyle(TableStyle(style))
    return t


# ============================================================
# Results table — grouped by panel
# ============================================================
def _results_table(order):
    """Results table with panel grouping."""
    lab = _get_lab()
    primary = _hex(lab['primary_color'])

    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        'Hdr', parent=styles['Normal'], fontSize=9,
        textColor=colors.white, fontName='Helvetica-Bold',
    )
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=9)
    cell_bold = ParagraphStyle(
        'CellBold', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold',
    )
    panel_header_style = ParagraphStyle(
        'PanelHdr', parent=styles['Normal'], fontSize=9.5,
        fontName='Helvetica-Bold', textColor=colors.HexColor('#1e40af'),
    )
    panel_sub_style = ParagraphStyle(
        'PanelSub', parent=styles['Normal'], fontSize=9,
        textColor=colors.HexColor('#212529'), leftIndent=10,
    )

    header_row = [
        Paragraph('Test', header_style),
        Paragraph('Result', header_style),
        Paragraph('Unit', header_style),
        Paragraph('Normal Range', header_style),
        Paragraph('Flag', header_style),
    ]
    data = [header_row]

    abnormal_rows = []
    row_idx = 1

    for item in order.top_level_items:
        if item.has_children:
            data.append([
                Paragraph(f'▸ {item.test.name}', panel_header_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
            ])
            row_idx += 1

            for child in item.children:
                flag = _flag_result(child.test.normal_range, child.result_value)
                flag_text = {
                    'normal': 'Normal',
                    'abnormal': 'Abnormal',
                    'unknown': '—',
                }.get(flag, '—')
                if flag == 'abnormal':
                    abnormal_rows.append(row_idx)

                data.append([
                    Paragraph(child.test.name, panel_sub_style),
                    Paragraph(child.result_value or '—', cell_style),
                    Paragraph(child.test.unit or '—', cell_style),
                    Paragraph(child.test.normal_range or '—', cell_style),
                    Paragraph(flag_text, cell_style),
                ])
                row_idx += 1
        else:
            flag = _flag_result(item.test.normal_range, item.result_value)
            flag_text = {
                'normal': 'Normal',
                'abnormal': 'Abnormal',
                'unknown': '—',
            }.get(flag, '—')
            if flag == 'abnormal':
                abnormal_rows.append(row_idx)

            data.append([
                Paragraph(item.test.name, cell_bold),
                Paragraph(item.result_value or '—', cell_style),
                Paragraph(item.test.unit or '—', cell_style),
                Paragraph(item.test.normal_range or '—', cell_style),
                Paragraph(flag_text, cell_style),
            ])
            row_idx += 1

    col_widths = [65 * mm, 30 * mm, 25 * mm, 35 * mm, 25 * mm]
    t = Table(data, colWidths=col_widths, repeatRows=1)

    style = [
        ('BACKGROUND', (0, 0), (-1, 0), primary),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#adb5bd')),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]

    for i, row in enumerate(data):
        if i == 0:
            continue
        cell0 = row[0]
        if hasattr(cell0, 'text') and cell0.text.startswith('▸'):
            style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#dbeafe')))

    for row_idx_ab in abnormal_rows:
        style.append(('BACKGROUND', (0, row_idx_ab), (-1, row_idx_ab), colors.HexColor('#f8d7da')))
        style.append(('TEXTCOLOR', (1, row_idx_ab), (1, row_idx_ab), colors.HexColor('#b02a37')))

    t.setStyle(TableStyle(style))
    return t, len(abnormal_rows)


# ============================================================
# Bottom-of-page drawing — full footer stack
# ============================================================
BOTTOM_PANEL_HEIGHT = 55 * mm


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


# ============================================================
# Abnormal note
# ============================================================
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


# ============================================================
# Main entry point
# ============================================================
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

    results_table, abnormal_count = _results_table(order)
    story.append(results_table)

    story.extend(_footer_flowables(abnormal_count))

    doc.build(
        story,
        onFirstPage=_draw_page_bottom,
        onLaterPages=_draw_page_bottom,
    )
    buffer.seek(0)
    return buffer