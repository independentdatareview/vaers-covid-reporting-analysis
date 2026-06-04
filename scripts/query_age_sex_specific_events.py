import duckdb

con = duckdb.connect(r".\vaers_covid.duckdb")

query = """
WITH symptom_events AS (
    SELECT
        r.VAERS_ID,
        r.VAX_MANU,
        r.SEX,
        CASE
            WHEN r.AGE_YRS IS NULL THEN 'Unknown'
            WHEN r.AGE_YRS < 12 THEN '<12'
            WHEN r.AGE_YRS < 18 THEN '12-17'
            WHEN r.AGE_YRS < 25 THEN '18-24'
            WHEN r.AGE_YRS < 40 THEN '25-39'
            WHEN r.AGE_YRS < 65 THEN '40-64'
            WHEN r.AGE_YRS < 80 THEN '65-79'
            ELSE '80+'
        END AS age_bucket,
        lower(s.symptom) AS symptom
    FROM covid_reports r
    JOIN covid_symptom_long s
      ON r.VAERS_ID = s.VAERS_ID
    WHERE r.SOURCE_SCOPE='DOMESTIC'
),

flags AS (
    SELECT
        VAERS_ID,
        VAX_MANU,
        SEX,
        age_bucket,

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
    GROUP BY VAERS_ID, VAX_MANU, SEX, age_bucket
),

totals AS (
    SELECT
        VAX_MANU,
        SEX,
        CASE
            WHEN AGE_YRS IS NULL THEN 'Unknown'
            WHEN AGE_YRS < 12 THEN '<12'
            WHEN AGE_YRS < 18 THEN '12-17'
            WHEN AGE_YRS < 25 THEN '18-24'
            WHEN AGE_YRS < 40 THEN '25-39'
            WHEN AGE_YRS < 65 THEN '40-64'
            WHEN AGE_YRS < 80 THEN '65-79'
            ELSE '80+'
        END AS age_bucket,
        COUNT(DISTINCT VAERS_ID) AS total_reports
    FROM covid_reports
    WHERE SOURCE_SCOPE='DOMESTIC'
    GROUP BY VAX_MANU, SEX, age_bucket
),

unpivoted AS (
    SELECT VAX_MANU, SEX, age_bucket, 'myocarditis' AS event, myocarditis AS flag FROM flags
    UNION ALL SELECT VAX_MANU, SEX, age_bucket, 'pericarditis', pericarditis FROM flags
    UNION ALL SELECT VAX_MANU, SEX, age_bucket, 'guillain_barre', guillain_barre FROM flags
    UNION ALL SELECT VAX_MANU, SEX, age_bucket, 'cvst', cvst FROM flags
    UNION ALL SELECT VAX_MANU, SEX, age_bucket, 'pulmonary_embolism', pulmonary_embolism FROM flags
    UNION ALL SELECT VAX_MANU, SEX, age_bucket, 'deep_vein_thrombosis', deep_vein_thrombosis FROM flags
    UNION ALL SELECT VAX_MANU, SEX, age_bucket, 'thrombosis_any', thrombosis_any FROM flags
    UNION ALL SELECT VAX_MANU, SEX, age_bucket, 'syncope', syncope FROM flags
    UNION ALL SELECT VAX_MANU, SEX, age_bucket, 'loss_of_consciousness', loss_of_consciousness FROM flags
)

SELECT
    u.event,
    u.VAX_MANU,
    u.SEX,
    u.age_bucket,
    SUM(u.flag) AS event_reports,
    t.total_reports,
    ROUND(100.0 * SUM(u.flag) / t.total_reports, 4) AS event_pct
FROM unpivoted u
JOIN totals t
  ON u.VAX_MANU = t.VAX_MANU
 AND coalesce(u.SEX, '') = coalesce(t.SEX, '')
 AND u.age_bucket = t.age_bucket
WHERE t.total_reports >= 500
GROUP BY u.event, u.VAX_MANU, u.SEX, u.age_bucket, t.total_reports
ORDER BY u.event, event_pct DESC
"""

df = con.execute(query).df()

print(df.to_string(index=False))

df.to_csv(
    r".\output\age_sex_specific_events.csv",
    index=False
)

con.close()
