"""Single source of truth for report block styling.

Every department's report block MUST import from here so that all
reports (chemistry, hematology, urinalysis, culture, molecular) share
the same outer border, inner grid, and corner radius.
"""

from reportlab.lib import colors


# --- Universal border palette ---
OUTER_BORDER_COLOR = colors.black
OUTER_BORDER_WIDTH = 1.2
INNER_GRID_COLOR = colors.HexColor('#adb5bd')
INNER_GRID_WIDTH = 0.5
CORNER_RADIUS = 8


def apply_block_style(table, extra_cmds=None, rounded=True):
    """Apply the standard ADAM Labs block look to a ReportLab Table.

    - Rounded outer BOX (black, 1.2pt)
    - Grey inner GRID (0.5pt)
    - Standard cell padding
    - Any extra commands from `extra_cmds` are appended (e.g. BACKGROUND, SPAN)

    Usage:
        t = Table(data)
        apply_block_style(t)
    """
    from reportlab.platypus import TableStyle

    cmds = [
        ('GRID', (0, 0), (-1, -1), INNER_GRID_WIDTH, INNER_GRID_COLOR),
        ('BOX', (0, 0), (-1, -1), OUTER_BORDER_WIDTH, OUTER_BORDER_COLOR),
    ]
    if rounded:
        cmds.append(('ROUNDEDCORNERS', [CORNER_RADIUS]*4))

    cmds.extend([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ])

    if extra_cmds:
        cmds.extend(extra_cmds)

    table.setStyle(TableStyle(cmds))
    return table


def resolve_section_titles(test, default_label=''):
    """Return list of title strings to render for a test's section banner.

    Modes:
      A -> [report_name]              (report name replaces default)
      B -> [category REPORT]           (category only)
      C -> [report_name, category REPORT]  (both, deduped)
      D -> []                          (nothing)
    Falls back to default_label if test/category not usable.
    """
    if test is None:
        return [default_label] if default_label else []

    rn = (getattr(test, 'report_name', '') or '').strip().upper()
    mode = (getattr(test, 'report_name_mode', 'C') or 'C').upper()

    cat = ''
    cr = getattr(test, 'category_ref', None)
    if cr:
        cat = ((getattr(cr, 'name', '') or '').strip()).upper()
    cat_label = (cat + ' REPORT') if cat else ''

    if mode == 'D':
        return []
    if mode == 'A':
        return [rn] if rn else ([default_label] if default_label else [])
    if mode == 'B':
        return [cat_label] if cat_label else ([default_label] if default_label else [])
    if mode == 'C':
        out = []
        if rn:
            out.append(rn)
        if cat_label and cat_label != rn and cat_label not in out:
            out.append(cat_label)
        if not out and default_label:
            out.append(default_label)
        # dedupe preserving order
        seen = set()
        out = [x for x in out if not (x in seen or seen.add(x))]
        return out
    return [cat_label or default_label] if (cat_label or default_label) else []
