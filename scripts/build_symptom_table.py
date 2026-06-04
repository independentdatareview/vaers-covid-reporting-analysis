from pathlib import Path
import duckdb

BASE = Path(r".")
EXTRACTED = BASE / "output" / "extracted_covid"
DB = BASE / "vaers_covid.duckdb"

con = duckdb.connect(str(DB))

years = [str(y) for y in range(2020, 2027)] + ["NonDomestic"]

selects = []

for year in years:
    folder = EXTRACTED / year
    files = list(folder.glob("*VAERSSYMPTOMS.csv"))

    if not files:
        print(f"No symptom file found for {year}, skipping")
        continue

    path = files[0].as_posix().replace("'", "''")
    scope = "NONDOMESTIC" if year == "NonDomestic" else "DOMESTIC"

    print(f"Loading symptoms {year}...")

    table = f"symptoms_{year}".replace("-", "_")

    con.execute(f"""
    CREATE OR REPLACE TABLE {table} AS
    SELECT
        *,
        '{scope}' AS SOURCE_SCOPE,
        '{year}' AS YEAR_FILE
    FROM read_csv_auto('{path}', ignore_errors=true, all_varchar=true)
    """)

    selects.append(f"SELECT * FROM {table}")

con.execute("CREATE OR REPLACE TABLE vaers_symptoms AS " + " UNION ALL ".join(selects))

con.execute("""
CREATE OR REPLACE TABLE covid_symptoms AS
SELECT s.*
FROM vaers_symptoms s
INNER JOIN (
    SELECT DISTINCT VAERS_ID
    FROM covid_reports
) c
ON s.VAERS_ID = c.VAERS_ID
""")

print("Validation counts:")
for table in ["vaers_symptoms", "covid_symptoms"]:
    count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {count:,}")

con.close()
