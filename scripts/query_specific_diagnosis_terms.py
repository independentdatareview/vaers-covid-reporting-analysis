import duckdb

con = duckdb.connect(r".\vaers_covid.duckdb")

query = """
WITH symptom_events AS (
    SELECT
        r.VAERS_ID,
        r.VAX_MANU,
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

        MAX(CASE WHEN symptom LIKE '%myocarditis%' THEN 1 ELSE 0 END) AS myocarditis,
        MAX(CASE WHEN symptom LIKE '%pericarditis%' THEN 1 ELSE 0 END) AS pericarditis,
        MAX(CASE WHEN symptom LIKE '%cardiac arrest%' THEN 1 ELSE 0 END) AS cardiac_arrest,
        MAX(CASE WHEN symptom LIKE '%myocardial infarction%' THEN 1 ELSE 0 END) AS myocardial_infarction,

        MAX(CASE WHEN symptom LIKE '%pulmonary embolism%' THEN 1 ELSE 0 END) AS pulmonary_embolism,
        MAX(CASE WHEN symptom LIKE '%deep vein thrombosis%' THEN 1 ELSE 0 END) AS deep_vein_thrombosis,
        MAX(CASE WHEN symptom LIKE '%cerebral venous sinus thrombosis%' THEN 1 ELSE 0 END) AS cvst,
        MAX(CASE WHEN symptom LIKE '%thrombosis%' THEN 1 ELSE 0 END) AS thrombosis_any,

        MAX(CASE WHEN symptom LIKE '%cerebrovascular accident%' THEN 1 ELSE 0 END) AS cerebrovascular_accident,
        MAX(CASE WHEN symptom LIKE '%ischaemic stroke%' THEN 1 ELSE 0 END) AS ischaemic_stroke,
        MAX(CASE WHEN symptom LIKE '%haemorrhagic stroke%' THEN 1 ELSE 0 END) AS haemorrhagic_stroke,

        MAX(CASE WHEN symptom LIKE '%guillain%' THEN 1 ELSE 0 END) AS guillain_barre,
        MAX(CASE WHEN symptom LIKE '%bell%' THEN 1 ELSE 0 END) AS bells_palsy,
        MAX(CASE WHEN symptom LIKE '%seizure%' THEN 1 ELSE 0 END) AS seizure,
        MAX(CASE WHEN symptom LIKE '%syncope%' THEN 1 ELSE 0 END) AS syncope,
        MAX(CASE WHEN symptom LIKE '%loss of consciousness%' THEN 1 ELSE 0 END) AS loss_of_consciousness,

        MAX(CASE WHEN symptom = 'death' THEN 1 ELSE 0 END) AS death_symptom

    FROM symptom_events
    GROUP BY VAERS_ID, VAX_MANU
),

totals AS (
    SELECT
        VAX_MANU,
        COUNT(DISTINCT VAERS_ID) AS total_reports
    FROM covid_reports
    WHERE SOURCE_SCOPE='DOMESTIC'
    GROUP BY VAX_MANU
),

unpivoted AS (
    SELECT VAX_MANU, 'myocarditis' AS event, myocarditis AS flag FROM flags
    UNION ALL SELECT VAX_MANU, 'pericarditis', pericarditis FROM flags
    UNION ALL SELECT VAX_MANU, 'cardiac_arrest', cardiac_arrest FROM flags
    UNION ALL SELECT VAX_MANU, 'myocardial_infarction', myocardial_infarction FROM flags
    UNION ALL SELECT VAX_MANU, 'pulmonary_embolism', pulmonary_embolism FROM flags
    UNION ALL SELECT VAX_MANU, 'deep_vein_thrombosis', deep_vein_thrombosis FROM flags
    UNION ALL SELECT VAX_MANU, 'cvst', cvst FROM flags
    UNION ALL SELECT VAX_MANU, 'thrombosis_any', thrombosis_any FROM flags
    UNION ALL SELECT VAX_MANU, 'cerebrovascular_accident', cerebrovascular_accident FROM flags
    UNION ALL SELECT VAX_MANU, 'ischaemic_stroke', ischaemic_stroke FROM flags
    UNION ALL SELECT VAX_MANU, 'haemorrhagic_stroke', haemorrhagic_stroke FROM flags
    UNION ALL SELECT VAX_MANU, 'guillain_barre', guillain_barre FROM flags
    UNION ALL SELECT VAX_MANU, 'bells_palsy', bells_palsy FROM flags
    UNION ALL SELECT VAX_MANU, 'seizure', seizure FROM flags
    UNION ALL SELECT VAX_MANU, 'syncope', syncope FROM flags
    UNION ALL SELECT VAX_MANU, 'loss_of_consciousness', loss_of_consciousness FROM flags
    UNION ALL SELECT VAX_MANU, 'death_symptom', death_symptom FROM flags
)

SELECT
    u.VAX_MANU,
    u.event,
    SUM(u.flag) AS event_reports,
    t.total_reports,
    ROUND(100.0 * SUM(u.flag) / t.total_reports, 4) AS event_pct
FROM unpivoted u
JOIN totals t
  ON u.VAX_MANU = t.VAX_MANU
GROUP BY u.VAX_MANU, u.event, t.total_reports
ORDER BY u.event, event_pct DESC
"""

df = con.execute(query).df()

print(df.to_string(index=False))

df.to_csv(
    r".\output\specific_diagnosis_terms_by_manufacturer.csv",
    index=False
)

con.close()
