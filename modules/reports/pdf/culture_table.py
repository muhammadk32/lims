"""Culture & Sensitivity - ADAM microbiology report layout."""
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle


def _plain(txt):
    import re
    if not txt:
        return ""
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = re.sub(r"&nbsp;", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def _culture_block(item, result, ab_rows):
    styles = getSampleStyleSheet()
    border = colors.HexColor("#212529")
    grey_hd = colors.HexColor("#e9ecef")

    title_style = ParagraphStyle("CulTitle", parent=styles["Normal"],
        fontSize=10, fontName="Helvetica-Bold", alignment=1, spaceAfter=4)
    label_style = ParagraphStyle("CulLabel", parent=styles["Normal"],
        fontSize=8, fontName="Helvetica-Bold")
    body_style = ParagraphStyle("CulBody", parent=styles["Normal"],
        fontSize=8, leading=11)
    group_style = ParagraphStyle("CulGroup", parent=styles["Normal"],
        fontSize=7.5, fontName="Helvetica-Bold", textColor=colors.HexColor("#0d6efd"))
    med_style = ParagraphStyle("CulMed", parent=styles["Normal"], fontSize=8)
    sir_style = ParagraphStyle("CulSIR", parent=styles["Normal"],
        fontSize=8, fontName="Helvetica-Bold", alignment=1)
    note_style = ParagraphStyle("CulNote", parent=styles["Normal"],
        fontSize=8, leading=11)
    hdr_style = ParagraphStyle("CulHdr", parent=styles["Normal"],
        fontSize=7.5, fontName="Helvetica-Bold", alignment=1)

    out = []

    # Title
    t = Table([[Paragraph("MICROBIOLOGY REPORT", title_style)]], colWidths=[100*mm])
    t.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.8, border),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    out.append(t)
    out.append(Spacer(1, 3*mm))

    # Specimen + Growth lines
    specimen = _plain(result.culture_specimen) or "-"
    body_rows = [[Paragraph("<b>SPECIMEN:</b>", label_style), Paragraph(specimen, body_style)]]

    growth_lines = []
    for g in (1, 2, 3):
        txt = _plain(getattr(result, "culture_growth_%d" % g, "") or "")
        if txt:
            growth_lines.append("CULTURE %d:  %s" % (g, txt))
    if growth_lines:
        body_rows.append([Paragraph("", label_style),
                          Paragraph("<br/>".join(growth_lines), body_style)])

    t2 = Table(body_rows, colWidths=[30*mm, 140*mm])
    t2.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 1),
        ("BOTTOMPADDING", (0,0), (-1,-1), 1),
    ]))
    out.append(t2)
    out.append(Spacer(1, 3*mm))

    # Antibiotic grid (single column, G1/G2/G3)
    filled = [r for r in ab_rows if (r.s_1 or r.s_2 or r.s_3 or r.mic_1 or r.mic_2 or r.mic_3)]
    if filled:
        filled.sort(key=lambda r: ((r.antibiotic.group or ""), (r.antibiotic.sort_order or 0)))

        grid = [[Paragraph("", hdr_style),
                 Paragraph("", hdr_style),
                 Paragraph("<b>G1</b>", hdr_style),
                 Paragraph("<b>G2</b>", hdr_style),
                 Paragraph("<b>G3</b>", hdr_style)]]

        cur_group = None
        for r in filled:
            g = (r.antibiotic.group or "OTHER").upper()
            if g != cur_group:
                grid.append([Paragraph(g, group_style),
                             Paragraph("", med_style),
                             Paragraph("", sir_style),
                             Paragraph("", sir_style),
                             Paragraph("", sir_style)])
                cur_group = g

            def sir(v):
                return (v or "-").upper() if v else "-"

            grid.append([Paragraph("", med_style),
                         Paragraph(r.antibiotic.name, med_style),
                         Paragraph(sir(r.s_1), sir_style),
                         Paragraph(sir(r.s_2), sir_style),
                         Paragraph(sir(r.s_3), sir_style)])

        ab_tbl = Table(grid, colWidths=[35*mm, 85*mm, 16*mm, 16*mm, 16*mm])
        ab_tbl.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#adb5bd")),
            ("BACKGROUND", (0,0), (-1,0), grey_hd),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("ALIGN", (2,0), (-1,-1), "CENTER"),
            ("LEFTPADDING", (0,0), (-1,-1), 3),
            ("RIGHTPADDING", (0,0), (-1,-1), 3),
            ("TOPPADDING", (0,0), (-1,-1), 2),
            ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ]))
        out.append(ab_tbl)
        out.append(Spacer(1, 2*mm))

    # Legend
    out.append(Paragraph("<b>S=</b> Sensitive  <b>I=</b> Intermediate  <b>R=</b> Resistant",
                         note_style))
    out.append(Spacer(1, 3*mm))

    # Comments
    comments = _plain(result.culture_comments_txt) or ""
    if comments:
        ct = Table([[Paragraph("<b>COMMENTS:</b>", label_style),
                     Paragraph(comments, note_style)]],
                   colWidths=[30*mm, 140*mm])
        ct.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ]))
        out.append(ct)

    return out
