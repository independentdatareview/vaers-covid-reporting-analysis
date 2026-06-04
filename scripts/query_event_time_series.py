import duckdb

con = duckdb.connect(r".\vaers_covid.duckdb")

query = """
WITH symptom_events AS (
    SELECT
        r.VAERS_ID,
        r.VAX_MANU,
        r.RECVDATE,
        strptime(r.RECVDATE, '%m/%d/%Y') AS received_date,
        lower(s.symptom) AS symptom
    FROM covid_reports r
    JOIN covid_symptom_long s
      ON r.VAERS_ID = s.VAERS_ID
    WHERE r.SOURCE_SCOPE='DOMESTIC'
      AND r.VAX_MANU IN ('JANSSEN','PFIZER\\BIONTECH','MODERNA')
      AND r.RECVDATE IS NOT NULL
),

flags AS (
    SELECT
        VAERS_ID,
        VAX_MANU,
        year(received_date) AS year,
        quarter(received_date) AS quarter,

        MAX(CASE WHEN symptom LIKE '%myocarditis%' THEN 1 ELSE 0 END) AS myocarditis,
        MAX(CASE WHEN symptom LIKE '%pericarditis%' THEN 1 ELSE 0 END) AS pericarditis,
        MAX(CASE WHEN symptom LIKE '%guillain%' THEN 1 ELSE 0 END) AS guillain_barre,
        MAX(CASE WHEN symptom LIKE '%cerebral venous sinus thrombosis%' THEN 1 ELSE 0 END) AS cvst,
        MAX(CASE WHEN symptom LIKE '%pulmonary embolism%' THEN 1 ELSE 0 END) AS pulmonary_embolism,
        MAX(CASE WHEN symptom LIKE '%deep vein thrombosis%' THEN 1 ELSE 0 END) AS deep_vein_thrombosis,
        MAX(CASE WHEN symptom LIKE '%thrombosis%' THEN 1 ELSE 0 END) AS thrombosis_any,
        MAX(CASE WHEN symptom LIKE '%syncope%' THEN 1 ELSE 0 END) AS syncope,
        MAX(CASE WHEN symptom LIKE '%loss of consciousness%' THEN 1 ELSE 0 END) AS loss_of_consciousness

    FROM symptom_events
    WHERE received_date IS NOT NULL
    GROUP BY VAERS_ID, VAX_MANU, year, quarter
),

unpivoted AS (
    SELECT VAX_MANU, year, quarter, 'myocarditis' AS event, myocarditis AS flag FROM flags
    UNION ALL SELECT VAX_MANU, year, quarter, 'pericarditis', pericarditis FROM flags
    UNION ALL SELECT VAX_MANU, year, quarter, 'guillain_barre', guillain_barre FROM flags
    UNION ALL SELECT VAX_MANU, year, quarter, 'cvst', cvst FROM flags
    UNION ALL SELECT VAX_MANU, year, quarter, 'pulmonary_embolism', pulmonary_embolism FROM flags
    UNION ALL SELECT VAX_MANU, year, quarter, 'deep_vein_thrombosis', deep_vein_thrombosis FROM flags
    UNION ALL SELECT VAX_MANU, year, quarter, 'thrombosis_any', thrombosis_any FROM flags
    UNION ALL SELECT VAX_MANU, year, quarter, 'syncope', syncope FROM flags
    UNION ALL SELECT VAX_MANU, year, quarter, 'loss_of_consciousness', loss_of_consciousness FROM flags
),

totals AS (
    SELECT
        VAX_MANU,
        year,
        quarter,
        COUNT(DISTINCT VAERS_ID) AS total_reports
    FROM flags
    GROUP BY VAX_MANU, year, quarter
)

SELECT
    u.year,
    u.quarter,
    u.VAX_MANU,
    u.event,
    SUM(u.flag) AS event_reports,
    t.total_reports,
    ROUND(100.0 * SUM(u.flag) / t.total_reports, 4) AS event_pct
FROM unpivoted u
JOIN totals t
  ON u.VAX_MANU = t.VAX_MANU
 AND u.year = t.year
 AND u.quarter = t.quarter
GROUP BY u.year, u.quarter, u.VAX_MANU, u.event, t.total_reports
HAVING t.total_reports >= 500
ORDER BY u.event, u.year, u.quarter, u.VAX_MANU
"""

df = con.execute(query).df()

print(df.to_string(index=False))

df.to_csv(
    r".\output\event_time_series_by_quarter.csv",
    index=False
)

con.close()
