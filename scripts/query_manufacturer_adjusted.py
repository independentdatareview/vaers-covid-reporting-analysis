import duckdb

con = duckdb.connect(r".\vaers_covid.duckdb")

df = con.execute("""
SELECT
    VAX_MANU,
    COUNT(*) AS lots_over_1000_reports,
    ROUND(AVG(observed_expected_ratio), 3) AS avg_oe_ratio,
    ROUND(MEDIAN(observed_expected_ratio), 3) AS median_oe_ratio,
    ROUND(MAX(observed_expected_ratio), 3) AS max_oe_ratio,
    SUM(observed_serious) AS observed_serious,
    ROUND(SUM(expected_serious), 2) AS expected_serious,
    ROUND(SUM(observed_serious) / SUM(expected_serious), 3) AS manufacturer_oe_ratio
FROM lot_adjusted_serious
GROUP BY VAX_MANU
ORDER BY manufacturer_oe_ratio DESC
""").df()

print(df.to_string(index=False))

df.to_csv(
    r".\output\manufacturer_adjusted_serious.csv",
    index=False
)
