import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(r".")
INPUT = BASE / "output" / "specific_diagnosis_terms_by_manufacturer.csv"
OUT = BASE / "output" / "figure_04_neuro_cluster.png"

df = pd.read_csv(INPUT)

events = [
    "guillain_barre",
    "syncope",
    "loss_of_consciousness",
]

labels = {
    "guillain_barre": "Guillain-Barré",
    "syncope": "Syncope",
    "loss_of_consciousness": "Loss of Consciousness",
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
    df["event"].isin(events)
    & df["VAX_MANU"].isin(manufacturers)
].copy()

subset["event_label"] = subset["event"].map(labels)
subset["manufacturer_label"] = subset["VAX_MANU"].map(manufacturer_labels)

pivot = subset.pivot(
    index="event_label",
    columns="manufacturer_label",
    values="event_pct"
)

pivot = pivot.reindex([
    "Guillain-Barré",
    "Syncope",
    "Loss of Consciousness",
])

pivot = pivot[[
    "Moderna",
    "Pfizer/BioNTech",
    "Janssen",
]]

pivot.plot(kind="bar", figsize=(10,6))

plt.title("Neurological VAERS Symptom Terms by Manufacturer")
plt.ylabel("Percent of reports containing term")
plt.xlabel("Event category")
plt.xticks(rotation=15)
plt.legend(title="Manufacturer")
plt.tight_layout()

plt.savefig(OUT, dpi=300, bbox_inches="tight")
print(f"Saved: {OUT}")
