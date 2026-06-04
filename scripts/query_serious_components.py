import duckdb

con = duckdb.connect(r".\vaers_covid.duckdb")

df = con.execute("""
SELECT
    VAX_MANU,

    COUNT(DISTINCT VAERS_ID) AS reports,

    SUM(died_flag) AS deaths,
    SUM(hosp_flag) AS hospitalizations,
    SUM(life_threat_flag) AS life_threatening,
    SUM(disable_flag) AS disabilities,

    ROUND(
        100.0 * SUM(died_flag) /
        COUNT(DISTINCT VAERS_ID),
        3
    ) AS death_pct,

    ROUND(
        100.0 * SUM(hosp_flag) /
        COUNT(DISTINCT VAERS_ID),
        3
    ) AS hosp_pct,

    ROUND(
        100.0 * SUM(life_threat_flag) /
        COUNT(DISTINCT VAERS_ID),
        3
    ) AS life_threat_pct,

    ROUND(
        100.0 * SUM(disable_flag) /
        COUNT(DISTINCT VAERS_ID),
        3
    ) AS disability_pct

FROM covid_reports
WHERE SOURCE_SCOPE='DOMESTIC'
GROUP BY VAX_MANU
ORDER BY reports DESC
""").df()

print(df.to_string(index=False))

df.to_csv(
    r".\output\manufacturer_serious_components.csv",
    index=False
)
