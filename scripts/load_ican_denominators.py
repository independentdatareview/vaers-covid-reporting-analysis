from pathlib import Path
import pandas as pd
import duckdb
import re

BASE = Path(r".")
ICAN_DIR = BASE / "data" / "ICANN"
DB = BASE / "vaers_covid.duckdb"
OUT = BASE / "output" / "ican_lot_denominators.csv"

con = duckdb.connect(str(DB))

records = []

def clean_lot(x):
    if pd.isna(x):
        return None
    x = str(x).strip().upper()
    x = re.sub(r"[^A-Z0-9]", "", x)
    if x == "":
        return None
    return x

def add_records(df, lot_col, dose_col, manufacturer, source_file, source_sheet):
    temp = df[[lot_col, dose_col]].copy()
    temp.columns = ["lot_number", "doses_shipped"]

    temp["lot_number"] = temp["lot_number"].apply(clean_lot)
    temp["doses_shipped"] = pd.to_numeric(temp["doses_shipped"], errors="coerce")

    temp = temp.dropna(subset=["lot_number", "doses_shipped"])
    temp = temp[temp["doses_shipped"] > 0]

    for _, row in temp.iterrows():
        records.append({
            "lot_number": row["lot_number"],
            "manufacturer": manufacturer,
            "doses_shipped": float(row["doses_shipped"]),
            "source_file": source_file,
            "source_sheet": source_sheet
        })

# -------------------------------------------------------------------
# Read known ICAN files
# -------------------------------------------------------------------

files = sorted(ICAN_DIR.glob("*.xlsx"))

for file in files:
    print(f"Reading {file.name}")

    try:
        xls = pd.ExcelFile(file)

        for sheet in xls.sheet_names:
            df = pd.read_excel(file, sheet_name=sheet)

            cols = [str(c).strip() for c in df.columns]
            df.columns = cols

            lower_cols = {c.lower(): c for c in cols}

            source_file = file.name
            source_sheet = sheet

            # Case 1: shipment-level Pfizer/CDC records
            if "lot_number" in lower_cols and "doses_shipped" in lower_cols:
                add_records(
                    df,
                    lower_cols["lot_number"],
                    lower_cols["doses_shipped"],
                    "PFIZER",
                    source_file,
                    source_sheet
                )

            # Case 2: aggregated doses by lot
            if "lot_number" in lower_cols and "dosesbylot" in lower_cols:
                add_records(
                    df,
                    lower_cols["lot_number"],
                    lower_cols["dosesbylot"],
                    "PFIZER",
                    source_file,
                    source_sheet
                )

            # Case 3: uppercase CDC source file
            if "lot_number" in lower_cols and "doses_shipped" in lower_cols:
                pass

    except Exception as e:
        print(f"ERROR: {file.name}: {e}")

raw = pd.DataFrame(records)

print("\nRaw denominator rows:", len(raw))

if raw.empty:
    raise SystemExit("No denominator records found.")

# -------------------------------------------------------------------
# Aggregate by manufacturer and lot
# -------------------------------------------------------------------

agg = (
    raw.groupby(["manufacturer", "lot_number"], as_index=False)
    .agg(
        total_doses_shipped=("doses_shipped", "sum"),
        source_rows=("doses_shipped", "count"),
        source_files=("source_file", lambda x: "; ".join(sorted(set(x)))),
        source_sheets=("source_sheet", lambda x: "; ".join(sorted(set(x))))
    )
)

agg = agg.sort_values(["manufacturer", "lot_number"])

print("\nAggregated lot denominators:", len(agg))
print(agg.head(20).to_string(index=False))

# -------------------------------------------------------------------
# Save to DuckDB and CSV
# -------------------------------------------------------------------

con.execute("CREATE OR REPLACE TABLE ican_lot_denominators_raw AS SELECT * FROM raw")
con.execute("CREATE OR REPLACE TABLE ican_lot_denominators AS SELECT * FROM agg")

agg.to_csv(OUT, index=False)

print(f"\nSaved CSV: {OUT}")

# -------------------------------------------------------------------
# Validation
# -------------------------------------------------------------------

summary = con.execute("""
SELECT
    manufacturer,
    COUNT(*) AS lots,
    SUM(total_doses_shipped) AS total_doses_shipped
FROM ican_lot_denominators
GROUP BY manufacturer
ORDER BY manufacturer
""").df()

print("\nSummary:")
print(summary.to_string(index=False))

con.close()
