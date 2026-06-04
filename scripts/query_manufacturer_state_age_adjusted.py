import duckdb

con = duckdb.connect(r".\vaers_covid.duckdb")

# Build state+age baseline rates
con.execute("""
CREATE OR REPLACE TABLE manufacturer_state_age_cells AS
SELECT
    VAX_MANU,
    STATE,
    CASE
        WHEN AGE_YRS IS NULL THEN 'Unknown'
        WHEN AGE_YRS < 18 THEN '<18'
        WHEN AGE_YRS < 40 THEN '18-39'
        WHEN AGE_YRS < 65 THEN '40-64'
        WHEN AGE_YRS < 80 THEN '65-79'
        ELSE '80+'
    END AS age_bucket,
    COUNT(DISTINCT VAERS_ID) AS reports,
    SUM(serious_flag) AS observed_serious
FROM covid_reports
WHERE SOURCE_SCOPE='DOMESTIC'
  AND STATE IS NOT NULL
GROUP BY VAX_MANU, STATE, age_bucket
""")

# Reuse the baseline table created earlier if it exists;
# otherwise recreate it.
con.execute("""
CREATE OR REPLACE TABLE state_age_baseline AS
SELECT
    STATE,
    CASE
        WHEN AGE_YRS IS NULL THEN 'Unknown'
        WHEN AGE_YRS < 18 THEN '<18'
        WHEN AGE_YRS < 40 THEN '18-39'
        WHEN AGE_YRS < 65 THEN '40-64'
        WHEN AGE_YRS < 80 THEN '65-79'
        ELSE '80+'
    END AS age_bucket,
    COUNT(DISTINCT VAERS_ID) AS reports,
    SUM(serious_flag) AS serious_reports,
    1.0 * SUM(serious_flag) /
        COUNT(DISTINCT VAERS_ID) AS serious_rate
FROM covid_reports
WHERE SOURCE_SCOPE='DOMESTIC'
  AND STATE IS NOT NULL
GROUP BY STATE, age_bucket
HAVING COUNT(DISTINCT VAERS_ID) >= 50
""")

df = con.execute("""
SELECT
    m.VAX_MANU,
    SUM(m.reports) AS reports,
    SUM(m.observed_serious) AS observed_serious,
    ROUND(SUM(m.reports * b.serious_rate),2) AS expected_serious,
    ROUND(
        SUM(m.observed_serious) -
        SUM(m.reports * b.serious_rate),
        2
    ) AS excess_serious,
    ROUND(
        SUM(m.observed_serious) /
        SUM(m.reports * b.serious_rate),
        3
    ) AS oe_ratio
FROM manufacturer_state_age_cells m
JOIN state_age_baseline b
    ON m.STATE = b.STATE
   AND m.age_bucket = b.age_bucket
GROUP BY m.VAX_MANU
ORDER BY oe_ratio DESC
""").df()

print(df.to_string(index=False))

df.to_csv(
    r".\output\manufacturer_state_age_adjusted.csv",
    index=False
)
