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
ORDER BY reports DESC
LIMIT 50
""").df()

print(df.to_string(index=False))
