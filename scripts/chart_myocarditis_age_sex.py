import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DB = r".\vaers_covid.duckdb"
OUT = r".\output\myocarditis_age_sex.png"

con = duckdb.connect(DB)

query = """
WITH symptom_events AS (
    SELECT
        r.VAERS_ID,
        r.VAX_MANU,
        r.SEX,
        CASE
            WHEN r.AGE_YRS < 12 THEN '<12'
            WHEN r.AGE_YRS < 18 THEN '12-17'
            WHEN r.AGE_YRS < 25 THEN '18-24'
            WHEN r.AGE_YRS < 40 THEN '25-39'
            WHEN r.AGE_YRS < 65 THEN '40-64'
            WHEN r.AGE_YRS < 80 THEN '65-79'
            ELSE '80+'
        END AS age_bucket,
        lower(s.symptom) AS symptom
    FROM covid_reports r
    JOIN covid_symptom_long s
      ON r.VAERS_ID = s.VAERS_ID
    WHERE r.SOURCE_SCOPE='DOMESTIC'
      AND r.VAX_MANU IN ('PFIZER\\BIONTECH','MODERNA','JANSSEN')
      AND r.SEX IN ('M','F')
),

flags AS (
    SELECT
        VAERS_ID,
        VAX_MANU,
        SEX,
        age_bucket,
        MAX(CASE WHEN symptom LIKE '%myocarditis%' THEN 1 ELSE 0 END) AS myocarditis
    FROM symptom_events
    GROUP BY VAERS_ID, VAX_MANU, SEX, age_bucket
)

SELECT
    VAX_MANU,
    SEX,
    age_bucket,
    COUNT(*) AS reports,
    SUM(myocarditis) AS myocarditis_reports,
    ROUND(100.0 * SUM(myocarditis) / COUNT(*), 4) AS myocarditis_pct
FROM flags
GROUP BY VAX_MANU, SEX, age_bucket
HAVING COUNT(*) >= 500
ORDER BY SEX, age_bucket, VAX_MANU
"""

df = con.execute(query).df()
con.close()

male = df[df["SEX"] == "M"]

pivot = male.pivot(
    index="age_bucket",
    columns="VAX_MANU",
    values="myocarditis_pct"
)

pivot = pivot.reindex([
    "<12","12-17","18-24","25-39","40-64","65-79","80+"
])

ax = pivot.plot(kind="bar", figsize=(10,6))

plt.title("Male Myocarditis Reports by Age Group")
plt.ylabel("Percent of Reports Containing Myocarditis")
plt.xlabel("Age Group")
plt.tight_layout()

plt.savefig(OUT, dpi=300)
print(f"Saved: {OUT}")
