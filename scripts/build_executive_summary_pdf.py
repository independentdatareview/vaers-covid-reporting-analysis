from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from pathlib import Path

BASE = Path(r".")

OUTPUT = BASE / "Executive_Summary_v1.pdf"

FIGURES = [
    BASE / "output" / "forest_plot_2021_odds_ratios.png",
    BASE / "output" / "myocarditis_age_sex.png",
    BASE / "output" / "figure_03_janssen_thrombosis_cluster.png",
    BASE / "output" / "figure_04_neuro_cluster.png",
    BASE / "output" / "figure_05_time_series_myocarditis.png",
]

doc = SimpleDocTemplate(str(OUTPUT))

styles = getSampleStyleSheet()

story = []

# ------------------------------------------------
# Title Page
# ------------------------------------------------

title = Paragraph(
    "COVID-19 VAERS Reporting Pattern Analysis<br/>2020–2026",
    styles["Title"]
)

author = Paragraph(
    "Version 1.0<br/>June 2026<br/><br/>Independent Researcher",
    styles["Heading2"]
)

story.append(title)
story.append(Spacer(1, 20))
story.append(author)
story.append(PageBreak())

# ------------------------------------------------
# Executive Summary
# ------------------------------------------------

summary = """
<b>Executive Summary</b><br/><br/>

This project analyzed COVID-related VAERS reports from
2020–2026 including domestic and non-domestic records.

The analysis utilized DuckDB, Python, confidence interval
analysis, logistic regression, symptom enrichment analysis,
manufacturer comparisons, lot analysis, and time-series methods.

Key findings included:

• Elevated myocarditis and pericarditis reporting among
Pfizer-associated reports.

• Elevated thrombosis, DVT, pulmonary embolism, CVST,
Guillain-Barré, syncope, and loss-of-consciousness reporting
among Janssen-associated reports.

These findings remained present after age and sex adjustment
and within a 2021-only rollout cohort.

The analysis did not identify evidence supporting placebo lots,
three-tier formulations, geographic targeting, or intentional
lot deployment patterns.
"""

story.append(Paragraph(summary, styles["BodyText"]))
story.append(PageBreak())

# ------------------------------------------------
# Figures
# ------------------------------------------------

captions = [
    "Figure 1. Age- and sex-adjusted logistic regression odds ratios.",
    "Figure 2. Male myocarditis reporting percentages by age group.",
    "Figure 3. Clotting-related symptom terms by manufacturer.",
    "Figure 4. Neurological symptom terms by manufacturer.",
    "Figure 5. Myocarditis reporting patterns by quarter during 2021.",
]

for fig, caption in zip(FIGURES, captions):

    if fig.exists():

        story.append(
            Paragraph(caption, styles["Heading3"])
        )

        story.append(
            Image(str(fig), width=450, height=300)
        )

        story.append(PageBreak())

# ------------------------------------------------
# Limitations
# ------------------------------------------------

limitations = """
<b>Limitations</b><br/><br/>

VAERS is a passive surveillance system and does not establish
causation.

Reporting frequency should not be interpreted as incidence.

This analysis did not include administered-dose denominator
data and therefore cannot estimate true risk.

Observed associations represent reporting patterns within the
VAERS dataset.
"""

story.append(
    Paragraph(limitations, styles["BodyText"])
)

story.append(PageBreak())

# ------------------------------------------------
# Future Research
# ------------------------------------------------

future = """
<b>Future Research</b><br/><br/>

Priority areas include:

• Manufacturer-specific denominator data

• Age-specific denominator data

• Vaccine Safety Datalink comparisons

• FDA Sentinel comparisons

• Medicare dataset comparisons

• Independent replication of findings
"""

story.append(
    Paragraph(future, styles["BodyText"])
)

doc.build(story)

print(f"Created: {OUTPUT}")
