import duckdb

con = duckdb.connect(r".\vaers_covid.duckdb")

manufacturers = [
    "JANSSEN",
    "PFIZER\\BIONTECH",
    "MODERNA"
]

for manu in manufacturers:

    print("\n" + "=" * 80)
    print(f"MANUFACTURER: {manu}")
    print("=" * 80)

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
    WHERE VAX_MANU = ?
    ORDER BY observed_expected_ratio DESC
    LIMIT 25
    """, [manu]).df()

    print(df.to_string(index=False))

    safe_name = manu.replace("\\", "_").replace("/", "_")
    df.to_csv(
        rf".\output\adjusted_{safe_name}_top25.csv",
        index=False
    )
