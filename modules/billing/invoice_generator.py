"""
Professional invoice PDF generator.
Includes: line items, subtotal, discount, total, payments, balance.
Branding (name, logo, contact, color) is DB-driven via LabSettings.
Timezone: Asia/Karachi (Pakistan)

IMPORTANT: Panel children (which have price=0 and parent_item_id set)
are NOT shown on invoices. Only top-level items are billed.
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
# Timezone helper
# ============================================================
TIMEZONE_NAME = 'Asia/Karachi'


def _now():
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


# ============================================================
# Lab identity
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
    'currency_symbol': 'Rs',
}


def _logo_abs_path(filename):
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
        'currency_symbol': getattr(s, 'currency_symbol', None) or 'Rs',
    }


def _get_lab():
    try:
        from flask import has_app_context
        from core.models import LabSettings

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
        print(f'[invoice_generator] _get_lab failed: {e}')

    return dict(_DEFAULT_LAB)


def _hex(color_str, fallback='#0d6efd'):
    try:
        return colors.HexColor(color_str or fallback)
    except Exception:
        return colors.HexColor(fallback)


# ---------- Backwards-compat constants ----------
_initial = _get_lab()
LAB_NAME = _initial['name']
LAB_ADDRESS = _initial['address']
LAB_PHONE = _initial['phone']
LAB_EMAIL = _initial['email']
LAB_WEBSITE = _initial['website']
LAB_TAX_ID = _initial['license_no']

DEFAULT_TAX_RATE = 0.0


# ============================================================
# Logo
# ============================================================
def _logo_flowable(lab, max_height_mm=18, max_width_mm=45):
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
        img.hAlign = 'LEFT'
        return img
    except Exception:
        return None


# ============================================================
# Header
# ============================================================
def _header():
    lab = _get_lab()
    primary = _hex(lab['primary_color'])

    styles = getSampleStyleSheet()
    name_style = ParagraphStyle(
        'LabName', parent=styles['Heading1'],
        fontSize=18, textColor=primary, alignment=0, spaceAfter=2,
    )
    contact = ParagraphStyle(
        'Contact', parent=styles['Normal'], fontSize=8,
        textColor=colors.HexColor('#495057'),
    )

    left_items = []

    logo = _logo_flowable(lab, max_height_mm=18, max_width_mm=45)
    if logo is not None:
        left_items.append(logo)
        left_items.append(Spacer(1, 2 * mm))

    left_items.append(Paragraph(lab['name'], name_style))

    if lab['tagline']:
        left_items.append(Paragraph(
            f'<i>{lab["tagline"]}</i>',
            ParagraphStyle('Tagline', parent=contact, fontSize=8,
                           textColor=colors.HexColor('#6c757d')),
        ))

    if lab['address']:
        left_items.append(Paragraph(lab['address'], contact))

    contact_parts = []
    if lab['phone']:
        contact_parts.append(f'Phone: {lab["phone"]}')
    if lab['email']:
        contact_parts.append(f'Email: {lab["email"]}')
    if contact_parts:
        left_items.append(Paragraph(' · '.join(contact_parts), contact))

    web_tax_parts = []
    if lab['website']:
        web_tax_parts.append(lab['website'])
    if lab['license_no']:
        web_tax_parts.append(f'Tax ID: {lab["license_no"]}')
    if web_tax_parts:
        left_items.append(Paragraph(' · '.join(web_tax_parts), contact))

    invoice_title = ParagraphStyle(
        'InvTitle', parent=styles['Heading1'],
        fontSize=22, textColor=primary, alignment=2,
    )
    right_items = [Paragraph('INVOICE', invoice_title)]

    data = [[left_items, right_items]]
    t = Table(data, colWidths=[110 * mm, 60 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    return t


# ============================================================
# Info block
# ============================================================
def _info_block(order):
    styles = getSampleStyleSheet()
    lbl = ParagraphStyle('Lbl', parent=styles['Normal'], fontSize=8,
                         textColor=colors.HexColor('#6c757d'))
    val = ParagraphStyle('Val', parent=styles['Normal'], fontSize=10)

    def pair(label, value):
        return [Paragraph(label.upper(), lbl),
                Paragraph(str(value if value is not None else '—'), val)]

    billed_to = [
        [Paragraph('<b>BILLED TO</b>', styles['Normal'])],
        pair('Name', order.patient.full_name),
        pair('Code', order.patient.patient_code),
        pair('Phone', order.patient.phone),
    ]
    details = [
        [Paragraph('<b>INVOICE DETAILS</b>', styles['Normal'])],
        pair('Invoice #', f'INV-{order.order_code}'),
        pair('Order #', order.order_code),
        pair('Date', _fmt_dt(order.created_at, '%Y-%m-%d')),
    ]

    rows4 = []
    for i in range(1, max(len(billed_to), len(details))):
        l = billed_to[i] if i < len(billed_to) else ['', '']
        r = details[i] if i < len(details) else ['', '']
        rows4.append([l[0], l[1], r[0], r[1]])

    header_row = [[billed_to[0][0], '', details[0][0], '']]
    data = header_row + rows4

    t = Table(data, colWidths=[22 * mm, 60 * mm, 25 * mm, 63 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (2, 0), (3, 0)),
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#f8d7da')),
        ('BACKGROUND', (2, 0), (3, 0), colors.HexColor('#cfe2ff')),
        ('BOX', (0, 0), (1, -1), 0.5, colors.HexColor('#ced4da')),
        ('BOX', (2, 0), (3, -1), 0.5, colors.HexColor('#ced4da')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#e9ecef')),
    ]))
    return t


# ============================================================
# Line items — ONLY top-level (billable) items
# ============================================================
def _line_items_table(order):
    """
    Line items table.
    IMPORTANT: Only shows top_level_items (parent items with price).
    Panel children (price=0) are NOT shown.
    """
    lab = _get_lab()
    primary = _hex(lab['primary_color'])
    cur = lab.get('currency_symbol', 'Rs')

    styles = getSampleStyleSheet()
    header = ParagraphStyle('H', parent=styles['Normal'], fontSize=9,
                            textColor=colors.white, fontName='Helvetica-Bold')
    cell = ParagraphStyle('C', parent=styles['Normal'], fontSize=9)
    cell_r = ParagraphStyle('CR', parent=styles['Normal'], fontSize=9, alignment=2)

    data = [[
        Paragraph('#', header),
        Paragraph('Test', header),
        Paragraph('Code', header),
        Paragraph('Unit Price', header),
        Paragraph('Qty', header),
        Paragraph('Amount', header),
    ]]

    # Only billable = top-level items
    billable_items = order.top_level_items

    for i, item in enumerate(billable_items, start=1):
        # Show panel indicator for panels
        display_name = item.test.name
        if item.has_children:
            display_name = f'{display_name}  (Panel)'

        data.append([
            Paragraph(str(i), cell),
            Paragraph(display_name, cell),
            Paragraph(item.test.code, cell),
            Paragraph(f'{cur} {item.price:.2f}', cell_r),
            Paragraph('1', cell_r),
            Paragraph(f'{cur} {item.price:.2f}', cell_r),
        ])

    widths = [10 * mm, 70 * mm, 22 * mm, 25 * mm, 15 * mm, 28 * mm]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#adb5bd')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('ALIGN', (3, 1), (5, -1), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return t


# ============================================================
# Totals
# ============================================================
def _totals_table(order, tax_rate=DEFAULT_TAX_RATE):
    lab = _get_lab()
    cur = lab.get('currency_symbol', 'Rs')

    styles = getSampleStyleSheet()
    lbl = ParagraphStyle('L', parent=styles['Normal'], fontSize=10)
    val = ParagraphStyle('V', parent=styles['Normal'], fontSize=10, alignment=2)
    grand_l = ParagraphStyle('GL', parent=styles['Normal'], fontSize=12,
                             fontName='Helvetica-Bold')
    grand_v = ParagraphStyle('GV', parent=styles['Normal'], fontSize=12,
                             fontName='Helvetica-Bold', alignment=2,
                             textColor=colors.HexColor('#198754'))
    disc_style = ParagraphStyle('Dsc', parent=styles['Normal'], fontSize=10,
                                alignment=2, textColor=colors.HexColor('#dc3545'))
    pay = ParagraphStyle('P', parent=styles['Normal'], fontSize=10, alignment=2,
                         textColor=colors.HexColor('#0d6efd'))
    due = ParagraphStyle('D', parent=styles['Normal'], fontSize=12,
                         fontName='Helvetica-Bold', alignment=2,
                         textColor=colors.HexColor('#dc3545'))

    subtotal = order.subtotal or 0.0
    discount = order.discount_value or 0.0
    total = order.final_total or 0.0
    paid = order.paid_amount
    balance = max(0.0, total - paid)

    rows = [
        [Paragraph('Subtotal', lbl), Paragraph(f'{cur} {subtotal:.2f}', val)],
    ]
    if discount > 0:
        rows.append([
            Paragraph('Discount', lbl),
            Paragraph(f'−{cur} {discount:.2f}', disc_style),
        ])
    rows += [
        [Paragraph('Total', grand_l), Paragraph(f'{cur} {total:.2f}', grand_v)],
        [Paragraph('Paid', lbl), Paragraph(f'{cur} {paid:.2f}', pay)],
        [Paragraph('Balance Due', grand_l), Paragraph(f'{cur} {balance:.2f}', due)],
    ]

    t = Table(rows, colWidths=[45 * mm, 30 * mm])
    style = [
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEABOVE', (0, 1), (-1, 1), 0.5, colors.HexColor('#adb5bd')),
    ]
    t.setStyle(TableStyle(style))

    outer = Table([['', t]], colWidths=[105 * mm, 75 * mm])
    outer.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    return outer


# ============================================================
# Payment history
# ============================================================
def _payments_table(order):
    if not order.payments:
        return None
    lab = _get_lab()
    cur = lab.get('currency_symbol', 'Rs')

    styles = getSampleStyleSheet()
    header = ParagraphStyle('H', parent=styles['Normal'], fontSize=9,
                            fontName='Helvetica-Bold')
    cell = ParagraphStyle('C', parent=styles['Normal'], fontSize=9)

    data = [[
        Paragraph('Date', header),
        Paragraph('Method', header),
        Paragraph('Reference', header),
        Paragraph('Amount', header),
    ]]

    for p in order.payments:
        data.append([
            Paragraph(_fmt_dt(p.created_at), cell),
            Paragraph(p.method_label, cell),
            Paragraph(p.reference or '—', cell),
            Paragraph(f'{cur} {p.amount:.2f}', cell),
        ])

    t = Table(data, colWidths=[40 * mm, 30 * mm, 60 * mm, 25 * mm], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e9ecef')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#adb5bd')),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t


# ============================================================
# Main entry point
# ============================================================
def generate_invoice_pdf(order, tax_rate=DEFAULT_TAX_RATE) -> io.BytesIO:
    lab = _get_lab()
    primary = _hex(lab['primary_color'])

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm,
        title=f'Invoice INV-{order.order_code}',
        author=lab['name'],
    )

    story = []
    story.append(_header())
    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width='100%', thickness=1.5, color=primary))
    story.append(Spacer(1, 6 * mm))

    story.append(_info_block(order))
    story.append(Spacer(1, 8 * mm))

    story.append(_line_items_table(order))
    story.append(Spacer(1, 6 * mm))
    story.append(_totals_table(order, tax_rate))

    pmt = _payments_table(order)
    if pmt:
        story.append(Spacer(1, 10 * mm))
        styles = getSampleStyleSheet()
        story.append(Paragraph('<b>Payment History</b>', styles['Normal']))
        story.append(Spacer(1, 3 * mm))
        story.append(pmt)

    story.append(Spacer(1, 15 * mm))
    story.append(HRFlowable(width='100%', thickness=0.5,
                            color=colors.HexColor('#dee2e6')))
    story.append(Spacer(1, 3 * mm))

    styles = getSampleStyleSheet()
    small = ParagraphStyle('S', parent=styles['Normal'], fontSize=8,
                           textColor=colors.HexColor('#6c757d'))

    footer_parts = [f'Thank you for choosing {lab["name"]}.']
    footer_parts.append(f'Generated on {_fmt_dt(_now())}.')
    if lab['email']:
        footer_parts.append(f'For billing inquiries, contact {lab["email"]}.')

    story.append(Paragraph(' '.join(footer_parts), small))

    if lab['footer_note']:
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(f'<i>{lab["footer_note"]}</i>', small))

    doc.build(story)
    buffer.seek(0)
    return buffer