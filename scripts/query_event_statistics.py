import duckdb
import pandas as pd
from math import log, exp, sqrt
from scipy.stats import fisher_exact

con = duckdb.connect(r".\vaers_covid.duckdb")

# Install scipy if needed:
# python -m pip install scipy

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
        lower(s.symptom) AS symptom
    FROM covid_reports r
    JOIN covid_symptom_long s
      ON r.VAERS_ID = s.VAERS_ID
    WHERE r.SOURCE_SCOPE='DOMESTIC'
      AND r.VAX_MANU IN ('JANSSEN','PFIZER\\BIONTECH','MODERNA')
),

flags AS (
    SELECT
        VAERS_ID,
        VAX_MANU,

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
    GROUP BY VAERS_ID, VAX_MANU
)

SELECT * FROM flags
"""

df = con.execute(query).df()
con.close()

comparisons = [
    ("JANSSEN", "PFIZER\\BIONTECH"),
    ("JANSSEN", "MODERNA"),
    ("PFIZER\\BIONTECH", "MODERNA"),
]

rows = []

for event in events:
    for a, b in comparisons:
        da = df[df["VAX_MANU"] == a]
        db = df[df["VAX_MANU"] == b]

        a_event = int(da[event].sum())
        a_total = int(len(da))
        a_non = a_total - a_event

        b_event = int(db[event].sum())
        b_total = int(len(db))
        b_non = b_total - b_event

        rate_a = a_event / a_total if a_total else 0
        rate_b = b_event / b_total if b_total else 0

        # Risk ratio with Wald CI on log scale
        rr = rate_a / rate_b if rate_b > 0 else float("inf")

        if a_event > 0 and b_event > 0:
            se = sqrt((1 / a_event) - (1 / a_total) + (1 / b_event) - (1 / b_total))
            ci_low = exp(log(rr) - 1.96 * se)
            ci_high = exp(log(rr) + 1.96 * se)
        else:
            ci_low = None
            ci_high = None

        # Fisher exact test
        _, p_value = fisher_exact([[a_event, a_non], [b_event, b_non]])

        rows.append({
            "event": event,
            "comparison": f"{a} vs {b}",
            "a": a,
            "b": b,
            "a_event": a_event,
            "a_total": a_total,
            "a_rate_pct": round(rate_a * 100, 4),
            "b_event": b_event,
            "b_total": b_total,
            "b_rate_pct": round(rate_b * 100, 4),
            "risk_ratio": round(rr, 3),
            "ci_95_low": round(ci_low, 3) if ci_low else None,
            "ci_95_high": round(ci_high, 3) if ci_high else None,
            "p_value": p_value,
        })

out = pd.DataFrame(rows)

print(out.to_string(index=False))

out.to_csv(
    r".\output\event_comparison_statistics.csv",
    index=False
)
