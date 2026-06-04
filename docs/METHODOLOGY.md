\# Methodology



\## Objective



The objective of this project was to evaluate reporting patterns within the COVID-19 VAERS dataset and determine whether observable differences existed across vaccine manufacturers, vaccine lots, demographic groups, geographic regions, and time periods.



This project was designed as an exploratory and statistical analysis of VAERS reporting behavior. It was not designed to establish causality or estimate true incidence rates.



\---



\# Data Sources



The analysis utilized publicly available VAERS data obtained from the CDC.



Datasets included:



\- VAERSDATA

\- VAERSVAX

\- VAERSSYMPTOMS



Years included:



\- 2020

\- 2021

\- 2022

\- 2023

\- 2024

\- 2025

\- 2026

\- Non-Domestic VAERS Reports



Only COVID-19 vaccine records were retained for analysis.



\---



\# Data Processing



The raw VAERS ZIP files were imported into a local DuckDB analytical database.



Records were linked using:



\- VAERS\_ID



COVID-related reports were identified using vaccine-type filtering from VAERSVAX records.



Linked tables were created to combine:



\- Patient demographics

\- Vaccine manufacturer

\- Vaccine lot number

\- Outcome indicators

\- Symptom descriptions



\---



\# Database Environment



Software:



\- Python 3.13

\- DuckDB

\- Pandas

\- NumPy

\- StatsModels

\- SciPy



All analysis was performed locally.



No cloud-based analytical services were used.



\---



\# Analytical Phases



\## Phase 1: Lot-Level Analysis



Objective:



Determine whether specific vaccine lots demonstrated unusual reporting behavior.



Methods:



\- Report counts by lot

\- Serious-event percentages by lot

\- Age-adjusted lot comparisons

\- State-adjusted lot comparisons



Outcome:



Substantial lot variation was observed, but much of the variation was explained by demographic and geographic differences.



\---



\## Phase 2: Manufacturer Analysis



Manufacturers analyzed:



\- Pfizer/BioNTech

\- Moderna

\- Janssen



Methods:



\- Serious-event comparisons

\- Death-report comparisons

\- Hospitalization comparisons

\- Disability comparisons



Outcome:



Manufacturer-specific reporting patterns remained after demographic adjustment.



\---



\## Phase 3: Symptom Analysis



VAERSSYMPTOMS records were transformed into a normalized symptom table.



Methods:



\- Symptom frequency analysis

\- Symptom enrichment analysis

\- Manufacturer comparison



Outcome:



Distinct symptom patterns emerged between manufacturers.



\---



\## Phase 4: Diagnosis Analysis



Specific diagnoses were identified through symptom-term matching.



Conditions evaluated included:



\### Cardiac



\- Myocarditis

\- Pericarditis

\- Cardiac arrest

\- Myocardial infarction



\### Thrombotic



\- Thrombosis

\- Deep Vein Thrombosis (DVT)

\- Pulmonary Embolism (PE)

\- Cerebral Venous Sinus Thrombosis (CVST)



\### Neurological



\- Guillain-Barré Syndrome

\- Syncope

\- Loss of Consciousness



\---



\## Phase 5: Statistical Analysis



Methods included:



\### Risk Ratios



Comparisons between manufacturers:



\- Janssen vs Pfizer

\- Janssen vs Moderna

\- Pfizer vs Moderna



\### Confidence Intervals



95% confidence intervals were calculated for risk-ratio estimates.



\### Fisher Exact Testing



Statistical significance was evaluated using Fisher exact testing.



\---



\## Phase 6: Logistic Regression



Multivariable logistic regression models were constructed.



Predictors:



\- Manufacturer

\- Age Bucket

\- Sex



Outcomes:



\- Myocarditis

\- Pericarditis

\- Guillain-Barré Syndrome

\- CVST

\- Pulmonary Embolism

\- DVT

\- Thrombosis

\- Syncope

\- Loss of Consciousness



Reference Manufacturer:



\- Moderna



Odds ratios and 95% confidence intervals were calculated.



\---



\## Phase 7: Time-Series Analysis



Reporting patterns were evaluated by:



\- Year

\- Quarter



Special attention was given to:



\- 2021 rollout period

\- 2022 follow-up period



A separate 2021-only logistic regression model was constructed to evaluate whether observed effects persisted within the primary vaccination rollout year.



\---



\# Reproducibility



All analyses were conducted using scripts contained within this repository.



The project is fully reproducible using:



\- Public VAERS data

\- DuckDB

\- Python



No proprietary datasets were used.

