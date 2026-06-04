import duckdb

con = duckdb.connect(r".\vaers_covid.duckdb")

# VAERS symptom files have up to five symptom columns per report.
# This unpivots them into one symptom per row.

con.execute("""
CREATE OR REPLACE TABLE covid_symptom_long AS
SELECT VAERS_ID, SYMPTOM1 AS symptom FROM covid_symptoms WHERE SYMPTOM1 IS NOT NULL
UNION ALL
SELECT VAERS_ID, SYMPTOM2 AS symptom FROM covid_symptoms WHERE SYMPTOM2 IS NOT NULL
UNION ALL
SELECT VAERS_ID, SYMPTOM3 AS symptom FROM covid_symptoms WHERE SYMPTOM3 IS NOT NULL
UNION ALL
SELECT VAERS_ID, SYMPTOM4 AS symptom FROM covid_symptoms WHERE SYMPTOM4 IS NOT NULL
UNION ALL
SELECT VAERS_ID, SYMPTOM5 AS symptom FROM covid_symptoms WHERE SYMPTOM5 IS NOT NULL
""")

con.execute("""
CREATE OR REPLACE TABLE symptom_manufacturer_counts AS
SELECT
    r.VAX_MANU,
    s.symptom,
    COUNT(DISTINCT r.VAERS_ID) AS reports
FROM covid_reports r
JOIN covid_symptom_long s
ON r.VAERS_ID = s.VAERS_ID
WHERE r.SOURCE_SCOPE='DOMESTIC'
GROUP BY r.VAX_MANU, s.symptom
""")

manufacturers = ["JANSSEN", "PFIZER\\BIONTECH", "MODERNA"]

for manu in manufacturers:
    print("\n" + "=" * 80)
    print(f"TOP SYMPTOMS: {manu}")
    print("=" * 80)

    df = con.execute("""
    SELECT
        symptom,
        reports
    FROM symptom_manufacturer_counts
    WHERE VAX_MANU = ?
    ORDER BY reports DESC
    LIMIT 50
    """, [manu]).df()

    print(df.to_string(index=False))

    safe = manu.replace("\\", "_").replace("/", "_")
    df.to_csv(
        rf".\output\top_symptoms_{safe}.csv",
        index=False
    )

con.close()
