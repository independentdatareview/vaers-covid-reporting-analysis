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

event_flags AS (
    SELECT
        VAERS_ID,
        VAX_MANU,

        MAX(CASE WHEN symptom LIKE '%myocarditis%'
                  OR symptom LIKE '%pericarditis%'
                 THEN 1 ELSE 0 END) AS cardiac_inflammation,

        MAX(CASE WHEN symptom LIKE '%cardiac arrest%'
                  OR symptom LIKE '%myocardial infarction%'
                  OR symptom LIKE '%heart attack%'
                 THEN 1 ELSE 0 END) AS acute_cardiac,

        MAX(CASE WHEN symptom LIKE '%pulmonary embolism%'
                  OR symptom LIKE '%deep vein thrombosis%'
                  OR symptom LIKE '%thrombosis%'
                  OR symptom LIKE '%thrombotic%'
                  OR symptom LIKE '%embolism%'
                 THEN 1 ELSE 0 END) AS clotting_embolic,

        MAX(CASE WHEN symptom LIKE '%cerebrovascular accident%'
                  OR symptom LIKE '%stroke%'
                  OR symptom LIKE '%ischaemic stroke%'
                  OR symptom LIKE '%haemorrhagic stroke%'
                 THEN 1 ELSE 0 END) AS stroke_related,

        MAX(CASE WHEN symptom LIKE '%guillain%'
                  OR symptom LIKE '%bell%'
                  OR symptom LIKE '%facial paralysis%'
                  OR symptom LIKE '%seizure%'
                  OR symptom LIKE '%syncope%'
                  OR symptom LIKE '%loss of consciousness%'
                  OR symptom LIKE '%tremor%'
                 THEN 1 ELSE 0 END) AS neuro_cluster,

        MAX(CASE WHEN symptom = 'death'
                 THEN 1 ELSE 0 END) AS death_symptom

    FROM symptom_events
    GROUP BY VAERS_ID, VAX_MANU
),

manufacturer_totals AS (
    SELECT
        VAX_MANU,
        COUNT(DISTINCT VAERS_ID) AS total_reports
    FROM covid_reports
    WHERE SOURCE_SCOPE='DOMESTIC'
    GROUP BY VAX_MANU
)

SELECT
    e.VAX_MANU,
    t.total_reports,

    SUM(cardiac_inflammation) AS cardiac_inflammation_reports,
    ROUND(100.0 * SUM(cardiac_inflammation) / t.total_reports, 3) AS cardiac_inflammation_pct,

    SUM(acute_cardiac) AS acute_cardiac_reports,
    ROUND(100.0 * SUM(acute_cardiac) / t.total_reports, 3) AS acute_cardiac_pct,

    SUM(clotting_embolic) AS clotting_embolic_reports,
    ROUND(100.0 * SUM(clotting_embolic) / t.total_reports, 3) AS clotting_embolic_pct,

    SUM(stroke_related) AS stroke_related_reports,
    ROUND(100.0 * SUM(stroke_related) / t.total_reports, 3) AS stroke_related_pct,

    SUM(neuro_cluster) AS neuro_cluster_reports,
    ROUND(100.0 * SUM(neuro_cluster) / t.total_reports, 3) AS neuro_cluster_pct,

    SUM(death_symptom) AS death_symptom_reports,
    ROUND(100.0 * SUM(death_symptom) / t.total_reports, 3) AS death_symptom_pct

FROM event_flags e
JOIN manufacturer_totals t
  ON e.VAX_MANU = t.VAX_MANU
GROUP BY e.VAX_MANU, t.total_reports
ORDER BY neuro_cluster_pct DESC
"""

df = con.execute(query).df()

print(df.to_string(index=False))

df.to_csv(
    r".\output\targeted_event_clusters_by_manufacturer.csv",
    index=False
)

con.close()
