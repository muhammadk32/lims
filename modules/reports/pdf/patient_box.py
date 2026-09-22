"""Patient + order information box."""
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Table, TableStyle

from .base import _fmt_dt_pretty
from .branding import _get_lab, _hex


def _patient_info_table(order):
    """Two-column info box with patient + order details."""
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

    registered_pretty = _fmt_dt_pretty(order.created_at) or '—'
    if order.reported_at:
        reporting_value = _fmt_dt_pretty(order.reported_at) or '—'
        reporting_pending = False
    else:
        reporting_value = 'Pending Approval'
        reporting_pending = True

    from modules.orders.models import OrderStatus
    status_label = OrderStatus.LABELS.get(order.status, order.status.capitalize())

    right = [
        [Paragraph('<b>Order Information</b>', styles['Heading4']), ''],
        cell('Order Code', order.order_code),
        cell('Registered On', registered_pretty),
        cell_pending('Reporting Date', reporting_value, reporting_pending),
        cell('Doctor', order.referred_by_name or (order.doctor.full_name if order.doctor else '—')),
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

    t.setStyle(TableStyle([
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
    ]))
    return t

