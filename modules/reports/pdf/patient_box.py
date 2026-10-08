"""Patient + order info box — 4-column reference layout with QR top-right."""
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Table, TableStyle, Image

from .base import _fmt_dt_pretty
from .branding import _get_lab, _hex
from .qr import qr_png_bytes


def _patient_info_table(order):
    """4-column patient + order info with QR code on the right."""
    lab = _get_lab()

    styles = getSampleStyleSheet()
    label_style = ParagraphStyle('PB_Lbl', parent=styles['Normal'],
                                 fontSize=7, leading=8.5,
                                 fontName='Helvetica-Bold',
                                 textColor=colors.HexColor('#495057'))
    value_style = ParagraphStyle('PB_Val', parent=styles['Normal'],
                                 fontSize=8.5, leading=10,
                                 textColor=colors.black)

    def block(label, value):
        return [
            Paragraph(label, label_style),
            Paragraph(str(value if value not in (None, '') else '-'), value_style),
        ]

    registered_pretty = _fmt_dt_pretty(order.created_at) or '-'
    from modules.orders.models import OrderStatus
    status_label = OrderStatus.LABELS.get(order.status, order.status.capitalize())

    patient_code = getattr(order.patient, 'patient_code', None) or '-'
    age_str = order.patient.compute_age() or '-'
    gender = order.patient.gender or '-'
    age_gender = f'{age_str} / {gender}'

    doctor_name = order.referred_by_name or (
        order.doctor.full_name if order.doctor else '-')

    ref_value = order.company_name or 'Walk-in'

    col1_r1 = block('Patient Name:', order.patient.full_name)
    col1_r2 = block('Age/Gender:', age_gender)

    col2_r1 = block('Registered At:', lab.get('name') or '-')
    col2_r2 = block('Registered On:', registered_pretty)

    col3_r1 = block('Reference:', ref_value)
    col3_r2 = block('Consultant:', doctor_name)

    col4_r1 = block('Patient No:', patient_code)
    col4_r2 = block('Case No:', order.order_code)

    rows = [
        [col1_r1[0], col2_r1[0], col3_r1[0], col4_r1[0]],
        [col1_r1[1], col2_r1[1], col3_r1[1], col4_r1[1]],
        [col1_r2[0], col2_r2[0], col3_r2[0], col4_r2[0]],
        [col1_r2[1], col2_r2[1], col3_r2[1], col4_r2[1]],
    ]

    # ---- QR (blank until content decided) ----
    qr_flowable = None
    try:
        from core.models import LabSettings
        s = LabSettings.get()
        show_qr = bool(getattr(s, 'report_show_qr', True)) if s else True
    except Exception:
        show_qr = True

    if show_qr:
        buf = qr_png_bytes(order.order_code or '')
        if buf:
            qr_flowable = Image(buf, width=22 * mm, height=22 * mm)
            qr_flowable.hAlign = 'CENTER'

    if qr_flowable is not None:
        for i, r in enumerate(rows):
            r.append(qr_flowable if i == 0 else '')

    n_cols = len(rows[0])
    col_widths = [42 * mm, 42 * mm, 42 * mm, 30 * mm]
    if qr_flowable is not None:
        col_widths.append(26 * mm)

    t = Table(rows, colWidths=col_widths)

    style = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('BOX', (0, 0), (-1, -1), 0.4, colors.HexColor('#adb5bd')),
    ]
    if qr_flowable is not None:
        style.append(('SPAN', (4, 0), (4, 3)))
        style.append(('VALIGN', (4, 0), (4, 3), 'MIDDLE'))
        style.append(('ALIGN', (4, 0), (4, 3), 'CENTER'))

    t.setStyle(TableStyle(style))
    return t
