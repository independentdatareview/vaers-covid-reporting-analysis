import duckdb

con = duckdb.connect(r".\vaers_covid.duckdb")

df = con.execute("""
SELECT
    VAX_MANU,
    lot,
    reports,
    death_pct,
    hospital_pct,
    serious_pct,
    mean_age,
    median_age,
    states_reported
FROM covid_lot_summary
WHERE SOURCE_SCOPE='DOMESTIC'
  AND reports >= 1000
ORDER BY serious_pct DESC
LIMIT 100
""").df()

print(df.to_string(index=False))

df.to_csv(
    r".\output\domestic_outliers_min1000.csv",
    index=False
)
