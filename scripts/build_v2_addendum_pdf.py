from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from pathlib import Path

BASE = Path(r".")
OUTPUT = BASE / "VAERS_v2_Denominator_Adjusted_Addendum.pdf"

doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=letter,
    rightMargin=54,
    leftMargin=54,
    topMargin=54,
    bottomMargin=54
)

styles = getSampleStyleSheet()
story = []

story.append(Paragraph("VAERS COVID Reporting Pattern Analysis", styles["Title"]))
story.append(Spacer(1, 12))
story.append(Paragraph("Version 2.0 Addendum: Denominator-Adjusted Lot Analysis", styles["Heading2"]))
story.append(Spacer(1, 24))
story.append(Paragraph("Independent Researcher<br/>June 2026", styles["BodyText"]))
story.append(PageBreak())

story.append(Paragraph("Executive Summary", styles["Heading1"]))
story.append(Paragraph("""
Version 2.0 incorporates ICAN/CDC lot-distribution data for Pfizer COVID vaccine lots.
This allowed the analysis to move beyond raw VAERS lot report counts and calculate
denominator-adjusted reporting metrics using doses shipped by lot.
""", styles["BodyText"]))
story.append(Spacer(1, 12))

story.append(Paragraph("""
The key finding is that several Pfizer lots remained elevated after denominator adjustment.
The strongest lot-level signal identified was GJ3277, which showed an observed/expected
serious-reporting ratio of 5.049.
""", styles["BodyText"]))
story.append(Spacer(1, 18))

story.append(Paragraph("Key Denominator-Adjusted Findings", styles["Heading1"]))

data = [
    ["Lot", "Doses Shipped", "Serious Reports", "Expected Serious", "O/E Ratio"],
    ["GJ3277", "3,930,955", "579", "114.68", "5.049"],
    ["EN6201", "15,043,577", "1,253", "438.89", "2.855"],
    ["EN6200", "13,890,331", "1,102", "405.25", "2.719"],
    ["EN6202", "13,619,726", "1,070", "397.35", "2.693"],
    ["ER2613", "15,392,071", "926", "449.06", "2.062"],
]

table = Table(data, repeatRows=1)
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ("ALIGN", (0, 0), (0, -1), "LEFT"),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
]))

story.append(table)
story.append(Spacer(1, 18))

story.append(Paragraph("Interpretation", styles["Heading1"]))
story.append(Paragraph("""
These lots exhibited elevated serious-reporting frequencies within VAERS relative to the Pfizer
lot baseline after adjustment for doses shipped. The EN6200, EN6201, and EN6202 lots remained
elevated as a cluster, while GJ3277 showed the strongest individual lot-level signal.
""", styles["BodyText"]))
story.append(Spacer(1, 12))

story.append(Paragraph("""
Some lots that appeared notable in raw report-count analysis became less remarkable after
denominator adjustment. This demonstrates why dose denominators are essential for lot-level
interpretation.
""", styles["BodyText"]))

story.append(PageBreak())

story.append(Paragraph("Method Summary", styles["Heading1"]))
story.append(Paragraph("""
For each matched Pfizer lot, the analysis calculated total VAERS reports, serious reports,
death reports, total doses shipped, reports per million doses shipped, serious reports per
million doses shipped, deaths per million doses shipped, expected serious reports, and the
observed/expected serious-reporting ratio.
""", styles["BodyText"]))
story.append(Spacer(1, 12))

story.append(Paragraph("""
Expected serious reports were calculated using the overall Pfizer serious-reporting baseline
among matched lots with denominator data.
""", styles["BodyText"]))

story.append(Spacer(1, 18))

story.append(Paragraph("Important Limitations", styles["Heading1"]))
story.append(Paragraph("""
This analysis uses doses shipped, not confirmed doses administered. VAERS is a passive
surveillance system. Reporting frequency is not incidence, and association does not establish
causation.
""", styles["BodyText"]))
story.append(Spacer(1, 12))

story.append(Paragraph("""
The results do not establish manufacturing defects, contamination, formulation differences,
clinical causality, or true injury rates. They should be interpreted as denominator-adjusted
VAERS reporting-pattern findings.
""", styles["BodyText"]))

story.append(Spacer(1, 18))

story.append(Paragraph("Conclusion", styles["Heading1"]))
story.append(Paragraph("""
Version 2.0 materially improves the lot-level analysis by incorporating dose-denominator data.
The denominator-adjusted results show that some Pfizer lots remained elevated even after
accounting for doses shipped.
""", styles["BodyText"]))

doc.build(story)

print(f"Created: {OUTPUT}")
