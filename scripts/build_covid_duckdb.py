from pathlib import Path
import zipfile
import duckdb
import time

BASE = Path(r".")
DATA = BASE / "data"
OUTPUT = BASE / "output"
EXTRACTED = OUTPUT / "extracted_covid"
DB = BASE / "vaers_covid.duckdb"

OUTPUT.mkdir(exist_ok=True)
EXTRACTED.mkdir(exist_ok=True)

YEARS = range(2020, 2027)

def find_csv(zf, token):
    token = token.upper()
    matches = [
        name for name in zf.namelist()
        if token in name.upper() and name.upper().endswith(".CSV")
    ]
    if not matches:
        raise FileNotFoundError(f"Could not find CSV containing {token}")
    return matches[0]

def extract_needed_files():
    print("Extracting needed CSV files...")

    extracted = []

    for year in YEARS:
        zip_path = DATA / f"{year}VAERSData.zip"
        year_dir = EXTRACTED / str(year)
        year_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(zip_path) as zf:
            data_file = find_csv(zf, f"{year}VAERSDATA")
            vax_file = find_csv(zf, f"{year}VAERSVAX")
            symptom_file = find_csv(zf, f"{year}VAERSSYMPTOMS")

            for member in [data_file, vax_file, symptom_file]:
                out_path = year_dir / Path(member).name
                if not out_path.exists():
                    zf.extract(member, year_dir)

        extracted.append({
            "scope": "DOMESTIC",
            "year": str(year),
            "data": str(year_dir / Path(data_file).name),
            "vax": str(year_dir / Path(vax_file).name),
            "symptoms": str(year_dir / Path(symptom_file).name),
        })

    nd_zip = DATA / "NonDomesticVAERSDATA.zip"
    nd_dir = EXTRACTED / "NonDomestic"
    nd_dir.mkdir(exist_ok=True)

    with zipfile.ZipFile(nd_zip) as zf:
        data_file = find_csv(zf, "NONDOMESTICVAERSDATA")
        vax_file = find_csv(zf, "NONDOMESTICVAERSVAX")
        symptom_file = find_csv(zf, "NONDOMESTICVAERSSYMPTOMS")

        for member in [data_file, vax_file, symptom_file]:
            out_path = nd_dir / Path(member).name
            if not out_path.exists():
                zf.extract(member, nd_dir)

    extracted.append({
        "scope": "NONDOMESTIC",
        "year": "NONDOMESTIC",
        "data": str(nd_dir / Path(data_file).name),
        "vax": str(nd_dir / Path(vax_file).name),
        "symptoms": str(nd_dir / Path(symptom_file).name),
    })

    return extracted

def sql_path(path):
    return Path(path).as_posix().replace("'", "''")

def main():
    start = time.time()
    files = extract_needed_files()

    if DB.exists():
        print(f"Removing old database: {DB}")
        DB.unlink()

    print(f"Creating DuckDB database: {DB}")
    con = duckdb.connect(str(DB))

    con.execute("SET memory_limit='8GB'")
    con.execute("SET threads=4")

    con.execute("""
        CREATE TABLE ingestion_log (
            scope VARCHAR,
            year_label VARCHAR,
            data_file VARCHAR,
            vax_file VARCHAR,
            symptoms_file VARCHAR
        )
    """)

    for item in files:
        con.execute(
            "INSERT INTO ingestion_log VALUES (?, ?, ?, ?, ?)",
            [item["scope"], item["year"], item["data"], item["vax"], item["symptoms"]]
        )

    print("Loading vaccine tables and filtering COVID records...")

    vax_selects = []

    for item in files:
        scope = item["scope"]
        year = item["year"]
        vax = sql_path(item["vax"])

        table = f"vax_{year}".replace("-", "_")

        print(f"  Loading VAX {year}...")

        con.execute(f"""
            CREATE OR REPLACE TABLE {table} AS
            SELECT
                *,
                regexp_replace(upper(trim(coalesce(VAX_LOT, ''))), '[^A-Z0-9]', '', 'g') AS VAX_LOT_NORM,
                '{scope}' AS SOURCE_SCOPE,
                '{year}' AS YEAR_FILE
            FROM read_csv_auto('{vax}', ignore_errors=true, all_varchar=true)
            WHERE upper(coalesce(VAX_TYPE, '')) LIKE '%COVID%'
               OR upper(coalesce(VAX_NAME, '')) LIKE '%COVID%'
               OR upper(coalesce(VAX_NAME, '')) LIKE '%SARS%'
        """)

        vax_selects.append(f"SELECT * FROM {table}")

    con.execute("CREATE OR REPLACE TABLE covid_vax AS " + " UNION ALL ".join(vax_selects))

    print("Creating COVID ID list...")

    con.execute("""
        CREATE OR REPLACE TABLE covid_ids AS
        SELECT DISTINCT VAERS_ID
        FROM covid_vax
    """)

    print("Loading matching DATA records...")

    data_selects = []

    for item in files:
        scope = item["scope"]
        year = item["year"]
        data = sql_path(item["data"])

        table = f"data_{year}".replace("-", "_")

        print(f"  Loading DATA {year}...")

        con.execute(f"""
            CREATE OR REPLACE TABLE {table} AS
            SELECT
                d.*,
                '{scope}' AS SOURCE_SCOPE,
                '{year}' AS YEAR_FILE
            FROM read_csv_auto('{data}', ignore_errors=true, all_varchar=true) d
            INNER JOIN covid_ids c
            ON d.VAERS_ID = c.VAERS_ID
        """)

        data_selects.append(f"SELECT * FROM {table}")

    con.execute("CREATE OR REPLACE TABLE covid_data AS " + " UNION ALL ".join(data_selects))

    print("Creating joined COVID reports table...")

    con.execute("""
        CREATE OR REPLACE TABLE covid_reports AS
        SELECT
            v.VAERS_ID,
            v.VAX_TYPE,
            v.VAX_MANU,
            v.VAX_NAME,
            v.VAX_LOT,
            v.VAX_LOT_NORM,
            v.VAX_DOSE_SERIES,
            v.SOURCE_SCOPE,
            v.YEAR_FILE,
            d.RECVDATE,
            d.STATE,
            TRY_CAST(d.AGE_YRS AS DOUBLE) AS AGE_YRS,
            d.SEX,
            d.DIED,
            d.DATEDIED,
            d.L_THREAT,
            d.ER_VISIT,
            d.HOSPITAL,
            TRY_CAST(d.HOSPDAYS AS DOUBLE) AS HOSPDAYS,
            d.DISABLE,
            d.RECOVD,
            d.VAX_DATE,
            d.ONSET_DATE,
            TRY_CAST(d.NUMDAYS AS DOUBLE) AS NUMDAYS,
            CASE WHEN upper(coalesce(d.DIED, '')) = 'Y' THEN 1 ELSE 0 END AS died_flag,
            CASE WHEN upper(coalesce(d.HOSPITAL, '')) = 'Y' THEN 1 ELSE 0 END AS hosp_flag,
            CASE WHEN upper(coalesce(d.L_THREAT, '')) = 'Y' THEN 1 ELSE 0 END AS life_threat_flag,
            CASE WHEN upper(coalesce(d.DISABLE, '')) = 'Y' THEN 1 ELSE 0 END AS disable_flag,
            CASE
                WHEN upper(coalesce(d.DIED, '')) = 'Y'
                  OR upper(coalesce(d.HOSPITAL, '')) = 'Y'
                  OR upper(coalesce(d.L_THREAT, '')) = 'Y'
                  OR upper(coalesce(d.DISABLE, '')) = 'Y'
                THEN 1 ELSE 0
            END AS serious_flag
        FROM covid_vax v
        LEFT JOIN covid_data d
        ON v.VAERS_ID = d.VAERS_ID
        WHERE v.VAX_LOT_NORM IS NOT NULL
          AND length(v.VAX_LOT_NORM) >= 3
          AND regexp_matches(v.VAX_LOT_NORM, '[0-9]')
          AND v.VAX_LOT_NORM NOT IN (
              'UNKNOWN','UNK','NONE','NA','NOTAVAILABLE','NOTPROVIDED',
              'NOLOT','NOREPORTED','MISSING','NULL','NIL'
          )
    """)

    print("Creating summary tables...")

    con.execute("""
        CREATE OR REPLACE TABLE covid_lot_summary AS
        SELECT
            SOURCE_SCOPE,
            VAX_MANU,
            VAX_LOT_NORM AS lot,
            COUNT(*) AS vax_rows,
            COUNT(DISTINCT VAERS_ID) AS reports,
            SUM(died_flag) AS death_reports,
            SUM(hosp_flag) AS hospital_reports,
            SUM(life_threat_flag) AS life_threat_reports,
            SUM(disable_flag) AS disability_reports,
            SUM(serious_flag) AS serious_reports,
            ROUND(100.0 * SUM(died_flag) / NULLIF(COUNT(DISTINCT VAERS_ID), 0), 3) AS death_pct,
            ROUND(100.0 * SUM(hosp_flag) / NULLIF(COUNT(DISTINCT VAERS_ID), 0), 3) AS hospital_pct,
            ROUND(100.0 * SUM(serious_flag) / NULLIF(COUNT(DISTINCT VAERS_ID), 0), 3) AS serious_pct,
            ROUND(avg(AGE_YRS), 2) AS mean_age,
            median(AGE_YRS) AS median_age,
            COUNT(DISTINCT STATE) AS states_reported,
            MIN(RECVDATE) AS first_received,
            MAX(RECVDATE) AS last_received
        FROM covid_reports
        GROUP BY SOURCE_SCOPE, VAX_MANU, VAX_LOT_NORM
        ORDER BY reports DESC
    """)

    con.execute("""
        CREATE OR REPLACE TABLE covid_lot_state_profile AS
        SELECT
            SOURCE_SCOPE,
            VAX_MANU,
            VAX_LOT_NORM AS lot,
            STATE,
            COUNT(DISTINCT VAERS_ID) AS reports,
            SUM(died_flag) AS death_reports,
            SUM(serious_flag) AS serious_reports
        FROM covid_reports
        WHERE STATE IS NOT NULL AND trim(STATE) <> ''
        GROUP BY SOURCE_SCOPE, VAX_MANU, VAX_LOT_NORM, STATE
    """)

    con.execute("""
        CREATE OR REPLACE TABLE covid_lot_age_profile AS
        SELECT
            SOURCE_SCOPE,
            VAX_MANU,
            VAX_LOT_NORM AS lot,
            CASE
                WHEN AGE_YRS IS NULL THEN 'Unknown'
                WHEN AGE_YRS < 18 THEN '<18'
                WHEN AGE_YRS < 40 THEN '18-39'
                WHEN AGE_YRS < 65 THEN '40-64'
                WHEN AGE_YRS < 80 THEN '65-79'
                ELSE '80+'
            END AS age_bucket,
            COUNT(DISTINCT VAERS_ID) AS reports,
            SUM(died_flag) AS death_reports,
            SUM(serious_flag) AS serious_reports
        FROM covid_reports
        GROUP BY SOURCE_SCOPE, VAX_MANU, VAX_LOT_NORM, age_bucket
    """)

    con.execute("""
        CREATE OR REPLACE TABLE covid_manufacturer_summary AS
        SELECT
            SOURCE_SCOPE,
            VAX_MANU,
            COUNT(DISTINCT VAERS_ID) AS reports,
            COUNT(DISTINCT VAX_LOT_NORM) AS lots,
            SUM(died_flag) AS death_reports,
            SUM(hosp_flag) AS hospital_reports,
            SUM(serious_flag) AS serious_reports,
            ROUND(100.0 * SUM(died_flag) / NULLIF(COUNT(DISTINCT VAERS_ID), 0), 3) AS death_pct,
            ROUND(100.0 * SUM(serious_flag) / NULLIF(COUNT(DISTINCT VAERS_ID), 0), 3) AS serious_pct
        FROM covid_reports
        GROUP BY SOURCE_SCOPE, VAX_MANU
        ORDER BY reports DESC
    """)

    print("Exporting CSV files...")

    exports = {
        "covid_lot_summary.csv": "SELECT * FROM covid_lot_summary ORDER BY reports DESC",
        "covid_top500_lots.csv": "SELECT * FROM covid_lot_summary ORDER BY reports DESC LIMIT 500",
        "covid_top50_lots.csv": "SELECT * FROM covid_lot_summary ORDER BY reports DESC LIMIT 50",
        "covid_manufacturer_summary.csv": "SELECT * FROM covid_manufacturer_summary ORDER BY reports DESC",
    }

    for filename, query in exports.items():
        out = sql_path(OUTPUT / filename)
        con.execute(f"COPY ({query}) TO '{out}' WITH (HEADER, DELIMITER ',')")

    print("Validation counts:")
    for table in ["covid_vax", "covid_ids", "covid_data", "covid_reports", "covid_lot_summary"]:
        count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count:,}")

    elapsed = round((time.time() - start) / 60, 2)
    print(f"Done in {elapsed} minutes.")
    print(f"Database: {DB}")
    print(f"Outputs: {OUTPUT}")

    con.close()

if __name__ == "__main__":
    main()
