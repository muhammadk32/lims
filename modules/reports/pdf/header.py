"""Report header — lab name, logo, contact info."""
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image

from .branding import _get_lab, _hex


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
