import duckdb

con = duckdb.connect(r".\vaers_covid.duckdb")

lots = [
    'GJ3277',
    'ER2613',
    'EN6200',
    'EN6201',
    'EN6202'
]

for lot in lots:
    print("\n" + "=" * 60)
    print(f"LOT: {lot}")
    print("=" * 60)

    df = con.execute(f"""
    SELECT
        age_bucket,
        reports,
        death_reports,
        serious_reports
    FROM covid_lot_age_profile
    WHERE lot = '{lot}'
    ORDER BY age_bucket
    """).df()

    print(df.to_string(index=False))
