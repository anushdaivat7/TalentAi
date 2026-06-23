"""Builds a polished PDF ranking report (reportlab) for download."""
from __future__ import annotations

import datetime as _dt
from io import BytesIO
from typing import Dict, List

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    LongTable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

# Brand palette (matches the dashboard).
_BG_HEADER = colors.HexColor("#4f46e5")
_BG_ROW_ALT = colors.HexColor("#eef2ff")
_TEXT_MUTED = colors.HexColor("#475569")
_LINE = colors.HexColor("#cbd5e1")
_ROSE = colors.HexColor("#e11d48")


def _styles():
    ss = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=ss["Title"], fontSize=20,
                           textColor=colors.HexColor("#1e1b4b"), spaceAfter=2)
    sub = ParagraphStyle("sub", parent=ss["Normal"], fontSize=9,
                         textColor=_TEXT_MUTED, spaceAfter=10)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=12,
                        textColor=colors.HexColor("#312e81"), spaceBefore=8, spaceAfter=6)
    cell = ParagraphStyle("cell", parent=ss["Normal"], fontSize=7.2, leading=9,
                          alignment=TA_LEFT)
    cell_head = ParagraphStyle("cellhead", parent=cell, fontSize=7.8,
                               textColor=colors.white, leading=10)
    cell_id = ParagraphStyle("cellid", parent=cell, fontName="Helvetica-Bold")
    return {"title": title, "sub": sub, "h2": h2, "cell": cell,
            "cell_head": cell_head, "cell_id": cell_id}


def _summary_table(ranked: List[Dict], trap_stats: Dict, st) -> Table:
    scores = [r.get("final_score", 0) for r in ranked]
    avg = round(sum(scores) / len(scores), 1) if scores else 0
    top = ranked[0] if ranked else {}
    pairs = [
        ("Candidates ranked", f"{len(ranked)}"),
        ("Average match score", f"{avg}"),
        ("Top candidate", f"{top.get('candidate_id', '-')} ({top.get('final_score', '-')})"),
        ("Honeypots in top 100", f"{sum(1 for r in ranked if r.get('is_honeypot'))}"),
        ("Honeypots disqualified (pool)", f"{trap_stats.get('honeypots_detected', '-')}"),
        ("Profiles scanned", f"{trap_stats.get('total_scanned', '-')}"),
    ]
    data = [[Paragraph(f"<b>{k}</b>", st["cell"]), Paragraph(str(v), st["cell"])]
            for k, v in pairs]
    t = Table(data, colWidths=[55 * mm, 40 * mm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, _LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, _LINE),
        ("BACKGROUND", (0, 0), (0, -1), _BG_ROW_ALT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def _candidates_table(ranked: List[Dict], st) -> LongTable:
    head = [
        Paragraph("#", st["cell_head"]),
        Paragraph("Candidate ID", st["cell_head"]),
        Paragraph("Score", st["cell_head"]),
        Paragraph("Title", st["cell_head"]),
        Paragraph("Exp", st["cell_head"]),
        Paragraph("Edu", st["cell_head"]),
        Paragraph("Location", st["cell_head"]),
        Paragraph("Reasoning", st["cell_head"]),
    ]
    rows = [head]
    honeypot_rows = []
    for i, r in enumerate(ranked, start=1):
        if r.get("is_honeypot"):
            honeypot_rows.append(i)
        rows.append([
            Paragraph(str(r.get("rank", i)), st["cell"]),
            Paragraph(str(r.get("candidate_id", "")), st["cell_id"]),
            Paragraph(str(r.get("final_score", "")), st["cell"]),
            Paragraph(str(r.get("current_title", "") or "-"), st["cell"]),
            Paragraph(f"{r.get('years_experience', '-')}", st["cell"]),
            Paragraph(str(r.get("education_tier", "") or "-").replace("tier_", "T"), st["cell"]),
            Paragraph(str(r.get("location", "") or "-"), st["cell"]),
            Paragraph(str(r.get("explanation", "") or ""), st["cell"]),
        ])

    widths = [10 * mm, 26 * mm, 13 * mm, 42 * mm, 12 * mm, 12 * mm, 34 * mm, 105 * mm]
    t = LongTable(rows, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), _BG_HEADER),
        ("GRID", (0, 0), (-1, -1), 0.25, _LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _BG_ROW_ALT]),
    ]
    for ri in honeypot_rows:
        style.append(("TEXTCOLOR", (1, ri), (1, ri), _ROSE))
    t.setStyle(TableStyle(style))
    return t


def build_report_pdf(ranked: List[Dict], trap_stats: Dict, team: str) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=landscape(A4),
        leftMargin=12 * mm, rightMargin=12 * mm,
        topMargin=12 * mm, bottomMargin=12 * mm,
        title=f"TalentAI Ranking Report - {team}",
        author="TalentAI",
    )
    st = _styles()
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    story = [
        Paragraph("TalentAI - Candidate Ranking Report", st["title"]),
        Paragraph(
            f"Role: Senior AI Engineer &nbsp;|&nbsp; Team: <b>{team}</b> "
            f"&nbsp;|&nbsp; Generated: {now} &nbsp;|&nbsp; "
            f"Top {len(ranked)} of {trap_stats.get('total_scanned', '100,000')} candidates",
            st["sub"],
        ),
        Paragraph("Summary", st["h2"]),
        _summary_table(ranked, trap_stats, st),
        Spacer(1, 6 * mm),
        Paragraph("Ranked Candidates", st["h2"]),
        _candidates_table(ranked, st),
    ]
    doc.build(story)
    return buf.getvalue()
