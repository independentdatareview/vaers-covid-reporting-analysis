import duckdb

con = duckdb.connect(r".\vaers_covid.duckdb")

df = con.execute("""
SELECT
    STATE,
    COUNT(DISTINCT VAERS_ID) AS reports,
    SUM(serious_flag) AS serious_reports,
    ROUND(
        100.0 * SUM(serious_flag) /
        COUNT(DISTINCT VAERS_ID),
        2
    ) AS serious_pct
FROM covid_reports
WHERE SOURCE_SCOPE='DOMESTIC'
  AND STATE IS NOT NULL
GROUP BY STATE
HAVING COUNT(DISTINCT VAERS_ID) >= 1000
ORDER BY serious_pct DESC
""").df()

print(df.to_string(index=False))
