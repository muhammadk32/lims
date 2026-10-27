"""Label PDF builders — A4 grid or single-label-per-page."""
import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Image,
    PageBreak, Spacer,
)

from .barcode_gen import code128_png, sample_suffix


# ---- A4 grid geometry (Avery L7159-ish: 3 cols x 8 rows) ----
GRID_COLS = 3
GRID_ROWS = 8
GRID_LEFT = 5 * mm
GRID_TOP = 12 * mm
GRID_GAP_X = 2 * mm
GRID_GAP_Y = 2 * mm
PAGE_W, PAGE_H = A4
LABEL_W = (PAGE_W - 2 * GRID_LEFT - (GRID_COLS - 1) * GRID_GAP_X) / GRID_COLS
LABEL_H = (PAGE_H - 2 * GRID_TOP - (GRID_ROWS - 1) * GRID_GAP_Y) / GRID_ROWS


def _label_cell(order, item, barcode_data, idx):
    """Compact label sized for a 2x1 inch page."""
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Table, TableStyle, Paragraph, Image
    from .barcode_gen import code128_png

    code_style = ParagraphStyle('LblCode', fontSize=8, leading=9,
                                fontName='Helvetica-Bold', alignment=1)
    name_style = ParagraphStyle('LblName', fontSize=6, leading=7, alignment=0)
    meta_style = ParagraphStyle('LblMeta', fontSize=7, leading=8, alignment=0)

    buf = code128_png(barcode_data, module_height=6.0, module_width=0.22, quiet_zone=1.0)
    img_w = float(44 * mm)   # fits inside 2in (50.8mm) minus margins
    img_h = float(7 * mm)
    img = Image(buf, width=img_w, height=img_h)
    img.hAlign = 'CENTER'

    stamp = datetime.utcnow().strftime('%d-%b-%Y  %I:%M %p')

    t = getattr(item, 'test', None)
    
    # Combine everything: item sample, test sample, and test name
    t = getattr(item, 'test', None)
    # Check if ANY test in the order is a URINE test
    is_urine_order = False
    for o_item in getattr(order, 'top_level_items', []):
        t_name = str(getattr(getattr(o_item, 'test', None), 'name', '') or '').upper()
        t_type = str(getattr(getattr(o_item, 'test', None), 'sample_type', '') or '').upper()
        i_type = str(getattr(o_item, 'sample_type', '') or '').upper()
        if 'URINE' in t_name or 'URINE' in t_type or 'URINE' in i_type:
            is_urine_order = True
            break

    parts = [
        [img],
        [Paragraph(barcode_data, code_style)],
        [Paragraph(
            '' if is_urine_order
               else (order.patient.full_name or ''),
            name_style,
        )],
        [Paragraph(stamp, meta_style)],
    ]
    content = Table(parts, colWidths=[img_w])
    content.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (0, 1), (0, 1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return content


def _collect_items(order):
    """One label per distinct sample_type specimen.
    Panels expand to children, then group by specimen type.
    Returns list of (item, barcode_data, specimen_label, test_names)."""
    flat = []
    for top in order.top_level_items:
        if top.has_children:
            for child in top.children:
                flat.append(child)
        else:
            flat.append(top)

    groups = {}
    for it in flat:
        stype = (getattr(it, 'sample_type', None) or '').strip() or 'SPECIMEN'
        key = stype.upper()
        groups.setdefault(key, {'sample_type': stype, 'items': []})['items'].append(it)

    items = []
    for idx, (key, g) in enumerate(sorted(groups.items())):
        suffix = '' if len(groups) == 1 else '-' + sample_suffix(idx)
        barcode_data = order.order_code + suffix
        test_names = [it.test.name if it.test else '' for it in g['items']]
        items.append((g['items'][0], barcode_data, g['sample_type'], test_names))
    return items


def _build_pdf(order):
    """One label per page, 2x1 inch page."""
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, PageBreak

    PAGE_W = 50.8 * mm
    PAGE_H = 25.4 * mm
    PAD = 1.5 * mm

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=(PAGE_W, PAGE_H),
        leftMargin=PAD, rightMargin=PAD,
        topMargin=PAD, bottomMargin=PAD,
        title=f'Labels — {order.order_code}',
    )
    items = _collect_items(order)
    story = []
    for i, (it, code, _spec, _tests) in enumerate(items):
        if i > 0:
            story.append(PageBreak())
        story.append(_label_cell(order, it, code, i))
    doc.build(story)
    buf.seek(0)
    return buf


def build_grid_pdf(order):
    return _build_pdf(order)


def build_single_pdf(order):
    return _build_pdf(order)
