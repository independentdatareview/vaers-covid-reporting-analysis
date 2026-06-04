import duckdb
import pandas as pd
from pathlib import Path

DB = r".\vaers_covid.duckdb"
OUT = r".\output\lot_reporting_rates.csv"

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

    WHERE total_doses_shipped >= 10000
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
        d.total_doses_shipped,
        d.source_rows,
        d.source_files,
        d.source_sheets

    FROM lot_stats l

    INNER JOIN clean_denominators d
        ON l.lot_number = d.lot_number
)

SELECT
    lot_number,
    VAX_MANU,
    reports,
    serious_reports,
    deaths,
    total_doses_shipped,

    ROUND(reports * 1000000.0 / total_doses_shipped, 2)
        AS reports_per_million,

    ROUND(serious_reports * 1000000.0 / total_doses_shipped, 2)
        AS serious_per_million,

    ROUND(deaths * 1000000.0 / total_doses_shipped, 2)
        AS deaths_per_million,

    source_rows,
    source_files,
    source_sheets

FROM joined

ORDER BY serious_per_million DESC
"""

df = con.execute(query).df()

print("\nMatched Pfizer lots with denominator >= 10,000 doses:")
print(len(df))

print("\nColumns:")
print(list(df.columns))

print("\nTop 50 by serious reports per million doses")
print("=" * 120)
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
print("=" * 120)
print("LOTS OF INTEREST")
print("=" * 120)

subset = df[df["lot_number"].isin(interesting)].copy()

if subset.empty:
    print("No lots of interest found.")
else:
    print(
        subset.sort_values("serious_per_million", ascending=False)
        .to_string(index=False)
    )

missing = [lot for lot in interesting if lot not in set(df["lot_number"])]
if missing:
    print("\nMissing lots of interest:")
    for lot in missing:
        print(lot)
else:
    print("\nAll lots of interest found.")

df.to_csv(OUT, index=False)
print(f"\nSaved: {OUT}")

print("\nValidation summary")
print("=" * 120)

summary = con.execute("""
WITH clean_denominators AS (
    SELECT *
    FROM ican_lot_denominators
    WHERE total_doses_shipped >= 10000
      AND LENGTH(lot_number) BETWEEN 5 AND 10
      AND regexp_matches(lot_number, '^[A-Z0-9]+$')
      AND NOT regexp_matches(lot_number, '^0+$')
)
SELECT
    COUNT(*) AS clean_denominator_lots,
    SUM(total_doses_shipped) AS clean_total_doses
FROM clean_denominators
""").df()

print(summary.to_string(index=False))

con.close()
