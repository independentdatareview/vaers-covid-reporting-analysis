\# VAERS COVID Analysis

\## Release Notes v2.0



Release Date: June 2026



\## Major Update



Version 2.0 adds ICAN/CDC lot-distribution denominator data for Pfizer COVID vaccine lots.



This allows denominator-adjusted lot analysis using:



\- VAERS reports by lot

\- serious reports by lot

\- death reports by lot

\- doses shipped by lot

\- reports per million doses shipped

\- serious reports per million doses shipped

\- observed/expected serious-reporting ratios



\## Key New Finding



Several Pfizer lots remained elevated after denominator adjustment.



Notable examples:



| Lot | Serious Reports | Expected Serious | O/E Ratio |

|---|---:|---:|---:|

| GJ3277 | 579 | 114.68 | 5.049 |

| EN6201 | 1,253 | 438.89 | 2.855 |

| EN6200 | 1,102 | 405.25 | 2.719 |

| EN6202 | 1,070 | 397.35 | 2.693 |

| ER2613 | 926 | 449.06 | 2.062 |



\## Interpretation



These lots exhibited elevated serious-reporting frequencies within VAERS relative to the Pfizer lot baseline after adjustment for doses shipped.



\## Important Limitation



This analysis uses doses shipped, not confirmed doses administered.



VAERS remains a passive reporting system.



The results do not establish causation, manufacturing defects, contamination, formulation differences, or true incidence rates.



\## New Outputs



\- output/ican\_lot\_denominators.csv

\- output/lot\_reporting\_rates.csv

\- output/lot\_observed\_expected\_rates.csv



\## Status



Version 2.0 is the denominator-adjusted lot-analysis release.

