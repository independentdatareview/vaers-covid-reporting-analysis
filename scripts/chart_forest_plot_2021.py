import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(r".")
INPUT = BASE / "output" / "logistic_regression_2021_results.csv"
OUT = BASE / "output" / "forest_plot_2021_odds_ratios.png"

df = pd.read_csv(INPUT)

# Keep only the main manufacturer signals
plot_rows = []

labels = {
    "myocarditis": "Myocarditis",
    "pericarditis": "Pericarditis",
    "guillain_barre": "Guillain-Barré",
    "cvst": "CVST",
    "pulmonary_embolism": "Pulmonary Embolism",
    "deep_vein_thrombosis": "Deep Vein Thrombosis",
    "thrombosis_any": "Any Thrombosis",
    "syncope": "Syncope",
    "loss_of_consciousness": "Loss of Consciousness",
}

for _, row in df.iterrows():
    term = row["term"]
    event = row["event"]

    if "PFIZER" in term and event in ["myocarditis", "pericarditis"]:
        manufacturer = "Pfizer vs Moderna"
    elif "JANSSEN" in term and event not in ["myocarditis", "pericarditis"]:
        manufacturer = "Janssen vs Moderna"
    else:
        continue

    plot_rows.append({
        "label": f"{labels.get(event, event)}\n{manufacturer}",
        "or": row["odds_ratio_vs_moderna"],
        "low": row["ci_95_low"],
        "high": row["ci_95_high"],
    })

plot_df = pd.DataFrame(plot_rows)

# Order by OR for readability
plot_df = plot_df.sort_values("or", ascending=True).reset_index(drop=True)

y = range(len(plot_df))

plt.figure(figsize=(10, 7))
plt.errorbar(
    plot_df["or"],
    y,
    xerr=[
        plot_df["or"] - plot_df["low"],
        plot_df["high"] - plot_df["or"]
    ],
    fmt="o",
    capsize=4
)

plt.axvline(1, linestyle="--")
plt.yticks(y, plot_df["label"])
plt.xscale("log")
plt.xlabel("Adjusted Odds Ratio vs Moderna (log scale)")
plt.title("2021 VAERS COVID Reporting Signals\nAge- and Sex-Adjusted Logistic Regression")
plt.tight_layout()

plt.savefig(OUT, dpi=300, bbox_inches="tight")
print(f"Saved chart: {OUT}")
