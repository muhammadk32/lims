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
    """Compact label: big barcode, order code, patient name, date."""
    name_style = ParagraphStyle('LblName', fontSize=10, leading=12,
                                fontName='Helvetica-Bold', alignment=1)
    code_style = ParagraphStyle('LblCode', fontSize=12, leading=14,
                                fontName='Helvetica-Bold', alignment=1)
    meta_style = ParagraphStyle('LblMeta', fontSize=8, leading=10,
                                alignment=1)

    bcode_buf = code128_png(
        barcode_data,
        module_height=16.0,
        module_width=0.30,
        quiet_zone=1.0,
    )
    img_w = LABEL_W - 12 * mm
    img_h = 18 * mm
    img = Image(bcode_buf, width=img_w, height=img_h)
    img.hAlign = 'CENTER'

    parts = [
        img,
        Paragraph(order.order_code, code_style),
        Paragraph(order.patient.full_name, name_style),
        Paragraph(datetime.utcnow().strftime('%d-%b-%Y %H:%M'), meta_style),
    ]

    inner = Table([[p] for p in parts], colWidths=[LABEL_W - 4 * mm])
    inner.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))

    outer = Table([[inner]], colWidths=[LABEL_W], rowHeights=[LABEL_H])
    outer.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.3, colors.HexColor('#adb5bd')),
        ('LEFTPADDING', (0, 0), (-1, -1), 2 * mm),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2 * mm),
        ('TOPPADDING', (0, 0), (-1, -1), 3 * mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3 * mm),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return outer

def _collect_items(order):
    """Flat list of (item, barcode_data) — panels expand to children with letter suffix."""
    items = []
    idx = 0
    for top in order.top_level_items:
        if top.has_children:
            # Panel: one label per child, using A/B/C suffix
            for child in top.children:
                idx += 1
                sfx = sample_suffix(idx - 1)
                items.append((child, order.order_code))
        else:
            idx += 1
            sfx = sample_suffix(idx - 1)
            items.append((top, order.order_code))
    return items


def build_grid_pdf(order):
    """A4 sheet with multiple labels per page."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=GRID_LEFT, rightMargin=GRID_LEFT,
        topMargin=GRID_TOP, bottomMargin=GRID_TOP,
        title=f'Labels — {order.order_code}',
    )

    items = _collect_items(order)
    cells = [_label_cell(order, item, code, i) for i, (item, code) in enumerate(items)]

    # Fill a rectangle of GRID_COLS x GRID_ROWS
    grid = []
    row = []
    for cell in cells:
        row.append(cell)
        if len(row) == GRID_COLS:
            grid.append(row)
            row = []
    if row:
        while len(row) < GRID_COLS:
            row.append('')
        grid.append(row)

    story = []
    story.append(Table(grid,
                       colWidths=[LABEL_W] * GRID_COLS,
                       rowHeights=[LABEL_H] * len(grid)))
    doc.build(story)
    buf.seek(0)
    return buf


def build_single_pdf(order):
    """One label per page — for thermal label printers."""
    buf = io.BytesIO()
    # Label printer sizes vary; use 100x50 mm as a sane default
    label_size = (100 * mm, 50 * mm)
    doc = SimpleDocTemplate(
        buf, pagesize=label_size,
        leftMargin=4 * mm, rightMargin=4 * mm,
        topMargin=3 * mm, bottomMargin=3 * mm,
        title=f'Labels — {order.order_code}',
    )

    items = _collect_items(order)
    story = []
    for i, (item, code) in enumerate(items):
        if i > 0:
            story.append(PageBreak())
        story.append(_label_cell(order, item, code, i))
    doc.build(story)
    buf.seek(0)
    return buf
