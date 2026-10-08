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
    """Return header flowable, layout driven by lab['header_style']."""
    lab = _get_lab()
    styles = getSampleStyleSheet()
    primary = _hex(lab['primary_color'])
    style_key = (lab.get('header_style') or 'centered').lower()
    if style_key == 'left':
        return _header_left(lab, styles, primary)
    if style_key == 'split':
        return _header_split(lab, styles, primary)
    if style_key == 'banner':
        return _header_banner(lab, styles, primary)
    return _header_centered(lab, styles, primary)



def _contact_line(lab):
    parts = [p for p in [lab['address'], lab['phone'], lab['email'], lab['website']] if p]
    return ' ? '.join(parts) if parts else ''



def _header_banner(lab, styles, primary):
    """Logo only, full width. Use when the logo image already contains
    the lab name and tagline (like a banner)."""
    rows = []
    logo = _logo_flowable(lab, max_height_mm=30, max_width_mm=170)
    if logo is None:
        # fall back to centered if no logo
        return _header_centered(lab, styles, primary)
    logo.hAlign = 'CENTER'
    # widen the drawn image to fill the page if possible
    iw, ih = logo.imageWidth, logo.imageHeight
    if iw and ih:
        target_w = 170 * mm
        scale = min(target_w / iw, (30 * mm) / ih)
        logo.drawWidth = iw * scale
        logo.drawHeight = ih * scale
    rows.append([logo])
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


def _header_centered(lab, styles, primary):
    """Current default ? logo top, name + tagline + contact below, all centered."""
    name_style = ParagraphStyle('LabName', parent=styles['Heading1'],
                                fontSize=18, textColor=primary, alignment=1, spaceAfter=2)
    tag_style  = ParagraphStyle('Tagline', parent=styles['Normal'],
                                fontSize=9, textColor=colors.HexColor('#6c757d'),
                                alignment=1, spaceAfter=4)
    contact_style = ParagraphStyle('Contact', parent=styles['Normal'],
                                   fontSize=8, alignment=1,
                                   textColor=colors.HexColor('#495057'))
    license_style = ParagraphStyle('License', parent=styles['Normal'],
                                   fontSize=7.5, alignment=1,
                                   textColor=colors.HexColor('#6c757d'))
    rows = []
    logo = _logo_flowable(lab, max_height_mm=22, max_width_mm=60)
    if logo is not None:
        rows.append([logo])
        rows.append([Spacer(1, 3 * mm)])
    rows.append([Paragraph(lab['name'], name_style)])
    if lab['tagline']:
        rows.append([Paragraph(lab['tagline'], tag_style)])
    if lab.get('header_show_contact', True):
        cl = _contact_line(lab)
        if cl:
            rows.append([Paragraph(cl, contact_style)])
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


def _header_left(lab, styles, primary):
    """Logo top-left, name + tagline + contact stacked left-aligned."""
    name_style = ParagraphStyle('LabName', parent=styles['Heading1'],
                                fontSize=18, textColor=primary, alignment=0, spaceAfter=2)
    tag_style  = ParagraphStyle('Tagline', parent=styles['Normal'],
                                fontSize=9, textColor=colors.HexColor('#6c757d'),
                                alignment=0, spaceAfter=4)
    contact_style = ParagraphStyle('Contact', parent=styles['Normal'],
                                   fontSize=8, alignment=0,
                                   textColor=colors.HexColor('#495057'))
    rows = []
    logo = _logo_flowable(lab, max_height_mm=22, max_width_mm=60)
    if logo is not None:
        logo.hAlign = 'LEFT'
        rows.append([logo])
        rows.append([Spacer(1, 2 * mm)])
    rows.append([Paragraph(lab['name'], name_style)])
    if lab['tagline']:
        rows.append([Paragraph(lab['tagline'], tag_style)])
    if lab.get('header_show_contact', True):
        cl = _contact_line(lab)
        if cl:
            rows.append([Paragraph(cl, contact_style)])
        if lab['license_no']:
            rows.append([Paragraph(f"License #: {lab['license_no']}", contact_style)])
    t = Table(rows, colWidths=[170 * mm])
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    return t


def _header_split(lab, styles, primary):
    """Two-column header ? logo left, name + contact right."""
    name_style = ParagraphStyle('LabName', parent=styles['Heading1'],
                                fontSize=16, textColor=primary, alignment=2, spaceAfter=2)
    tag_style  = ParagraphStyle('Tagline', parent=styles['Normal'],
                                fontSize=9, textColor=colors.HexColor('#6c757d'),
                                alignment=2, spaceAfter=3)
    contact_style = ParagraphStyle('Contact', parent=styles['Normal'],
                                   fontSize=8, alignment=2,
                                   textColor=colors.HexColor('#495057'))

    right_rows = [[Paragraph(lab['name'], name_style)]]
    if lab['tagline']:
        right_rows.append([Paragraph(lab['tagline'], tag_style)])
    if lab.get('header_show_contact', True):
        cl = _contact_line(lab)
        if cl:
            right_rows.append([Paragraph(cl, contact_style)])
        if lab['license_no']:
            right_rows.append([Paragraph(f"License #: {lab['license_no']}", contact_style)])

    right = Table(right_rows, colWidths=[100 * mm])
    right.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))

    logo = _logo_flowable(lab, max_height_mm=22, max_width_mm=55)
    if logo is not None:
        logo.hAlign = 'LEFT'
        left_cell = logo
    else:
        left_cell = Paragraph('', styles['Normal'])

    t = Table([[left_cell, right]], colWidths=[65 * mm, 105 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    return t


# ============================================================
# Canvas-drawable header — for onLaterPages repeat
# ============================================================
def draw_letterhead_on_canvas(canvas, doc):
    """Draw the letterhead (logo + lab name + contact + divider) at the
    top of the current page. Called from doc.build's onLaterPages."""
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from .branding import _get_lab

    lab = _get_lab()
    page_w, page_h = doc.pagesize
    left = doc.leftMargin
    right = doc.rightMargin
    top = 15 * mm

    try:
        primary = colors.HexColor(lab.get('primary_color') or '#0d6efd')
    except Exception:
        primary = colors.HexColor('#0d6efd')

    canvas.saveState()

    y = page_h - top
    # Lab name (centered)
    canvas.setFont('Helvetica-Bold', 16)
    canvas.setFillColor(colors.HexColor('#b91c1c'))  # red-ish
    canvas.drawCentredString(page_w / 2, y - 5 * mm, lab.get('name', 'LABORATORY'))

    # Tagline
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#6c757d'))
    if lab.get('tagline'):
        canvas.drawCentredString(page_w / 2, y - 9 * mm, lab['tagline'])

    # Contact line
    contact = ' · '.join(filter(None, [
        lab.get('address', '').split('\n')[0] if lab.get('address') else '',
        lab.get('phone', ''),
        lab.get('email', ''),
    ]))
    if contact:
        canvas.setFont('Helvetica', 7.5)
        canvas.drawCentredString(page_w / 2, y - 13 * mm, contact)

    # Divider
    canvas.setStrokeColor(primary)
    canvas.setLineWidth(1.5)
    canvas.line(left, y - 16 * mm, page_w - right, y - 16 * mm)

    canvas.restoreState()


# ============================================================
# Continuation-page header (thin strip) — drawn by onLaterPages
# ============================================================
def draw_continuation_header(canvas, doc, order=None):
    """Compact patient strip + divider for pages 2+."""
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from .branding import _get_lab

    lab = _get_lab()
    page_w, page_h = doc.pagesize
    left = doc.leftMargin
    right = doc.rightMargin
    box_w = page_w - left - right

    try:
        primary = colors.HexColor(lab.get('primary_color') or '#0d6efd')
    except Exception:
        primary = colors.HexColor('#0d6efd')

    canvas.saveState()

    # Row 1: lab name (left) + contact (right)
    y1 = page_h - 8 * mm
    canvas.setFont('Helvetica-Bold', 9)
    canvas.setFillColor(colors.HexColor('#b91c1c'))
    canvas.drawString(left, y1, lab.get('name', 'LABORATORY'))

    contact = ' · '.join(filter(None, [lab.get('phone', ''), lab.get('email', '')]))
    if contact:
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.HexColor('#6c757d'))
        canvas.drawRightString(page_w - right, y1, contact)

    # Row 2: patient | patient code | gender/age | order | status
    if order is not None:
        p = getattr(order, 'patient', None)
        parts = []
        if p and p.full_name:
            parts.append('Patient: ' + p.full_name)
        if p and p.patient_code:
            parts.append(p.patient_code)
        if p and p.gender:
            parts.append(p.gender)
        if order.order_code:
            parts.append('Order ' + order.order_code)
        if order.created_at:
            parts.append(order.created_at.strftime('%d-%b-%Y'))
        if order.status:
            parts.append(order.status.title())
        line2 = '  |  '.join(parts)
        if line2:
            canvas.setFont('Helvetica', 7.5)
            canvas.setFillColor(colors.HexColor('#212529'))
            canvas.drawString(left, page_h - 12.5 * mm, line2)

    # Divider
    canvas.setStrokeColor(primary)
    canvas.setLineWidth(0.8)
    canvas.line(left, page_h - 15 * mm, page_w - right, page_h - 15 * mm)

    canvas.restoreState()