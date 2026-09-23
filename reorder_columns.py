# Reorder columns + remove Flag
p = 'modules/reports/pdf/results_table.py'
s = open(p, encoding='utf-8').read()

# 1. Reorder header row — current date, Unit, Normal Range, then prev dates, no Flag
old_header = """    header_cells = [
        Paragraph('Test', header_style),
        Paragraph(order.created_at.strftime('%d-%b-%y') if order.created_at else 'Result', header_style),
    ]
    for d in date_labels:
        header_cells.append(Paragraph(fmt_date(d), header_style))
    header_cells += [
        Paragraph('Unit', header_style),
        Paragraph('Normal Range', header_style),
        Paragraph('Flag', header_style),
    ]
    data = [header_cells]"""

new_header = """    header_cells = [
        Paragraph('Test', header_style),
        Paragraph(order.created_at.strftime('%d-%b-%y') if order.created_at else 'Result', header_style),
        Paragraph('Unit', header_style),
        Paragraph('Normal Range', header_style),
    ]
    for d in date_labels:
        header_cells.append(Paragraph(fmt_date(d), header_style))
    data = [header_cells]"""

if old_header in s:
    s = s.replace(old_header, new_header, 1)
    print('OK  - header reordered, Flag removed')

# 2. Panel header row — adjust cell count
old_panel = """            panel_cells = [
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
            row_idx += 1"""

new_panel = """            panel_cells = [
                Paragraph(f'▸ {item.test.name}', panel_header_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
            ]
            panel_cells += [Paragraph('', cell_style)] * n_prev
            data.append(panel_cells)
            row_idx += 1"""

if old_panel in s:
    s = s.replace(old_panel, new_panel, 1)
    print('OK  - panel header row adjusted')

# 3. Child rows — reorder: name, value, unit, range, then prev
old_child = """                row = [
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
                row_idx += 1"""

new_child = """                row = [
                    Paragraph(child.test.name, panel_sub_style),
                    Paragraph(child.result_value or '—', cell_style),
                    Paragraph(child.test.unit or '—', cell_style),
                    Paragraph(child.test.normal_range or '—', cell_style),
                ]
                for pv in prev_values_for(child.test.name):
                    row.append(Paragraph(pv or '—', cell_prev))
                data.append(row)
                row_idx += 1"""

if old_child in s:
    s = s.replace(old_child, new_child, 1)
    print('OK  - child row reordered')

# 4. Standalone rows — same treatment
old_standalone = """            row = [
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
            row_idx += 1"""

new_standalone = """            row = [
                Paragraph(item.test.name, cell_bold),
                Paragraph(item.result_value or '—', cell_style),
                Paragraph(item.test.unit or '—', cell_style),
                Paragraph(item.test.normal_range or '—', cell_style),
            ]
            for pv in prev_values_for(item.test.name):
                row.append(Paragraph(pv or '—', cell_prev))
            data.append(row)
            row_idx += 1"""

if old_standalone in s:
    s = s.replace(old_standalone, new_standalone, 1)
    print('OK  - standalone row reordered')

# 5. Column widths — reflect new order
old_widths = """    if n_prev > 0:
        col_widths = [55 * mm, 22 * mm]
        col_widths += [22 * mm] * n_prev
        col_widths += [18 * mm, 35 * mm, 18 * mm]
    else:
        col_widths = [65 * mm, 30 * mm, 25 * mm, 35 * mm, 25 * mm]"""

new_widths = """    if n_prev > 0:
        col_widths = [55 * mm, 22 * mm, 18 * mm, 35 * mm]
        col_widths += [22 * mm] * n_prev
    else:
        col_widths = [65 * mm, 30 * mm, 25 * mm, 35 * mm]"""

if old_widths in s:
    s = s.replace(old_widths, new_widths, 1)
    print('OK  - column widths adjusted')

open(p, 'w', encoding='utf-8').write(s)
print()
print('=' * 50)
print('Done. Restart Flask and reload the PDF.')
print('=' * 50)
