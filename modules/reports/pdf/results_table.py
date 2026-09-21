"""Results table — grouped by panel, with abnormal highlighting."""
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Table, TableStyle

from .branding import _get_lab, _hex


def _flag_result(normal_range, result_value):
    """Return 'normal' | 'abnormal' | 'unknown'."""
    try:
        from modules.results.validators import check_result
        return check_result(normal_range, result_value)
    except Exception:
        return 'unknown'


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
