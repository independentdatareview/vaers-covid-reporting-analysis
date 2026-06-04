import duckdb
import pandas as pd
import math

DB = r".\vaers_covid.duckdb"
OUT = r".\output\lot_observed_expected_rates.csv"

con = duckdb.connect(DB)

query = """
WITH lot_stats AS (

    SELECT
        UPPER(TRIM(VAX_LOT_NORM)) AS lot_number,
        VAX_MANU,
        COUNT(DISTINCT VAERS_ID) AS reports,
        SUM(serious_flag) AS serious_reports,
        SUM(died_flag) AS deaths

    FROM covid_reports

    WHERE VAX_LOT_NORM IS NOT NULL
      AND TRIM(VAX_LOT_NORM) <> ''
      AND VAX_MANU LIKE 'PFIZER%'

    GROUP BY
        UPPER(TRIM(VAX_LOT_NORM)),
        VAX_MANU
),

clean_denominators AS (

    SELECT
        manufacturer,
        lot_number,
        total_doses_shipped,
        source_rows,
        source_files,
        source_sheets

    FROM ican_lot_denominators

    WHERE total_doses_shipped >= 100000
      AND LENGTH(lot_number) BETWEEN 5 AND 10
      AND regexp_matches(lot_number, '^[A-Z0-9]+$')
      AND NOT regexp_matches(lot_number, '^0+$')
),

joined AS (

    SELECT
        l.lot_number,
        l.VAX_MANU,
        l.reports,
        l.serious_reports,
        l.deaths,
        d.total_doses_shipped

    FROM lot_stats l

    INNER JOIN clean_denominators d
        ON l.lot_number = d.lot_number
),

baseline AS (

    SELECT
        SUM(serious_reports) * 1.0 / SUM(total_doses_shipped) AS serious_rate_per_dose,
        SUM(reports) * 1.0 / SUM(total_doses_shipped) AS report_rate_per_dose,
        SUM(deaths) * 1.0 / SUM(total_doses_shipped) AS death_rate_per_dose
    FROM joined
)

SELECT
    j.lot_number,
    j.VAX_MANU,
    j.total_doses_shipped,
    j.reports,
    j.serious_reports,
    j.deaths,

    ROUND(j.reports * 1000000.0 / j.total_doses_shipped, 2) AS reports_per_million,
    ROUND(j.serious_reports * 1000000.0 / j.total_doses_shipped, 2) AS serious_per_million,
    ROUND(j.deaths * 1000000.0 / j.total_doses_shipped, 2) AS deaths_per_million,

    ROUND(j.total_doses_shipped * b.serious_rate_per_dose, 2) AS expected_serious,
    ROUND(j.serious_reports / NULLIF(j.total_doses_shipped * b.serious_rate_per_dose, 0), 3) AS serious_oe_ratio,

    ROUND(j.total_doses_shipped * b.death_rate_per_dose, 2) AS expected_deaths,
    ROUND(j.deaths / NULLIF(j.total_doses_shipped * b.death_rate_per_dose, 0), 3) AS death_oe_ratio

FROM joined j
CROSS JOIN baseline b

ORDER BY serious_oe_ratio DESC
"""

df = con.execute(query).df()
con.close()

# Add approximate Poisson 95% CI for serious O/E ratio
# CI for observed count approximated as observed ± 1.96*sqrt(observed), then divided by expected.
ci_low = []
ci_high = []

for _, row in df.iterrows():
    obs = row["serious_reports"]
    exp = row["expected_serious"]

    if exp and exp > 0 and obs > 0:
        low_obs = max(0, obs - 1.96 * math.sqrt(obs))
        high_obs = obs + 1.96 * math.sqrt(obs)
        ci_low.append(round(low_obs / exp, 3))
        ci_high.append(round(high_obs / exp, 3))
    else:
        ci_low.append(None)
        ci_high.append(None)

df["serious_oe_ci_low"] = ci_low
df["serious_oe_ci_high"] = ci_high

print("\nMatched Pfizer lots with denominator >= 100,000 doses:")
print(len(df))

print("\nTop 50 by serious observed/expected ratio")
print("=" * 130)
print(df.head(50).to_string(index=False))

interesting = [
    "EN6200",
    "EN6201",
    "EN6202",
    "ER2613",
    "GJ3277",
    "EW0162",
    "EW0168",
    "ER8731",
    "ER8736",
    "ER8737",
    "EL9263",
]

print("\n")
print("=" * 130)
print("LOTS OF INTEREST")
print("=" * 130)

subset = df[df["lot_number"].isin(interesting)].copy()

if subset.empty:
    print("No lots of interest found.")
else:
    print(
        subset.sort_values("serious_oe_ratio", ascending=False)
        .to_string(index=False)
    )

df.to_csv(OUT, index=False)

print(f"\nSaved: {OUT}")
