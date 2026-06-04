import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(r".")
INPUT = BASE / "output" / "event_time_series_by_quarter.csv"
OUT = BASE / "output" / "figure_05_2021_time_series.png"

df = pd.read_csv(INPUT)

events = [
    "myocarditis",
    "cvst",
    "guillain_barre",
    "thrombosis_any",
]

event_labels = {
    "myocarditis": "Myocarditis",
    "cvst": "CVST",
    "guillain_barre": "Guillain-Barré",
    "thrombosis_any": "Any Thrombosis",
}

manufacturers = [
    "MODERNA",
    "PFIZER\\BIONTECH",
    "JANSSEN",
]

manufacturer_labels = {
    "MODERNA": "Moderna",
    "PFIZER\\BIONTECH": "Pfizer/BioNTech",
    "JANSSEN": "Janssen",
}

subset = df[
    (df["year"] == 2021)
    & df["event"].isin(events)
    & df["VAX_MANU"].isin(manufacturers)
].copy()

subset["period"] = subset["year"].astype(str) + " Q" + subset["quarter"].astype(str)
subset["event_label"] = subset["event"].map(event_labels)
subset["manufacturer_label"] = subset["VAX_MANU"].map(manufacturer_labels)

for event in events:
    event_name = event_labels[event]
    event_df = subset[subset["event"] == event].copy()

    pivot = event_df.pivot(
        index="period",
        columns="manufacturer_label",
        values="event_pct"
    )

    pivot = pivot.reindex(["2021 Q1", "2021 Q2", "2021 Q3", "2021 Q4"])

    pivot = pivot[[
        "Moderna",
        "Pfizer/BioNTech",
        "Janssen",
    ]]

    plt.figure(figsize=(9, 5))
    pivot.plot(marker="o")

    plt.title(f"{event_name} VAERS Reporting Pattern by Quarter, 2021")
    plt.ylabel("Percent of reports containing term")
    plt.xlabel("Quarter")
    plt.tight_layout()

    event_out = BASE / "output" / f"figure_05_time_series_{event}.png"
    plt.savefig(event_out, dpi=300, bbox_inches="tight")
    print(f"Saved: {event_out}")
    plt.close()
