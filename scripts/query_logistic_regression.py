import duckdb
import pandas as pd
import statsmodels.formula.api as smf

con = duckdb.connect(r".\vaers_covid.duckdb")

events = [
    "myocarditis",
    "pericarditis",
    "guillain_barre",
    "cvst",
    "pulmonary_embolism",
    "deep_vein_thrombosis",
    "thrombosis_any",
    "syncope",
    "loss_of_consciousness",
]

query = """
WITH symptom_events AS (
    SELECT
        r.VAERS_ID,
        r.VAX_MANU,
        r.STATE,
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
      AND r.VAX_MANU IN ('JANSSEN','PFIZER\\BIONTECH','MODERNA')
      AND r.STATE IS NOT NULL
      AND r.SEX IN ('M','F')
),

flags AS (
    SELECT
        VAERS_ID,
        VAX_MANU,
        STATE,
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
    GROUP BY VAERS_ID, VAX_MANU, STATE, SEX, age_bucket
)

SELECT *
FROM flags
"""

df = con.execute(query).df()
con.close()

# Use Moderna as reference manufacturer, because it was lowest in the adjusted serious-event analysis.
df["VAX_MANU"] = pd.Categorical(
    df["VAX_MANU"],
    categories=["MODERNA", "PFIZER\\BIONTECH", "JANSSEN"]
)

results = []

for event in events:
    print("\n" + "=" * 80)
    print(f"EVENT: {event}")
    print("=" * 80)

    formula = f"{event} ~ C(VAX_MANU) + C(age_bucket) + C(SEX) + C(STATE)"

    try:
        model = smf.logit(formula=formula, data=df).fit(disp=False, maxiter=100)

        params = model.params
        conf = model.conf_int()
        pvals = model.pvalues

        for term in params.index:
            if term.startswith("C(VAX_MANU)"):
                odds_ratio = float(pd.np.exp(params[term]))
                ci_low = float(pd.np.exp(conf.loc[term, 0]))
                ci_high = float(pd.np.exp(conf.loc[term, 1]))

                row = {
                    "event": event,
                    "term": term,
                    "odds_ratio_vs_moderna": round(odds_ratio, 3),
                    "ci_95_low": round(ci_low, 3),
                    "ci_95_high": round(ci_high, 3),
                    "p_value": pvals[term],
                }

                results.append(row)

        event_results = pd.DataFrame([r for r in results if r["event"] == event])
        print(event_results.to_string(index=False))

    except Exception as e:
        print(f"Model failed for {event}: {e}")

out = pd.DataFrame(results)

out.to_csv(
    r".\output\logistic_regression_event_results.csv",
    index=False
)

print("\nSaved:")
print(r".\output\logistic_regression_event_results.csv")
