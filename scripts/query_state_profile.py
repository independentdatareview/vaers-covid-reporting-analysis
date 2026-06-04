import duckdb

con = duckdb.connect(r".\vaers_covid.duckdb")

lots = ["GJ3277", "ER2613"]

for lot in lots:

    print("\n")
    print("=" * 60)
    print(f"LOT: {lot}")
    print("=" * 60)

    df = con.execute(f"""
    SELECT
        STATE,
        reports,
        death_reports,
        serious_reports
    FROM covid_lot_state_profile
    WHERE lot = '{lot}'
    ORDER BY reports DESC
    LIMIT 25
    """).df()

    print(df.to_string(index=False))
