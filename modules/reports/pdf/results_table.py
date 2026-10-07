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
from reportlab.platypus import Paragraph, Table, TableStyle, HRFlowable, Spacer

from .branding import _get_lab, _hex
from .culture_table import _culture_block as _culture_flowables


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

    # PCR full-page takeover: single PCR item
    if items_override and len(items_override) == 1:
        _only = items_override[0]
        _fmt = (_only.test.result_format or '').lower()
        if _fmt in ('pcr', 'molecular', 'pcr_quant'):
            return _pcr_section(_only, order)

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
    section_header_style = ParagraphStyle(
        'SectionHdr', parent=styles['Normal'], fontSize=10,
        fontName='Helvetica-Bold', textColor=colors.black,
    )
    col_header_style = ParagraphStyle(
        'ColHdr', parent=styles['Normal'], fontSize=8.5,
        fontName='Helvetica-Bold', textColor=colors.black,
    )

    # Header row (used only if no categories exist)
    header_cells = [
        Paragraph('Test', header_style),
        Paragraph(order.created_at.strftime('%d-%b-%y') if order.created_at else 'Result', header_style),
        Paragraph('Unit', header_style),
        Paragraph('Normal Range', header_style),
    ]
    for d in date_labels:
        header_cells.append(Paragraph(fmt_date(d), header_style))

    data = []
    notes_flowables = []
    notes_row_indices = []
    abnormal_rows = []
    critical_rows = []
    row_idx = 0

    def fmt_date(d):
        try:
            return d.strftime('%d-%b-%y')
        except Exception:
            return '-'

    def prev_values_for(name):
        priors = previous_map.get((name or '').lower(), [])
        out = []
        for i in range(n_prev):
            if i < len(priors):
                out.append(priors[i][1])
            else:
                out.append(None)
        return out

    def _collect_note(bucket, test, order_):
        # The normal range is already shown in the REFERENCE RANGE column —
        # do not repeat it as a note below the table.
        return

    def _collect_culture(bucket, item, order_):
        fmt = (item.test.result_format or '').lower()
        if fmt not in ('culture', 'culture_sensitivity'):
            return
        from modules.results.models import Result
        from core.models import CultureAntibiotic
        r = Result.query.filter_by(order_item_id=item.id).first()
        if not r:
            return
        ab_rows = CultureAntibiotic.query.filter_by(order_item_id=item.id).all()
        try:
            for f in _culture_flowables(item, r, ab_rows):
                bucket.append(f)
        except Exception as e:
            print(f'[culture_table] failed: {e}')

    def _collect_pcr_details(bucket, item, order_):
        from modules.results.models import Result
        r = Result.query.filter_by(order_item_id=item.id).first()
        tpl = None
        try:
            from modules.tests.models import PcrTemplate
            tpl = PcrTemplate.query.filter_by(test_id=item.test_id).first()
        except Exception:
            tpl = None

        def _pick(a, b):
            return a if a else (b if tpl else None)

        specimen    = r.specimen if r else None
        result_type = (r.result_type or r.value) if r else None
        viral_load  = r.viral_load_type if r else None
        interpretation = _pick(r.interpretation_html if r else None,
                               tpl.interpretation_html if tpl else None)
        methodology = _pick(r.method_html if r else None,
                            tpl.methodology_html if tpl else None)
        suggestion  = _pick(r.suggestion_html if r else None,
                            tpl.suggestion_html if tpl else None)
        comments    = _pick(r.comments_html if r else None,
                            tpl.comments_html if tpl else None)

        if not any([specimen, result_type, viral_load, interpretation,
                    methodology, suggestion, comments]):
            return

        def _clean(html):
            if not html:
                return ''
            h = str(html)
            h = re.sub(r'<br\s*/?>', '<br/>', h, flags=re.I)
            h = re.sub(r'</p\s*>', '<br/><br/>', h, flags=re.I)
            h = re.sub(r'<p[^>]*>', '', h, flags=re.I)
            h = re.sub(r'</?(div|span)[^>]*>', '', h, flags=re.I)
            h = re.sub(r'<strong[^>]*>', '<b>', h, flags=re.I)
            h = re.sub(r'</strong\s*>', '</b>', h, flags=re.I)
            h = re.sub(r'<em[^>]*>', '<i>', h, flags=re.I)
            h = re.sub(r'</em\s*>', '</i>', h, flags=re.I)
            h = re.sub(r'<(?!/?(b|i|u|br|font|super|sub)\b)[^>]+>', '', h, flags=re.I)
            h = re.sub(r'&nbsp;', ' ', h)
            h = re.sub(r'&ndash;', '\u2013', h)
            h = re.sub(r'&mdash;', '\u2014', h)
            h = re.sub(r'&amp;', '&', h)
            h = re.sub(r'[ \t]+', ' ', h)
            h = re.sub(r'(\s*<br/>\s*){3,}', '<br/><br/>', h)
            h = re.sub(r'&(?!(amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+)\b)', '&amp;', h)
            return h.strip()

        body_style = ParagraphStyle('PcrBody', parent=styles['Normal'],
                                    fontSize=7, leading=9)
        head_style = ParagraphStyle('PcrHead', parent=styles['Normal'],
                                    fontSize=8, fontName='Helvetica-Bold')

        # --- MOLECULAR REPORT heading + test name ---
        mol_hdr_style = ParagraphStyle('MolHdr', parent=styles['Normal'],
                                       fontSize=10, fontName='Helvetica-Bold',
                                       textColor=colors.black)
        test_name_style = ParagraphStyle('MolTestName', parent=styles['Normal'],
                                         fontSize=9, fontName='Helvetica-Bold',
                                         textColor=colors.black)

        bucket.append(Spacer(1, 3 * mm))
        # Underlined header box like other sections
        _mol_hdr_tbl = Table([[Paragraph('MOLECULAR REPORT', mol_hdr_style)]],
                             colWidths=[170 * mm])
        _mol_hdr_tbl.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1.2, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 1.2, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        bucket.append(_mol_hdr_tbl)
        bucket.append(Spacer(1, 1 * mm))
        bucket.append(Paragraph(item.test.name, test_name_style))

        # SPECIMEN / RESULT / VIRAL LOAD
        if specimen:
            bucket.append(Paragraph(f'<b>SPECIMEN:</b> {specimen}', body_style))
        if result_type:
            bucket.append(Paragraph(f'<b>RESULT:</b> {result_type}', body_style))
        if viral_load:
            bucket.append(Paragraph(f'<b>VIRAL LOAD:</b> {viral_load}', body_style))

        for label, body in [('Interpretation', interpretation),
                            ('Methodologies', methodology),
                            ('Suggestions', suggestion),
                            ('Comments', comments)]:
            cleaned = _clean(body)
            if cleaned:
                bucket.append(Spacer(1, 2 * mm))
                bucket.append(HRFlowable(width='100%', thickness=0.4,
                                         color=colors.HexColor('#adb5bd')))
                bucket.append(Paragraph(f'<u><b>{label}:</b></u>', head_style))
                bucket.append(Paragraph(cleaned, body_style))

    _iter_items = items_override if items_override is not None else order.top_level_items

    # ---- Group items by category (alphabetical; uncategorized last) ----
    class _SectionMarker:
        __slots__ = ('name', 'test', 'has_children', 'children', 'result_value')
        def __init__(self, name):
            self.name = name
            self.test = None
            self.has_children = False
            self.children = []
            self.result_value = None

    def _cat_key(it):
        c = it.test.category_ref if getattr(it, 'test', None) else None
        return (1, '') if c is None else (0, str(c.name).upper())

    _sorted_items = sorted([i for i in _iter_items if getattr(i, 'test', None)],
                           key=_cat_key)

    _with_headers = []
    _last_cat = object()
    for _it in _sorted_items:
        _c = _it.test.category_ref if _it.test else None
        _cn = _c.name if _c else None
        if _cn != _last_cat:
            _last_cat = _cn
            if _cn:
                _with_headers.append(_SectionMarker(_cn))
        _with_headers.append(_it)

    _section_header_rows = []
    _colhdr_rows = []

    _with_headers = list(_with_headers)
    for item in _with_headers:
        if isinstance(item, _SectionMarker):
            # Skip section if every item under it is PCR (they render standalone below)
            _idx = _with_headers.index(item)
            _upcoming = []
            for _x in _with_headers[_idx + 1:]:
                if isinstance(_x, _SectionMarker):
                    break
                _upcoming.append(_x)
            _has_printable = any(
                (i.test.result_format or '').lower() not in ('pcr', 'pcr_quant', 'molecular')
                for i in _upcoming if getattr(i, 'test', None)
            )
            if not _has_printable:
                continue

            # Section title row — skip MOLECULAR (handled inside PCR blocks)
            _is_molecular_section = (item.name or '').strip().upper() == 'MOLECULAR'
            if not _is_molecular_section:
                if '_first_section_done' in dir() and _first_section_done:
                    _spacer = [Paragraph('', cell_style)] * (4 + n_prev)
                    data.append(_spacer)
                    row_idx += 1
                _first_section_done = True
                _hdr = [Paragraph(item.name.upper() + ' REPORT', section_header_style)]
                _hdr += [Paragraph('', cell_style)] * (3 + n_prev)
                data.append(_hdr)
                _section_header_rows.append(row_idx)
                row_idx += 1

            # Column header row
            _colhdr = [
                Paragraph('TEST', col_header_style),
                Paragraph('RESULT', col_header_style),
                Paragraph('UNIT', col_header_style),
                Paragraph('REFERENCE RANGE', col_header_style),
            ]
            for _d in date_labels:
                _colhdr.append(Paragraph(fmt_date(_d), col_header_style))
            data.append(_colhdr)
            _colhdr_rows.append(row_idx)
            row_idx += 1
            continue

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
                _collect_culture(notes_flowables, child, order)
        else:
            flag, _crit = _efo(item.test, item.result_value, order)
            if flag == 'abnormal':
                abnormal_rows.append(row_idx)
                if _crit:
                    critical_rows.append(row_idx)

            is_pcr = (item.test.result_format or '').lower() in ('pcr', 'pcr_quant', 'molecular')
            is_culture = (item.test.result_format or '').lower() in ('culture', 'culture_sensitivity')

            if is_culture:
                _collect_culture(notes_flowables, item, order)
            elif is_pcr:
                # PCR: skip the flat row entirely; render standalone section below
                _collect_pcr_details(notes_flowables, item, order)
            else:
                row = [
                    Paragraph(item.test.name, cell_bold),
                    Paragraph(item.result_value or '-', cell_style),
                    Paragraph(item.test.unit or '-', cell_style),
                    Paragraph(_rrfo(item.test, order) or '-', cell_style),
                ]
                for pv in prev_values_for(item.test.name):
                    row.append(Paragraph(pv or '-', cell_prev))
                data.append(row)
                row_idx += 1
                _collect_note(notes_flowables, item.test, order)

    # Column widths
    if n_prev > 0:
        col_widths = [55 * mm, 22 * mm, 18 * mm, 35 * mm]
        col_widths += [22 * mm] * n_prev
    else:
        col_widths = [65 * mm, 30 * mm, 25 * mm, 35 * mm]

    if len(data) <= 1:
        empty = Table([['']], colWidths=[1])
        empty.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        return empty, notes_flowables, len(abnormal_rows), len(critical_rows)

    t = Table(data, colWidths=col_widths, repeatRows=0)

    style = [
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]

    # Section title rows: black underline above + below, full span
    for _r in _section_header_rows:
        style.append(('LINEABOVE', (0, _r), (-1, _r), 1.2, colors.black))
        style.append(('LINEBELOW', (0, _r), (-1, _r), 1.2, colors.black))
        style.append(('BACKGROUND', (0, _r), (-1, _r), colors.white))
        style.append(('SPAN', (0, _r), (-1, _r)))

    # Column header rows: thin underline below
    for _r in _colhdr_rows:
        style.append(('LINEBELOW', (0, _r), (-1, _r), 0.8, colors.black))
        style.append(('BACKGROUND', (0, _r), (-1, _r), colors.white))

    # Panel header rows (blue)
    for i, row in enumerate(data):
        if i in _section_header_rows or i in _colhdr_rows:
            continue
        cell0 = row[0]
        if hasattr(cell0, 'text') and cell0.text.startswith('>'):
            style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#dbeafe')))

    # Abnormal rows (light pink)
    for r in abnormal_rows:
        style.append(('BACKGROUND', (0, r), (-1, r), colors.HexColor('#f8d7da')))
        style.append(('TEXTCOLOR', (1, r), (1, r), colors.HexColor('#b02a37')))

    # Critical rows
    for r in critical_rows:
        style.append(('BACKGROUND', (0, r), (-1, r), colors.HexColor('#f5b7b1')))
        style.append(('TEXTCOLOR', (1, r), (1, r), colors.HexColor('#7f1d1d')))

    for r in notes_row_indices:
        style.append(('LINEABOVE', (0, r), (-1, r), 0, colors.white))
        style.append(('LINEBELOW', (0, r), (-1, r), 0, colors.white))
        style.append(('LINEBEFORE', (0, r), (0, r), 0, colors.white))
        style.append(('LINEAFTER', (-1, r), (-1, r), 0, colors.white))
        style.append(('BACKGROUND', (0, r), (-1, r), colors.white))

    t.setStyle(TableStyle(style))
    return t, notes_flowables, len(abnormal_rows), len(critical_rows)


def _pcr_section(item, order):
    """Full-page MOLECULAR DIAGNOSTIC SECTION for a single PCR test.
    Returns (Table, [], 0, 0) matching the _results_table signature.
    """
    import re as _re

    lab = _get_lab()
    primary = _hex(lab['primary_color'])
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('PcrTitle', parent=styles['Normal'],
                                 fontSize=10, fontName='Helvetica-Bold',
                                 textColor=colors.black)
    band_style = ParagraphStyle('PcrBand', parent=styles['Normal'],
                                fontSize=9, fontName='Helvetica-Bold',
                                textColor=colors.black)
    kv_label = ParagraphStyle('PcrKv', parent=styles['Normal'],
                              fontSize=8, fontName='Helvetica-Bold')
    kv_val = ParagraphStyle('PcrKvVal', parent=styles['Normal'], fontSize=8)
    section_head = ParagraphStyle('PcrSec', parent=styles['Normal'],
                                  fontSize=8, fontName='Helvetica-Bold',
                                  textColor=colors.black)
    body_style = ParagraphStyle('PcrBody', parent=styles['Normal'],
                                fontSize=7, leading=9)

    from modules.results.models import Result
    r = Result.query.filter_by(order_item_id=item.id).first()
    tpl = None
    try:
        from modules.tests.models import PcrTemplate
        tpl = PcrTemplate.query.filter_by(test_id=item.test_id).first()
    except Exception:
        tpl = None

    def _pick(a, b):
        return a if a else (b if tpl else None)

    specimen    = r.specimen if r else None
    result_type = (r.result_type or r.value) if r else None
    viral_load  = r.viral_load_type if r else None
    interpretation = _pick(r.interpretation_html if r else None,
                           tpl.interpretation_html if tpl else None)
    methodology = _pick(r.method_html if r else None,
                        tpl.methodology_html if tpl else None)
    comments    = _pick(r.comments_html if r else None,
                        tpl.comments_html if tpl else None)

    def _clean(html):
        if not html:
            return ''
        h = str(html)
        h = _re.sub(r'<br\s*/?>', '<br/>', h, flags=_re.I)
        h = _re.sub(r'</p\s*>', '<br/><br/>', h, flags=_re.I)
        h = _re.sub(r'<p[^>]*>', '', h, flags=_re.I)
        h = _re.sub(r'</?(div|span)[^>]*>', '', h, flags=_re.I)
        h = _re.sub(r'<strong[^>]*>', '<b>', h, flags=_re.I)
        h = _re.sub(r'</strong\s*>', '</b>', h, flags=_re.I)
        h = _re.sub(r'<em[^>]*>', '<i>', h, flags=_re.I)
        h = _re.sub(r'</em\s*>', '</i>', h, flags=_re.I)
        h = _re.sub(r'<(?!/?(b|i|u|br|font|super|sub)\b)[^>]+>', '', h, flags=_re.I)
        h = _re.sub(r'&nbsp;', ' ', h)
        h = _re.sub(r'&ndash;', '\u2013', h)
        h = _re.sub(r'&mdash;', '\u2014', h)
        h = _re.sub(r'&amp;', '&', h)
        h = _re.sub(r'[ \t]+', ' ', h)
        h = _re.sub(r'(\s*<br/>\s*){3,}', '<br/><br/>', h)
        h = _re.sub(r'&(?!(amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+)\b)', '&amp;', h)
        return h.strip()

    page_w = 170 * mm

    title_para = Paragraph('MOLECULAR DIAGNOSTIC SECTION', title_style)

    band_tbl = Table([[Paragraph(item.test.name.upper(), band_style)]],
                     colWidths=[page_w])
    band_tbl.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.9, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))

    kv_rows = []
    for label, val in [('SPECIMEN:', specimen),
                       ('RESULT:', result_type),
                       ('VIRAL LOAD:', viral_load)]:
        if val:
            kv_rows.append([
                Paragraph(f'<b>{label}</b>', kv_label),
                Paragraph(str(val), kv_val),
            ])
    kv_tbl = Table(kv_rows, colWidths=[30 * mm, 140 * mm])
    kv_tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))

    flow = [title_para, band_tbl, kv_tbl]

    def _section(title, body_html):
        cleaned = _clean(body_html)
        if not cleaned:
            return
        flow.append(Spacer(1, 2 * mm))
        flow.append(HRFlowable(width='100%', thickness=0.4,
                               color=colors.HexColor('#adb5bd'),
                               spaceBefore=1, spaceAfter=2))
        flow.append(Paragraph(f'<u><b>{title}:</b></u>', section_head))
        flow.append(Spacer(1, 1))
        flow.append(Paragraph(cleaned, body_style))

    _section('Interpretation', interpretation)
    _section('Methodologies', methodology)
    _section('Comments', comments)

    empty = Table([['']], colWidths=[1])
    empty.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    return empty, flow, 0, 0
