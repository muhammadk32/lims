"""Results table — grouped by panel, with abnormal highlighting."""
import re
from reportlab.lib import colors
from modules.tests.ranges import (
    resolve_range_for_order as _rrfo_raw,
    critical_for_order as _cfo,
    evaluate_for_order as _efo,
    pick_range_for_patient as _prfp,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Table, TableStyle, HRFlowable, Spacer

from .branding import _get_lab, _hex
from .culture_table import _culture_block as _culture_flowables



def _rrfo(test, order):
    """Wrap resolve_range_for_order: strip all HTML, return plain text.

    Handles the common case where the stored range is a Word-paste blob:
    - Truncated HTML fragments like '<p class="MsoNormal" ...>Interprer'
    - Full HTML with prose + numbers
    - Clean text ranges like '10 - 140'

    Strategy:
      1. If raw is already a plain range, return it.
      2. If raw is HTML/prose garbage, try to extract 'num - num' pattern.
      3. If nothing usable found, return '-'.
    """
    try:
        raw = _rrfo_raw(test, order)
    except Exception:
        return '-'
    if not raw:
        return '-'
    import re as _r
    s = str(raw).strip()

    # Fast path: already a clean short range
    if len(s) <= 40 and not s.startswith('<') and _r.search(r'\d', s):
        s_clean = _r.sub(r'\s+', ' ', s).strip()
        return s_clean or '-'

    # Try to extract a numeric range from anywhere in the raw string first
    # (works even when HTML is truncated mid-tag)
    range_match = _r.search(r'\d+(?:\.\d+)?\s*[-–]\s*\d+(?:\.\d+)?', s)
    if range_match:
        return range_match.group(0).strip()

    # Fall back: strip HTML tags and inspect what's left
    stripped = _r.sub(r'<[^>]*>', '', s)
    stripped = _r.sub(r'<[^>]*$', '', stripped)
    stripped = stripped.replace('<', '').replace('>', '')
    stripped = _r.sub(r'\s+', ' ', stripped).strip()

    # If the stripped text contains prose markers or is truncated, it is junk
    junk_markers = (
        'Interprer', 'Interpretation', 'MsoNormal', 'font-',
        'color:', 'face=', 'style=',
    )
    if any(j.lower() in stripped.lower() for j in junk_markers):
        return '-'

    # Truncated HTML (started with <p but no </p>)
    if s.startswith('<') and '</' not in s:
        return '-'

    return stripped or '-'


def _sanitize_para(html):
    """Clean up HTML fragments that break reportlab's paragraph parser.

    - Removes <p> with only <br> inside
    - Strips trailing <br> before closing </p>
    - Collapses multiple consecutive <br> to one
    """
    if not html:
        return ''
    import re
    s = str(html)
    # empty <p>...</p> with only whitespace or brs
    s = re.sub(r'<p>\s*(?:<br\s*/?>\s*)*</p>', '', s, flags=re.I)
    # brs before </p>
    s = re.sub(r'(?:<br\s*/?>\s*)+</p>', '</p>', s, flags=re.I)
    # brs right after <p>
    s = re.sub(r'<p>\s*(?:<br\s*/?>\s*)+', '<p>', s, flags=re.I)
    # collapse runs
    s = re.sub(r'(?:<br\s*/?>\s*){3,}', '<br/>', s, flags=re.I)
    return s.strip()

def _flag_result(normal_range, result_value):
    """Return 'normal' | 'abnormal' | 'unknown'."""
    try:
        from modules.results.validators import check_result
        return check_result(normal_range, result_value)
    except Exception:
        return 'unknown'


def _collect_histopath(bucket, item, order):
    """Render a histopathology / cytology narrative block into bucket."""
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
    from ._shared_style import resolve_section_titles

    styles = getSampleStyleSheet()
    from modules.results.models import Result
    r = Result.query.filter_by(order_item_id=item.id).first()
    if r is None:
        return

    content_fields = [
        getattr(r, 'biopsy_no', None),
        getattr(r, 'clinical_history_html', None),
        getattr(r, 'histopath_specimen_html', None),
        getattr(r, 'gross_html', None),
        getattr(r, 'microscopic_html', None),
        getattr(r, 'immuno_stains_html', None),
        getattr(r, 'final_diagnosis_html', None),
        getattr(r, 'comments_html', None),
        getattr(r, 'notes', None),
    ]
    if not any(content_fields):
        return

    title_style = ParagraphStyle('HpTitle', parent=styles['Normal'],
                                 fontSize=10, fontName='Helvetica-Bold',
                                 textColor=colors.black)
    spec_style = ParagraphStyle('HpSpec', parent=styles['Normal'],
                                fontSize=9, fontName='Helvetica-Bold',
                                textColor=colors.black)
    lbl_style = ParagraphStyle('HpLbl', parent=styles['Normal'],
                               fontSize=7.5, fontName='Helvetica-Bold',
                               textColor=colors.black)
    body_style = ParagraphStyle('HpBody', parent=styles['Normal'],
                                fontSize=8, leading=10)

    def _clean(html):
        if not html:
            return ''
        h = str(html)
        return h.replace('\r\n', '<br/>').replace('\n', '<br/>')

    bucket.append(Spacer(1, 3 * mm))

    _titles = resolve_section_titles(item.test, default_label='')
    for _t in _titles:
        _hdr = Table([[Paragraph(_t, title_style)]], colWidths=[170 * mm])
        _hdr.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 1.2, colors.black),
            ('LINEBELOW', (0, 0), (-1, -1), 1.2, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ]))
        bucket.append(_hdr)
        bucket.append(Spacer(1, 3 * mm))

    _name_tbl = Table([[Paragraph(item.test.name, spec_style)]], colWidths=[170 * mm])
    _name_tbl.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
    ]))
    bucket.append(_name_tbl)
    bucket.append(Spacer(1, 2 * mm))

    rows = []
    if getattr(r, 'biopsy_no', None):
        rows.append([Paragraph('Biopsy/Cytology No:', lbl_style),
                     Paragraph(str(r.biopsy_no), body_style)])
    if getattr(r, 'clinical_history_html', None):
        rows.append([Paragraph('Clinical History / Pre Op Dx:', lbl_style),
                     Paragraph(_clean(r.clinical_history_html), body_style)])
    if getattr(r, 'histopath_specimen_html', None):
        rows.append([Paragraph('Specimen:', lbl_style),
                     Paragraph(_clean(r.histopath_specimen_html), body_style)])
    if getattr(r, 'gross_html', None):
        rows.append([Paragraph('Gross:', lbl_style),
                     Paragraph(_clean(r.gross_html), body_style)])
    if getattr(r, 'microscopic_html', None):
        rows.append([Paragraph('Microscopic Examination:', lbl_style),
                     Paragraph(_clean(r.microscopic_html), body_style)])
    if getattr(r, 'immuno_stains_html', None):
        rows.append([Paragraph('Immuno-Stains:', lbl_style),
                     Paragraph(_clean(r.immuno_stains_html), body_style)])
    if getattr(r, 'final_diagnosis_html', None):
        rows.append([Paragraph('Final Diagnosis / Opinion:', lbl_style),
                     Paragraph(_clean(r.final_diagnosis_html), body_style)])
    if getattr(r, 'comments_html', None):
        rows.append([Paragraph('Comments:', lbl_style),
                     Paragraph(_clean(r.comments_html), body_style)])
    if getattr(r, 'notes', None):
        rows.append([Paragraph('Notes:', lbl_style),
                     Paragraph(_clean(r.notes), body_style)])

    if rows:
        t = Table(rows, colWidths=[45 * mm, 125 * mm])
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOX', (0, 0), (-1, -1), 1.0, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#adb5bd')),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))
        bucket.append(t)

    bucket.append(Spacer(1, 3 * mm))

def _results_table(order, previous_map=None, date_labels=None, items_override=None, content_width=None):
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
    def fmt_date(d):
        try:
            return d.strftime('%d-%b-%y')
        except Exception:
            return '-'


    header_cells = [
        Paragraph('Test', header_style),
        Paragraph(order.created_at.strftime('%d-%b-%y') if order.created_at else 'Result', header_style),
        Paragraph('Unit', header_style),
        Paragraph('Normal Range', header_style),
    ]
    for d in date_labels:
        header_cells.append(Paragraph(fmt_date(d), header_style))

    _last_test_id = None
    _sep_rows = []
    data = []
    notes_flowables = []
    notes_row_indices = []
    abnormal_rows = []
    critical_rows = []
    row_idx = 0

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
        ab_rows = CultureAntibiotic.query.filter_by(order_item_id=item.id).all()

        # If antibiotic rows exist but Result parent is missing, render a synthetic Result
        # object so the culture table can still build (organism/specimen will be blank).
        if not r and ab_rows:
            class _SynthResult:
                # All culture fields the PDF block may reference
                culture_specimen = None
                culture_organism = None
                culture_direct_text = None
                culture_direct_note = None
                culture_zn_text = None
                culture_zn_note = None
                culture_gram_text = None
                culture_gram_note = None
                culture_comments_dd = None
                culture_comments_txt = None
                culture_bacteria_ids = None
                culture_no_sensitive = None
                culture_no_growth = None
                culture_mixed_growth = None
                culture_colony_count = None
                culture_incubation = None
                culture_notes = None
                entered_at = None
                result_value = None
                def __getattr__(self, name):
                    # Any other unknown attribute -> None instead of crashing
                    return None
            r = _SynthResult()

        if not r:
            # No result and no antibiotics — show the pending block.
            from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            from reportlab.lib.units import mm
            st = getSampleStyleSheet()
            hdr = ParagraphStyle('CultHdr', parent=st['Normal'],
                                 fontSize=10, fontName='Helvetica-Bold',
                                 textColor=colors.white)
            pending = ParagraphStyle('CultP', parent=st['Normal'], fontSize=9)
            tbl = Table(
                [[Paragraph('CULTURE & SENSITIVITY', hdr)],
                 [Paragraph(f'<b>{item.test.name}</b> — results pending.', pending)]],
                colWidths=[170 * mm]
            )
            tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('BACKGROUND', (0, 1), (-1, 1), colors.white),
                ('BOX', (0, 0), (-1, -1), 1.0, colors.black),
                ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            bucket.append(tbl)
            bucket.append(Spacer(1, 4 * mm))
            return
        try:
            for f in _culture_flowables(item, r, ab_rows):
                bucket.append(f)
        except Exception as e:
            print(f'[culture_table] failed: {e}')
            import traceback; traceback.print_exc()

    def _collect_pcr_details(bucket, item, order_):
        # Hard gate: this function must only run for PCR / molecular tests
        _fmt = (getattr(getattr(item, 'test', None), 'result_format', '') or '').lower()
        if _fmt not in ('pcr', 'pcr_quant', 'molecular'):
            return
        from modules.results.models import Result
        r = Result.query.filter_by(order_item_id=item.id).first()
        tpl = None
        try:
            from modules.tests.models import PcrTemplate
            tpl = PcrTemplate.query.filter_by(test_id=item.test_id).first()
        except Exception:
            tpl = None

        def _pick(a, b):
            return _sanitize_para(a if a else (b if tpl else None))

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
        from ._shared_style import resolve_section_titles as _rst
        _mol_titles = _rst(getattr(item, 'test', None), default_label='MOLECULAR REPORT')
        for _mt in _mol_titles:
            _mol_hdr_tbl = Table([[Paragraph(_mt, mol_hdr_style)]],
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
        __slots__ = ('name', 'test', 'has_children', 'children', 'result_value', 'report_name', 'report_name_mode')
        def __init__(self, name, report_name='', report_name_mode='C'):
            self.name = name
            self.report_name = report_name
            self.report_name_mode = report_name_mode
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
                _with_headers.append(_SectionMarker(_cn, report_name=(getattr(_it.test, 'report_name', None) or ''), report_name_mode=(getattr(_it.test, 'report_name_mode', 'C') or 'C')))
        _with_headers.append(_it)

    _section_header_rows = []
    _section_hdr_row_indices = []
    _colhdr_rows = []
    _needs_colhdr = False  # default; will flip on for the first section

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
                (i.test.result_format or '').lower() not in ('pcr', 'pcr_quant', 'molecular', 'culture', 'culture_sensitivity', 'histopath', 'histopathology', 'histo')
                for i in _upcoming if getattr(i, 'test', None)
            )
            if not _has_printable:
                continue

            # Section title row — skip MOLECULAR (handled inside PCR blocks)
            _is_molecular_section = (item.name or '').strip().upper() == 'MOLECULAR'
            if not _is_molecular_section:
                _first_section_done = True
                
                # Add large white gap before a new Category Report (e.g., ROUTINE HEMATOLOGY)
                _gap = [Paragraph('', cell_style)] * (4 + n_prev)
                data.append(_gap)
                _mode = (item.report_name_mode or 'C').upper()
                _rn = (item.report_name or '').strip()
                _dept = (item.name or '').strip()
                _dept_title = (_dept.upper() + ' REPORT') if _dept else ''

                def _append_hdr(txt, style):
                    _row = [Paragraph(txt, style)]
                    _row += [Paragraph('', cell_style)] * (3 + n_prev)
                    data.append(_row)

                if _mode == 'D':
                    pass  # nothing
                elif _mode == 'A' and _rn:
                    _append_hdr(_rn.upper(), section_header_style)
                elif _mode == 'B' and _dept_title:
                    _append_hdr(_dept_title, section_header_style)
                elif _mode == 'C':
                    if _rn:
                        _append_hdr(_rn.upper(), section_header_style)
                    if _dept_title:
                        _append_hdr(_dept_title, cell_style)
                else:
                    if _dept_title:
                        _append_hdr(_dept_title, section_header_style)
                _section_header_rows.append(row_idx)
                row_idx += 1

            # Do NOT print column headers here. Wait for the first item to print them
            # so that panels can print their own name above the columns.
            _needs_colhdr = True
            continue

        if item.has_children:
            # Culture / PCR panels render via their dedicated block, not the numeric grid.
            _panel_fmt = (getattr(item.test, 'result_format', '') or '').lower()
            if _panel_fmt in ('culture', 'culture_sensitivity'):
                _collect_culture(notes_flowables, item, order)
                _last_test_id = item.test.id
                continue
            if _panel_fmt in ('pcr', 'pcr_quant', 'molecular'):
                _collect_pcr_details(notes_flowables, item, order)
                _last_test_id = item.test.id
                continue

            # Insert a gap row before this panel begins (unless it's the very first item)
            if _last_test_id is not None and _last_test_id != item.test.id:
                _gap = [Paragraph('', cell_style)] * (4 + n_prev)
                data.append(_gap)
                _sep_rows.append(row_idx)
                row_idx += 1
            _last_test_id = item.test.id


            panel_cells = [
                Paragraph('> ' + item.test.name, panel_header_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
            ]
            panel_cells += [Paragraph('', cell_style)] * n_prev
            data.append(panel_cells)
            row_idx += 1

            # Print column headers right below the panel name
            if '_needs_colhdr' in dir() and _needs_colhdr:
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
                _needs_colhdr = False

            # Group children by section — keep original order, group headings
            _seen = set()
            _ordered_sections = []
            for _ch in item.children:
                _sec = (getattr(_ch.test, 'panel_section', None) or '').strip()
                if _sec not in _seen:
                    _seen.add(_sec)
                    _ordered_sections.append(_sec)

            section_hdr_style = ParagraphStyle(
                'PanelSectionHdr', parent=styles['Normal'], fontSize=8.5,
                fontName='Helvetica-Bold', textColor=colors.HexColor('#212529'),
            )

            for _sec in _ordered_sections:
                # Emit section header row (spans all columns)
                if _sec:
                    _sh = [Paragraph(_sec, section_hdr_style)]
                    _sh += [Paragraph('', cell_style)] * (3 + n_prev)
                    data.append(_sh)
                    _section_hdr_row_indices.append(row_idx)
                    row_idx += 1

                for child in [c for c in item.children
                              if (getattr(c.test, 'panel_section', None) or '').strip() == _sec]:
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
                        Paragraph('' if child_is_pcr else _sanitize_para(_rrfo(child.test, order) or '-'), cell_style),
                    ]
                    for pv in prev_values_for(child.test.name):
                        row.append(Paragraph(pv or '-', cell_prev))
                    data.append(row)
                    row_idx += 1
                    _collect_note(notes_flowables, child.test, order)
                    _child_fmt = (child.test.result_format or '').lower() if child.test else ''
                    if _child_fmt in ('pcr', 'pcr_quant', 'molecular'):
                        _collect_pcr_details(notes_flowables, child, order)
                    if _child_fmt in ('culture', 'culture_sensitivity'):
                        _collect_culture(notes_flowables, child, order)
        else:
            flag, _crit = _efo(item.test, item.result_value, order)
            if flag == 'abnormal':
                abnormal_rows.append(row_idx)
                if _crit:
                    critical_rows.append(row_idx)

            is_pcr = (item.test.result_format or '').lower() in ('pcr', 'pcr_quant', 'molecular')
            is_culture = (item.test.result_format or '').lower() in ('culture', 'culture_sensitivity')
            is_histopath = (item.test.result_format or '').lower() in ('histopath', 'histopathology', 'histo')

            if is_culture:
                _collect_culture(notes_flowables, item, order)
            elif is_pcr:
                _collect_pcr_details(notes_flowables, item, order)
            elif is_histopath:
                _collect_histopath(notes_flowables, item, order)
            else:
                # Spacing row between different tests
                if _last_test_id is not None and _last_test_id != item.test.id:
                    _sep = [Paragraph('', cell_style)] * (4 + n_prev)
                    data.append(_sep)
                    _sep_rows.append(row_idx)
                    row_idx += 1
                _last_test_id = item.test.id

                # Force a block break for every new test
                if _last_test_id is not None and _last_test_id != item.test.id:
                    _sep = [Paragraph('', cell_style)] * (4 + n_prev)
                    data.append(_sep)
                    _sep_rows.append(row_idx)
                    row_idx += 1
                _last_test_id = item.test.id

                # Print column headers right before the first flat test row
                if '_needs_colhdr' in dir() and _needs_colhdr:
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
                    _needs_colhdr = False

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

    # Column widths — scale to fill the available content width.
    # Fallback to A4 content width (170mm) if not supplied.
    _avail = content_width if content_width else (170 * mm)
    if n_prev > 0:
        # TEST | RESULT | UNIT | REFERENCE | prev1 | prev2 | ...
        # Base 4 columns take 75% of width, prev columns share remaining 25%.
        _base = _avail * 0.75
        _prev_total = _avail * 0.25
        _prev_w = _prev_total / max(n_prev, 1)
        # Split base 75% into TEST(40%) RESULT(20%) UNIT(15%) REF(25%)
        col_widths = [
            _base * 0.40,
            _base * 0.20,
            _base * 0.15,
            _base * 0.25,
        ]
        col_widths += [_prev_w] * n_prev
    else:
        # TEST(40%) RESULT(20%) UNIT(15%) REF(25%) = 100% of content width
        col_widths = [
            _avail * 0.40,
            _avail * 0.20,
            _avail * 0.15,
            _avail * 0.25,
        ]

    if len(data) <= 1:
        empty = Table([['']], colWidths=[1])
        empty.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        # For culture / PCR tests, data[] is empty but notes_flowables holds the report body.
        # Return an empty table + those flowables so the caller renders them.
        return empty, notes_flowables, len(abnormal_rows), len(critical_rows)

    # --- SPLIT INTO SEPARATE BLOCKS (one per test) ---
    # Build a set of "first row of a new test" indices:
    # only result rows that follow a section-header block or a previous test's last row.
    if _sep_rows:
        blocks = []
        start_idx = 0
        for sep_idx in _sep_rows:
            # Build a table up to the separator row
            chunk_data = data[start_idx:sep_idx]
            if chunk_data:
                t = Table(chunk_data, colWidths=col_widths, repeatRows=0)
                zebra_cmds = [('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]
                for _i in range(len(chunk_data)):
                    if _i % 2 == 1:
                        zebra_cmds.append(('BACKGROUND', (0, _i), (-1, _i), colors.HexColor('#f8f9fa')))
                zebra_cmds.extend([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#adb5bd')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')), # Header row background
                    ('BOX', (0, 0), (-1, -1), 1.2, colors.black),
                    ('ROUNDEDCORNERS', [8, 8, 8, 8]),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ])
                for _r in _section_header_rows:
                    if start_idx <= _r < sep_idx:
                        local_r = _r - start_idx
                        zebra_cmds.extend([
                            ('BACKGROUND', (0, local_r), (-1, local_r), colors.white),
                            ('SPAN', (0, local_r), (-1, local_r)),
                            ('LINEBELOW', (0, local_r), (-1, local_r), 0, colors.white),
                        ])
                t.setStyle(TableStyle(zebra_cmds))
                blocks.append(t)
                blocks.append(Spacer(1, 25))
            start_idx = sep_idx + 1

        # Last block
        chunk_data = data[start_idx:]
        if chunk_data:
            t = Table(chunk_data, colWidths=col_widths, repeatRows=0)
            zebra_cmds = [('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]
            for _i in range(len(chunk_data)):
                if _i % 2 == 1:
                    zebra_cmds.append(('BACKGROUND', (0, _i), (-1, _i), colors.HexColor('#f8f9fa')))
            zebra_cmds.extend([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#adb5bd')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')), # Header row background
                ('BOX', (0, 0), (-1, -1), 1.2, colors.black),
                ('ROUNDEDCORNERS', [8, 8, 8, 8]),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ])
            for _r in _section_header_rows:
                if start_idx <= _r:
                    local_r = _r - start_idx
                    zebra_cmds.extend([
                        ('BACKGROUND', (0, local_r), (-1, local_r), colors.white),
                        ('SPAN', (0, local_r), (-1, local_r)),
                    ])
            t.setStyle(TableStyle(zebra_cmds))
            blocks.append(t)

        return blocks, notes_flowables, len(abnormal_rows), len(critical_rows)

    # Fallback if no separators were found (just one block)
    t = Table(data, colWidths=col_widths, repeatRows=0)

    style = [
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#adb5bd')),
        ('BOX', (0, 0), (-1, -1), 1.2, colors.black), # Outer border
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]

    # Section title rows: black underline above + below, full span
    # Per-test separators: 60pt blank gap with no borders
    for _r in _sep_rows:
        style.append(('SPAN', (0, _r), (-1, _r)))
        style.append(('BACKGROUND', (0, _r), (-1, _r), colors.white))
        style.append(('LINEBELOW', (0, _r), (-1, _r), 0, colors.white))
        style.append(('LINEABOVE', (0, _r), (-1, _r), 0, colors.white))
        style.append(('INNERGRID', (0, _r), (-1, _r), 0, colors.white))
        style.append(('TOPPADDING', (0, _r), (-1, _r), 0))
        style.append(('BOTTOMPADDING', (0, _r), (-1, _r), 60))

    for _r in _section_header_rows:
        # Thick separator ABOVE section header (marks boundary of previous test)
        style.append(('LINEABOVE', (0, _r), (-1, _r), 2.0, colors.black))
        style.append(('LINEBELOW', (0, _r), (-1, _r), 1.2, colors.black))
        style.append(('BACKGROUND', (0, _r), (-1, _r), colors.white))
        style.append(('SPAN', (0, _r), (-1, _r)))

    # Panel sub-section header rows (grey background, spans all columns)
    for _r in _section_hdr_row_indices:
        style.append(('SPAN', (0, _r), (-1, _r)))
        style.append(('BACKGROUND', (0, _r), (-1, _r), colors.HexColor('#dee2e6')))
        style.append(('LINEBELOW', (0, _r), (-1, _r), 0.5, colors.black))

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

    from ._shared_style import resolve_section_titles
    _pcr_titles = resolve_section_titles(item.test, default_label='MOLECULAR DIAGNOSTIC SECTION')
    # Render every title as a separate row in the band table
    _band_rows = []
    for _t in _pcr_titles:
        _band_rows.append([Paragraph(_t, band_style)])
    if not _band_rows:
        _band_rows = [[Paragraph('', band_style)]]
    _band_label = item.test.name.upper() if item.test and item.test.name else ''
    _band_rows.append([Paragraph(_band_label, band_style)])
    band_tbl = Table(_band_rows, colWidths=[page_w])
    title_para = Spacer(1, 0)
    from ._shared_style import apply_block_style
    apply_block_style(band_tbl, extra_cmds=[
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ])

    kv_rows = []
    for label, val in [('SPECIMEN:', specimen),
                       ('RESULT:', result_type),
                       ('VIRAL LOAD:', viral_load)]:
        if val:
            kv_rows.append([
                Paragraph(f'<b>{label}</b>', kv_label),
                Paragraph(str(val), kv_val),
            ])
    # If no specimen / result / viral load was entered, show a pending notice
    if kv_rows:
        kv_tbl = Table(kv_rows, colWidths=[30 * mm, 140 * mm])
        kv_tbl.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        flow = [title_para, band_tbl, kv_tbl]
    else:
        # No result entered — render a pending notice under the band title
        pending_style = ParagraphStyle(
            'PendingPcr', parent=styles['Normal'],
            fontSize=9, textColor=colors.HexColor('#6c757d'),
            leftIndent=6, spaceBefore=4,
        )
        pending_para = Paragraph(
            f'<i>{item.test.name} — results pending (no specimen/result entered yet).</i>',
            pending_style,
        )
        flow = [title_para, band_tbl, pending_para]

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
