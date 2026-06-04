import duckdb

con = duckdb.connect(r".\vaers_covid.duckdb")

df = con.execute("""
WITH manufacturer_reports AS (
    SELECT
        VAX_MANU,
        COUNT(DISTINCT VAERS_ID) AS total_reports
    FROM covid_reports
    WHERE SOURCE_SCOPE='DOMESTIC'
    GROUP BY VAX_MANU
),

symptom_rates AS (
    SELECT
        r.VAX_MANU,
        s.symptom,
        COUNT(DISTINCT r.VAERS_ID) AS symptom_reports
    FROM covid_reports r
    JOIN covid_symptom_long s
      ON r.VAERS_ID = s.VAERS_ID
    WHERE r.SOURCE_SCOPE='DOMESTIC'
    GROUP BY r.VAX_MANU, s.symptom
)

SELECT
    sr.VAX_MANU,
    sr.symptom,
    sr.symptom_reports,
    mr.total_reports,
    ROUND(
        100.0 * sr.symptom_reports / mr.total_reports,
        3
    ) AS symptom_pct
FROM symptom_rates sr
JOIN manufacturer_reports mr
  ON sr.VAX_MANU = mr.VAX_MANU
WHERE sr.symptom_reports >= 500
ORDER BY sr.VAX_MANU, symptom_pct DESC
""").df()

for manu in df["VAX_MANU"].unique():
    print("\n" + "=" * 80)
    print(manu)
    print("=" * 80)

    subset = (
        df[df["VAX_MANU"] == manu]
        .sort_values("symptom_pct", ascending=False)
        .head(50)
    )

    print(subset.to_string(index=False))

con.close()
