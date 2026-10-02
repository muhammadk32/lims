"""Culture & Sensitivity - ADAM microbiology 2-column layout."""
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
        fontSize=7.5, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0d6efd"))
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
        ("BOX", (0, 0), (-1, -1), 0.8, border),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    out.append(t)
    out.append(Spacer(1, 3*mm))

    # Specimen + Growth
    specimen = _plain(result.culture_specimen) or "-"
    body_rows = [[Paragraph("<b>SPECIMEN:</b>", label_style),
                  Paragraph(specimen, body_style)]]
    growth_lines = []
    for g in (1, 2, 3):
        txt = _plain(getattr(result, "culture_growth_%d" % g, "") or "")
        if not txt or txt.strip().lower() in ("none", "null"):
            continue
        growth_lines.append("CULTURE %d:  %s" % (g, txt))
    if growth_lines:
        body_rows.append([Paragraph("", label_style),
                          Paragraph("<br/>".join(growth_lines), body_style)])
    t2 = Table(body_rows, colWidths=[30*mm, 140*mm])
    t2.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    out.append(t2)
    out.append(Spacer(1, 3*mm))

    # Antibiotic grid ? 2-column layout
    filled = [r for r in ab_rows if (r.s_1 or r.s_2 or r.s_3 or r.mic_1 or r.mic_2 or r.mic_3)]
    if filled:
        filled.sort(key=lambda r: ((r.antibiotic.group or ""), (r.antibiotic.sort_order or 0)))

        _ns = (result.culture_no_sensitive or "").strip()
        n_g = 1
        if "No Sensitive" in _ns:
            n_g = 1
        else:
            for ch in _ns:
                if ch.isdigit():
                    n_g = int(ch); break

        half = (len(filled) + 1) // 2
        left_items  = filled[:half]
        right_items = filled[half:]

        # Build row data: each row is [med_name, g1, g2, med_name_r, g1_r, g2_r]
        # Group header rows span the med column (rest blank)
        def build_rows(items):
            rows = []
            cur = None
            for r in items:
                g = (r.antibiotic.group or "OTHER").upper()
                if g != cur:
                    rows.append(("group", g))
                    cur = g
                vals = [(r.s_1 or "-").upper(),
                        (r.s_2 or "-").upper(),
                        (r.s_3 or "-").upper()][:n_g]
                rows.append(("med", (r.antibiotic.name, vals)))
            return rows

        L = build_rows(left_items)
        R = build_rows(right_items)

        n_rows = max(len(L), len(R))
        while len(L) < n_rows: L.append(("empty", None))
        while len(R) < n_rows: R.append(("empty", None))

        # Build header row: [blank, G1, G2] [blank, G1, G2]
        hdr = [Paragraph("", hdr_style)]
        for i in range(1, n_g + 1):
            hdr.append(Paragraph("<b>G%d</b>" % i, hdr_style))
        hdr.append(Paragraph("", hdr_style))
        for i in range(1, n_g + 1):
            hdr.append(Paragraph("<b>G%d</b>" % i, hdr_style))

        grid = [hdr]

        for l, r in zip(L, R):
            row = []
            # Left half
            if l[0] == "group":
                row.append(Paragraph(l[1], group_style))
                for _ in range(n_g):
                    row.append(Paragraph("", sir_style))
            elif l[0] == "med":
                name, vals = l[1]
                row.append(Paragraph(name, med_style))
                for v in vals:
                    row.append(Paragraph(v, sir_style))
                while len(vals) < n_g:
                    row.append(Paragraph("", sir_style))
            else:
                for _ in range(1 + n_g):
                    row.append(Paragraph("", med_style))

            # Right half
            if r[0] == "group":
                row.append(Paragraph(r[1], group_style))
                for _ in range(n_g):
                    row.append(Paragraph("", sir_style))
            elif r[0] == "med":
                name, vals = r[1]
                row.append(Paragraph(name, med_style))
                for v in vals:
                    row.append(Paragraph(v, sir_style))
                while len(vals) < n_g:
                    row.append(Paragraph("", sir_style))
            else:
                for _ in range(1 + n_g):
                    row.append(Paragraph("", med_style))

            grid.append(row)

        # Column widths ? each half = (med_w) + n_g * g_w
        #   total = 170mm
        total_w = 170 * mm
        half_w = total_w / 2
        g_w = 12 * mm
        med_w = half_w - (n_g * g_w)
        if med_w < 20 * mm:
            med_w = 20 * mm
            g_w = (half_w - med_w) / n_g
        col_w = [med_w] + [g_w] * n_g + [med_w] + [g_w] * n_g
        # final safety: shave
        diff = sum(col_w) - total_w
        if diff > 0:
            shave = diff / len(col_w)
            col_w = [w - shave for w in col_w]

        ab_tbl = Table(grid, colWidths=col_w)
        mid = 1 + n_g
        ab_tbl.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#adb5bd")),
            ("BACKGROUND", (0, 0), (-1, 0), grey_hd),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LINEBEFORE", (mid, 0), (mid, -1), 1.0, colors.HexColor("#212529")),
        ]))
        out.append(ab_tbl)
        out.append(Spacer(1, 2*mm))

    out.append(Paragraph("<b>S=</b> Sensitive  <b>I=</b> Intermediate  <b>R=</b> Resistant",
                         note_style))
    out.append(Spacer(1, 3*mm))

    comments = _plain(result.culture_comments_txt) or ""
    if comments:
        ct = Table([[Paragraph("<b>COMMENTS:</b>", label_style),
                     Paragraph(comments, note_style)]], colWidths=[30*mm, 140*mm])
        ct.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        out.append(ct)

    return out
