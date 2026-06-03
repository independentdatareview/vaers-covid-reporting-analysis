\# VAERS COVID Reporting Pattern Analysis



\## Overview



This project analyzes publicly available COVID-19 vaccine adverse event reports from VAERS and combines them with publicly released CDC lot-distribution data to evaluate reporting patterns at the manufacturer and vaccine-lot level.



The project focuses on statistical signal detection, denominator adjustment, and reproducible analysis.



\## Objectives



The primary goals were:



\- Analyze manufacturer-level reporting patterns

\- Evaluate serious adverse event reporting frequencies

\- Examine symptom clusters

\- Perform denominator-adjusted lot analysis

\- Calculate observed-versus-expected (O/E) reporting ratios

\- Produce reproducible research outputs



\## Data Sources



\### VAERS



Public VAERS datasets including:



\- Reports

\- Vaccine information

\- Symptom information



\### CDC Lot Distribution Records



Publicly released lot-distribution records obtained through public disclosure and incorporated into denominator-adjusted analysis.



\## Major Findings



\### Manufacturer-Level



The analysis identified persistent differences in reporting patterns among:



\- Pfizer/BioNTech

\- Moderna

\- Janssen



after adjusting for age and state distributions.



\### Lot-Level



Several Pfizer lots remained elevated after denominator adjustment.



Examples:



| Lot | O/E Ratio |

|------|------:|

| GJ3277 | 5.049 |

| EN6201 | 2.855 |

| EN6200 | 2.719 |

| EN6202 | 2.693 |

| ER2613 | 2.062 |



These values represent elevated serious-reporting frequencies relative to the overall Pfizer lot baseline.



\## Important Limitations



This project does NOT establish:



\- Causation

\- Manufacturing defects

\- Product contamination

\- Clinical injury rates

\- Incidence rates



VAERS is a passive surveillance system and the analysis should be interpreted as reporting-pattern analysis only.



\## Repository Contents



\### Executive Summary



\- EXECUTIVE\_SUMMARY\_v2.md



\### Findings Reports



\- VAERS\_FINDINGS\_REPORT.md

\- VAERS\_FINDINGS\_REPORT\_v2.md



\### Release Notes



\- RELEASE\_NOTES\_v1.md

\- RELEASE\_NOTES\_v2.md



\### Methodology



\- docs/METHODOLOGY.md



\### Limitations



\- docs/LIMITATIONS.md



\### Outputs



\- output/ican\_lot\_denominators.csv

\- output/lot\_reporting\_rates.csv

\- output/lot\_observed\_expected\_rates.csv



\### PDFs



\- VAERS\_COVID\_Reporting\_Analysis\_Final.pdf

\- VAERS\_v2\_Denominator\_Adjusted\_Addendum.pdf



\## Reproducibility



All calculations were performed using:



\- DuckDB

\- Python

\- Pandas



The project was designed to be reproducible using publicly available source data.



\## Status



Version 2.0 Final Release



June 2026

