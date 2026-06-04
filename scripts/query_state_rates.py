import duckdb

con = duckdb.connect(r".\vaers_covid.duckdb")

lots = ["GJ3277", "ER2613"]

for lot in lots:

    print("\n")
    print("=" * 70)
    print(f"LOT: {lot}")
    print("=" * 70)

    df = con.execute(f"""
    SELECT
        STATE,
        reports,
        death_reports,
        serious_reports,
        ROUND(100.0 * serious_reports / reports, 2) AS serious_pct,
        ROUND(100.0 * death_reports / reports, 2) AS death_pct
    FROM covid_lot_state_profile
    WHERE lot = '{lot}'
      AND reports >= 10
    ORDER BY reports DESC
    """).df()

    print(df.to_string(index=False))
