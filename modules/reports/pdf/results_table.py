"""Results table — grouped by panel, with abnormal highlighting."""
import re
from reportlab.lib import colors
from modules.tests.ranges import (
    resolve_range_for_order as _rrfo,
    critical_for_order as _cfo,
    evaluate_for_order as _efo,
    pick_range_for_patient as _prfp,
)
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


def _results_table(order, previous_map=None, date_labels=None, items_override=None):
    """Results table with panel grouping + previous results columns.

    previous_map: {test_name_lower: [(date, value), ...]}
    date_labels:  [datetime, datetime]  -- for column headers
    Returns (Table, notes_flowables, abnormal_count, critical_count).
    """
    previous_map = previous_map or {}
    date_labels = date_labels or []
    n_prev = len(date_labels)

    lab = _get_lab()
    primary = _hex(lab['primary_color'])

    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        'Hdr', parent=styles['Normal'], fontSize=8.5,
        textColor=colors.white, fontName='Helvetica-Bold',
    )
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8.5)
    cell_bold = ParagraphStyle(
        'CellBold', parent=styles['Normal'], fontSize=8.5, fontName='Helvetica-Bold',
    )
    cell_prev = ParagraphStyle(
        'CellPrev', parent=styles['Normal'], fontSize=8.5,
        textColor=colors.HexColor('#6c757d'),
    )
    panel_header_style = ParagraphStyle(
        'PanelHdr', parent=styles['Normal'], fontSize=9,
        fontName='Helvetica-Bold', textColor=colors.HexColor('#1e40af'),
    )
    notes_style = ParagraphStyle(
        'RangeNotes', parent=styles['Normal'], fontSize=7.5,
        textColor=colors.HexColor('#495057'), leftIndent=10, spaceBefore=2,
    )
    panel_sub_style = ParagraphStyle(
        'PanelSub', parent=styles['Normal'], fontSize=8.5,
        textColor=colors.HexColor('#212529'), leftIndent=10,
    )

    def _collect_pcr_details(bucket, item, order_):
        """If this item has a Result with PCR fields, render them as
        a borderless block under the result row."""
        # Query Result directly (backref can be None for detached sessions)
        from modules.results.models import Result
        r = Result.query.filter_by(order_item_id=item.id).first()
        if r is None:
            return
        has_any = any([r.specimen, r.result_type, r.viral_load_type,
                       r.interpretation_html, r.method_html,
                       r.suggestion_html, r.comments_html])
        if not has_any:
            return

        import re as _re
        def _clean(html):
            if not html:
                return ''
            txt = _re.sub(r'<[^>]+>', ' ', html)
            txt = _re.sub(r'&nbsp;', ' ', txt)
            txt = _re.sub(r'\s+', ' ', txt).strip()
            return txt

        inner = []
        if r.specimen:
            inner.append(f'<b>SPECIMEN:</b> {r.specimen}')
        if r.result_type or r.value:
            inner.append(f'<b>RESULT:</b> {r.result_type or r.value}')
        if r.viral_load_type:
            inner.append(f'<b>VIRAL LOAD:</b> {r.viral_load_type}')

        blocks = [
            ('Interpretation', _clean(r.interpretation_html)),
            ('Methodologies',  _clean(r.method_html)),
            ('Suggestions',    _clean(r.suggestion_html)),
            ('Comments',       _clean(r.comments_html)),
        ]
        for label, body in blocks:
            if body:
                inner.append(f'<br/><b><u>{label}:</u></b><br/>{body}')

        if not inner:
            return
        html = '<br/>'.join(inner)
        pcr_style = ParagraphStyle(
            'PCRDetail', parent=styles['Normal'], fontSize=7.5,
            textColor=colors.HexColor('#212529'), leftIndent=8, spaceBefore=4,
            spaceAfter=6, leading=10,
        )
        bucket.append(Paragraph(html, pcr_style))

    def _collect_note(bucket, test, order_):
        """Append (test_name, note) as a Paragraph to the notes bucket."""
        try:
            rng = _prfp(test, getattr(order_, 'patient', None))
        except Exception:
            rng = None
        notes = getattr(rng, 'notes', None) if rng else None
        if not notes:
            return
        plain = re.sub(r'<[^>]+>', ' ', notes)
        plain = re.sub(r'\s+', ' ', plain).strip()
        if not plain:
            return
        html = f'<b>{test.name}:</b> {plain}'
        bucket.append(Paragraph(html, notes_style))

    def _append_notes_row(test, order_, n_cols):
        """Return a notes row (as list) if the matching range has notes, else None."""
        try:
            rng = _prfp(test, getattr(order_, 'patient', None))
        except Exception:
            rng = None
        notes = getattr(rng, 'notes', None) if rng else None
        if not notes:
            return None
        # strip HTML tags for PDF (reportlab can't render HTML)
        import re as _re
        plain = _re.sub(r'<[^>]+>', ' ', notes)
        plain = _re.sub(r'\s+', ' ', plain).strip()
        if not plain:
            return None
        blank = Paragraph('', cell_style)
        return [blank] + [Paragraph(plain, notes_style)] + [blank] * (n_cols - 2)

    def fmt_date(d):
        try:
            return d.strftime('%d-%b-%y')
        except Exception:
            return '-'

    # Header row
    header_cells = [
        Paragraph('Test', header_style),
        Paragraph(order.created_at.strftime('%d-%b-%y') if order.created_at else 'Result', header_style),
        Paragraph('Unit', header_style),
        Paragraph('Normal Range', header_style),
    ]
    for d in date_labels:
        header_cells.append(Paragraph(fmt_date(d), header_style))
    data = [header_cells]

    notes_flowables = []
    notes_row_indices = []
    abnormal_rows = []
    critical_rows = []
    row_idx = 1

    def prev_values_for(name):
        priors = previous_map.get((name or '').lower(), [])
        out = []
        for i in range(n_prev):
            if i < len(priors):
                out.append(priors[i][1])
            else:
                out.append(None)
        return out

    _iter_items = items_override if items_override is not None else order.top_level_items
    for item in _iter_items:
        if item.has_children:
            panel_cells = [
                Paragraph('> ' + item.test.name, panel_header_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
            ]
            panel_cells += [Paragraph('', cell_style)] * n_prev
            data.append(panel_cells)
            row_idx += 1

            for child in item.children:
                flag, _crit = _efo(child.test, child.result_value, order)
                if flag == 'abnormal':
                    abnormal_rows.append(row_idx)
                    if _crit:
                        critical_rows.append(row_idx)

                child_is_pcr = (child.test.result_format or '').lower() in ('pcr', 'pcr_quant', 'molecular')
                row = [
                    Paragraph(child.test.name, panel_sub_style),
                    Paragraph('' if child_is_pcr else (child.result_value or '-'), cell_style),
                    Paragraph('' if child_is_pcr else (child.test.unit or '-'), cell_style),
                    Paragraph('' if child_is_pcr else (_rrfo(child.test, order) or '-'), cell_style),
                ]
                for pv in prev_values_for(child.test.name):
                    row.append(Paragraph(pv or '-', cell_prev))
                data.append(row)
                row_idx += 1
                _collect_note(notes_flowables, child.test, order)
                _collect_pcr_details(notes_flowables, child, order)
        else:
            flag, _crit = _efo(item.test, item.result_value, order)
            if flag == 'abnormal':
                abnormal_rows.append(row_idx)
                if _crit:
                    critical_rows.append(row_idx)

            is_pcr = (item.test.result_format or '').lower() in ('pcr', 'pcr_quant', 'molecular')
            row = [
                Paragraph(item.test.name, cell_bold),
                Paragraph('' if is_pcr else (item.result_value or '-'), cell_style),
                Paragraph('' if is_pcr else (item.test.unit or '-'), cell_style),
                Paragraph('' if is_pcr else (_rrfo(item.test, order) or '-'), cell_style),
            ]
            for pv in prev_values_for(item.test.name):
                row.append(Paragraph(pv or '-', cell_prev))
            data.append(row)
            row_idx += 1
            _collect_note(notes_flowables, item.test, order)
            _collect_pcr_details(notes_flowables, item, order)

    # Column widths
    if n_prev > 0:
        col_widths = [55 * mm, 22 * mm, 18 * mm, 35 * mm]
        col_widths += [22 * mm] * n_prev
    else:
        col_widths = [65 * mm, 30 * mm, 25 * mm, 35 * mm]

    t = Table(data, colWidths=col_widths, repeatRows=1)

    style = [
        ('BACKGROUND', (0, 0), (-1, 0), primary),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#adb5bd')),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]

    # Panel header rows (blue)
    for i, row in enumerate(data):
        if i == 0:
            continue
        cell0 = row[0]
        if hasattr(cell0, 'text') and cell0.text.startswith('>'):
            style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#dbeafe')))

    # Abnormal rows (light pink)
    for r in abnormal_rows:
        style.append(('BACKGROUND', (0, r), (-1, r), colors.HexColor('#f8d7da')))
        style.append(('TEXTCOLOR', (1, r), (1, r), colors.HexColor('#b02a37')))

    # Critical rows (darker pink - applied after, wins)
    for r in critical_rows:
        style.append(('BACKGROUND', (0, r), (-1, r), colors.HexColor('#f5b7b1')))
        style.append(('TEXTCOLOR', (1, r), (1, r), colors.HexColor('#7f1d1d')))

    # Strip grid + padding from notes rows so they read as prose
    for r in notes_row_indices:
        style.append(('LINEABOVE',   (0, r), (-1, r), 0, colors.white))
        style.append(('LINEBELOW',   (0, r), (-1, r), 0, colors.white))
        style.append(('LINEBEFORE',  (0, r), (0, r),  0, colors.white))
        style.append(('LINEAFTER',   (-1, r), (-1, r), 0, colors.white))
        style.append(('BACKGROUND',  (0, r), (-1, r), colors.white))
        style.append(('TOPPADDING',  (0, r), (-1, r), 2))
        style.append(('BOTTOMPADDING', (0, r), (-1, r), 6))

    t.setStyle(TableStyle(style))
    return t, notes_flowables, len(abnormal_rows), len(critical_rows)