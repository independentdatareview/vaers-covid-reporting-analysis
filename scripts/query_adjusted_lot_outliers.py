import duckdb

con = duckdb.connect(r".\vaers_covid.duckdb")

# This builds an adjusted expected-serious table using STATE + age bucket.
# It asks: given the state and age mix of each lot, how many serious reports
# would we expect if the lot behaved like the overall domestic dataset?

con.execute("""
CREATE OR REPLACE TABLE domestic_reports_with_age AS
SELECT
    *,
    CASE
        WHEN AGE_YRS IS NULL THEN 'Unknown'
        WHEN AGE_YRS < 18 THEN '<18'
        WHEN AGE_YRS < 40 THEN '18-39'
        WHEN AGE_YRS < 65 THEN '40-64'
        WHEN AGE_YRS < 80 THEN '65-79'
        ELSE '80+'
    END AS age_bucket
FROM covid_reports
WHERE SOURCE_SCOPE='DOMESTIC'
  AND STATE IS NOT NULL
  AND trim(STATE) <> ''
""")

con.execute("""
CREATE OR REPLACE TABLE state_age_baseline AS
SELECT
    STATE,
    age_bucket,
    COUNT(DISTINCT VAERS_ID) AS baseline_reports,
    SUM(serious_flag) AS baseline_serious,
    1.0 * SUM(serious_flag) / COUNT(DISTINCT VAERS_ID) AS baseline_serious_rate
FROM domestic_reports_with_age
GROUP BY STATE, age_bucket
HAVING COUNT(DISTINCT VAERS_ID) >= 50
""")

con.execute("""
CREATE OR REPLACE TABLE lot_state_age_cells AS
SELECT
    VAX_MANU,
    VAX_LOT_NORM AS lot,
    STATE,
    age_bucket,
    COUNT(DISTINCT VAERS_ID) AS reports,
    SUM(serious_flag) AS observed_serious
FROM domestic_reports_with_age
GROUP BY VAX_MANU, VAX_LOT_NORM, STATE, age_bucket
""")

con.execute("""
CREATE OR REPLACE TABLE lot_adjusted_serious AS
SELECT
    l.VAX_MANU,
    l.lot,
    SUM(l.reports) AS reports,
    SUM(l.observed_serious) AS observed_serious,
    SUM(l.reports * b.baseline_serious_rate) AS expected_serious,
    SUM(l.observed_serious) - SUM(l.reports * b.baseline_serious_rate) AS excess_serious,
    1.0 * SUM(l.observed_serious) / NULLIF(SUM(l.reports * b.baseline_serious_rate), 0) AS observed_expected_ratio
FROM lot_state_age_cells l
INNER JOIN state_age_baseline b
    ON l.STATE = b.STATE
   AND l.age_bucket = b.age_bucket
GROUP BY l.VAX_MANU, l.lot
HAVING SUM(l.reports) >= 1000
ORDER BY observed_expected_ratio DESC
""")

df = con.execute("""
SELECT
    VAX_MANU,
    lot,
    reports,
    observed_serious,
    ROUND(expected_serious, 2) AS expected_serious,
    ROUND(excess_serious, 2) AS excess_serious,
    ROUND(observed_expected_ratio, 3) AS oe_ratio
FROM lot_adjusted_serious
ORDER BY oe_ratio DESC
LIMIT 100
""").df()

print(df.to_string(index=False))

df.to_csv(
    r".\output\adjusted_serious_outliers_state_age_min1000.csv",
    index=False
)
