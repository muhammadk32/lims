"""
Feature 3: Report with previous 2 results
- Q1=B: Show last 2 previous visits (3 columns total)
- Q2=B: Match by test NAME
- Q3=B: Skip tests that have no prior history
"""
import os

# ============================================================
# 1. New query helper — reports/queries.py
# ============================================================
qp = 'modules/reports/queries.py'
if not os.path.exists(qp):
    open(qp, 'w', encoding='utf-8').write('"""Report query helpers."""\n')

q = open(qp, encoding='utf-8').read()

if 'def get_previous_results' not in q:
    q += '''

# ============================================================
# Previous results lookup for patient
# ============================================================
def get_previous_results(patient_id, current_order_id, test_name, limit=2):
    """Return list of (date, value) for the last N prior results of this test.

    Match is by test name (case-insensitive). Only looks at orders
    older than current_order_id. Ordered newest first.
    """
    from modules.orders.models import Order, OrderItem, OrderStatus
    from modules.tests.models import Test
    from sqlalchemy import func

    if not test_name:
        return []

    rows = (
        db.session.query(
            Order.created_at.label('date'),
            OrderItem.result_value.label('value'),
        )
        .join(Order, OrderItem.order_id == Order.id)
        .join(Test, OrderItem.test_id == Test.id)
        .filter(Order.patient_id == patient_id)
        .filter(Order.id < current_order_id)
        .filter(Order.status.in_([OrderStatus.COMPLETED, OrderStatus.APPROVED]))
        .filter(func.lower(Test.name) == func.lower(test_name))
        .filter(OrderItem.result_value.isnot(None))
        .filter(OrderItem.result_value != '')
        .order_by(Order.id.desc())
        .limit(limit)
        .all()
    )

    return [(r.date, r.value) for r in rows]


def build_previous_map(patient_id, current_order_id, limit=2):
    """Build {test_name_lower: [(date, value), ...]} for all tests in current order.

    Only includes tests that have at least one prior result.
    """
    from modules.orders.models import Order, OrderItem, OrderStatus
    from modules.tests.models import Test
    from sqlalchemy import func

    order = db.session.get(Order, current_order_id)
    if not order:
        return {}, []

    # Collect every test name used in the current order (top-level + children)
    names = set()
    for item in order.top_level_items:
        if item.test:
            names.add(item.test.name)
        for ch in item.children:
            if ch.test:
                names.add(ch.test.name)

    result_map = {}
    date_labels = []

    for name in names:
        priors = get_previous_results(patient_id, current_order_id, name, limit)
        if priors:
            result_map[name.lower()] = priors

    # Build consistent date headers: use the most common order positions
    # Take dates from any test that has 2 priors
    for name, priors in result_map.items():
        for i, (d, _) in enumerate(priors):
            while len(date_labels) <= i:
                date_labels.append(None)
            if date_labels[i] is None:
                date_labels[i] = d
        break  # only first test is enough for labels

    return result_map, date_labels
'''
    open(qp, 'w', encoding='utf-8').write(q)
    print('OK  - reports/queries.py: get_previous_results + build_previous_map added')
else:
    print('SKIP - queries already has functions')


# Add db import if missing
if 'from extensions import db' not in q:
    q = open(qp, encoding='utf-8').read()
    if not q.lstrip().startswith('from extensions import db'):
        q = 'from extensions import db\n\n' + q
        open(qp, 'w', encoding='utf-8').write(q)
        print('OK  - queries.py: db imported')


# ============================================================
# 2. Update results_table.py — support previous columns
# ============================================================
rtp = 'modules/reports/pdf/results_table.py'
rt = open(rtp, encoding='utf-8').read()

# Replace the entire _results_table function with a version that accepts previous_map + date_labels
new_fn = '''def _results_table(order, previous_map=None, date_labels=None):
    """Results table with panel grouping + previous results columns.

    previous_map: {test_name_lower: [(date, value), ...]}
    date_labels:  [datetime, datetime]  — for column headers
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
    panel_sub_style = ParagraphStyle(
        'PanelSub', parent=styles['Normal'], fontSize=8.5,
        textColor=colors.HexColor('#212529'), leftIndent=10,
    )

    def fmt_date(d):
        try:
            return d.strftime('%d-%b-%y')
        except Exception:
            return '—'

    # Header row
    header_cells = [
        Paragraph('Test', header_style),
        Paragraph('Result', header_style),
    ]
    for d in date_labels:
        header_cells.append(Paragraph(fmt_date(d), header_style))
    header_cells += [
        Paragraph('Unit', header_style),
        Paragraph('Normal Range', header_style),
        Paragraph('Flag', header_style),
    ]
    data = [header_cells]

    abnormal_rows = []
    row_idx = 1

    def prev_values_for(name):
        """Return [v1, v2] list of previous values in order, padded with None."""
        priors = previous_map.get((name or '').lower(), [])
        out = []
        for i in range(n_prev):
            if i < len(priors):
                out.append(priors[i][1])
            else:
                out.append(None)
        return out

    for item in order.top_level_items:
        if item.has_children:
            panel_cells = [
                Paragraph(f'▸ {item.test.name}', panel_header_style),
                Paragraph('', cell_style),
            ]
            panel_cells += [Paragraph('', cell_style)] * n_prev
            panel_cells += [
                Paragraph('', cell_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
            ]
            data.append(panel_cells)
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

                row = [
                    Paragraph(child.test.name, panel_sub_style),
                    Paragraph(child.result_value or '—', cell_style),
                ]
                for pv in prev_values_for(child.test.name):
                    row.append(Paragraph(pv or '—', cell_prev))
                row += [
                    Paragraph(child.test.unit or '—', cell_style),
                    Paragraph(child.test.normal_range or '—', cell_style),
                    Paragraph(flag_text, cell_style),
                ]
                data.append(row)
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

            row = [
                Paragraph(item.test.name, cell_bold),
                Paragraph(item.result_value or '—', cell_style),
            ]
            for pv in prev_values_for(item.test.name):
                row.append(Paragraph(pv or '—', cell_prev))
            row += [
                Paragraph(item.test.unit or '—', cell_style),
                Paragraph(item.test.normal_range or '—', cell_style),
                Paragraph(flag_text, cell_style),
            ]
            data.append(row)
            row_idx += 1

    # Column widths — adapt to presence of previous columns
    if n_prev > 0:
        col_widths = [55 * mm, 22 * mm]
        col_widths += [22 * mm] * n_prev
        col_widths += [18 * mm, 35 * mm, 18 * mm]
    else:
        col_widths = [65 * mm, 30 * mm, 25 * mm, 35 * mm, 25 * mm]

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
'''

# Replace the existing function
idx = rt.find('def _results_table')
if idx == -1:
    print('WARN - _results_table not found in results_table.py')
else:
    end = rt.find(chr(10) + 'def ', idx + 1)
    if end == -1:
        end = len(rt)
    rt = rt[:idx] + new_fn + '\n\n' + rt[end:]
    open(rtp, 'w', encoding='utf-8').write(rt)
    print('OK  - results_table.py updated with previous columns')


# ============================================================
# 3. Update generator.py — build previous_map and pass it
# ============================================================
gp = 'modules/reports/pdf/generator.py'
g = open(gp, encoding='utf-8').read()

old_call = '''    results_table, abnormal_count = _results_table(order)
    story.append(results_table)'''

new_call = '''    # Build previous-results map for this patient (last 2 prior visits)
    previous_map = {}
    date_labels = []
    try:
        from modules.reports.queries import build_previous_map
        previous_map, date_labels = build_previous_map(order.patient_id, order.id, limit=2)
    except Exception as e:
        print(f'[pdf.generator] previous_map failed: {e}')

    results_table, abnormal_count = _results_table(
        order,
        previous_map=previous_map,
        date_labels=date_labels,
    )
    story.append(results_table)'''

if old_call in g:
    g = g.replace(old_call, new_call, 1)
    open(gp, 'w', encoding='utf-8').write(g)
    print('OK  - generator.py: passes previous_map to results_table')
else:
    print('WARN - generator call anchor not found')


print()
print('=' * 55)
print('Done. Restart Flask, then view any PDF report for a')
print('patient who has 2+ prior visits with the same test.')
print('=' * 55)
