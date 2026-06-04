import duckdb

con = duckdb.connect(r".\vaers_covid.duckdb")

df = con.execute("""
SELECT
    SOURCE_SCOPE,
    VAX_MANU,
    lot,
    reports,
    death_reports,
    hospital_reports,
    serious_reports,
    death_pct,
    hospital_pct,
    serious_pct,
    mean_age,
    median_age,
    states_reported
FROM covid_lot_summary
WHERE reports >= 1000
ORDER BY serious_pct DESC
LIMIT 100
""").df()

print(df.to_string(index=False))

df.to_csv(r".\output\serious_outliers_min1000.csv", index=False)
