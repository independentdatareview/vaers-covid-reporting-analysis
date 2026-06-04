import duckdb

DB = r".\vaers_covid.duckdb"

con = duckdb.connect(DB)

print("\n1) Basic denominator table summary")
print("=" * 80)

df = con.execute("""
SELECT
    manufacturer,
    COUNT(*) AS lots,
    SUM(total_doses_shipped) AS total_doses_shipped
FROM ican_lot_denominators
GROUP BY manufacturer
ORDER BY manufacturer
""").df()

print(df.to_string(index=False))


print("\n2) Plausible-looking lot numbers only")
print("=" * 80)

df = con.execute("""
SELECT
    manufacturer,
    COUNT(*) AS plausible_lots,
    SUM(total_doses_shipped) AS plausible_total_doses
FROM ican_lot_denominators
WHERE LENGTH(lot_number) BETWEEN 5 AND 10
  AND regexp_matches(lot_number, '^[A-Z0-9]+$')
  AND NOT regexp_matches(lot_number, '^0+$')
GROUP BY manufacturer
ORDER BY manufacturer
""").df()

print(df.to_string(index=False))


print("\n3) Top plausible lots by doses shipped")
print("=" * 80)

df = con.execute("""
SELECT
    manufacturer,
    lot_number,
    total_doses_shipped,
    source_rows,
    source_files,
    source_sheets
FROM ican_lot_denominators
WHERE LENGTH(lot_number) BETWEEN 5 AND 10
  AND regexp_matches(lot_number, '^[A-Z0-9]+$')
  AND NOT regexp_matches(lot_number, '^0+$')
ORDER BY total_doses_shipped DESC
LIMIT 50
""").df()

print(df.to_string(index=False))


print("\n4) Check known lots from our VAERS analysis")
print("=" * 80)

known_lots = [
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
    "EL9263"
]

lot_list = ",".join([f"'{x}'" for x in known_lots])

df = con.execute(f"""
SELECT
    manufacturer,
    lot_number,
    total_doses_shipped,
    source_rows,
    source_files,
    source_sheets
FROM ican_lot_denominators
WHERE lot_number IN ({lot_list})
ORDER BY lot_number
""").df()

print(df.to_string(index=False))


print("\n5) Which known lots are missing?")
print("=" * 80)

found = set(df["lot_number"].tolist())
missing = [x for x in known_lots if x not in found]

if missing:
    for lot in missing:
        print(lot)
else:
    print("None. All known lots found.")


con.close()
