"""
Supplier Quality Scorecard — starter analysis.

Generates a synthetic incoming-inspection log (6 suppliers x 3 months:
lots received, rejected lots, defective units, late lots), computes the
standard supplier KPIs (defect PPM, lot acceptance rate, on-time delivery)
and a weighted composite score, then renders a quarterly scorecard chart
with monthly trends.

Run:  python3 analyze_scorecard.py
Out:  data/inspection_log.csv, data/scorecard.csv,
      output/scorecard.png, summary on stdout.

The same KPI math is reproduced in SQL in sql/scorecard.sql.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "inspection_log.csv")
SCORECARD = os.path.join(BASE, "data", "scorecard.csv")
OUT = os.path.join(BASE, "output", "scorecard.png")
os.makedirs(os.path.join(BASE, "data"), exist_ok=True)
os.makedirs(os.path.join(BASE, "output"), exist_ok=True)

rng = np.random.default_rng(21)
UNITS_PER_LOT = 1000
MONTHS = ["2026-08", "2026-09", "2026-10"]

# supplier quality profiles: (reject_rate, late_rate, defect_units_per_rejected_lot)
PROFILES = {
    "Supplier A": (0.020, 0.020, 28),    # excellent
    "Supplier B": (0.045, 0.040, 45),    # good
    "Supplier C": (0.085, 0.060, 70),    # mediocre
    "Supplier D": (0.160, 0.050, 120),   # poor quality
    "Supplier E": (0.035, 0.170, 40),    # good quality, chronic lateness
    "Supplier F": (0.050, 0.050, 55),    # starts OK, deteriorates (trend injected below)
}

rows = []
for sup, (rej_r, late_r, def_u) in PROFILES.items():
    for mi, month in enumerate(MONTHS):
        # Supplier F deteriorates across the quarter; D improves slightly after a SCAR
        rr, lr = rej_r, late_r
        if sup == "Supplier F":
            rr, lr = rej_r * (1 + mi * 0.9), late_r * (1 + mi * 0.5)
        if sup == "Supplier D" and mi == 2:
            rr = rej_r * 0.55
        lots = int(rng.integers(28, 46))
        rejected_lots = int(rng.binomial(lots, min(rr, 0.35)))
        late_lots = int(rng.binomial(lots, min(lr, 0.40)))
        defective_units = int(rejected_lots * max(def_u + rng.integers(-12, 13), 5))
        rows.append({"supplier": sup, "month": month, "lots_received": lots,
                     "rejected_lots": rejected_lots, "defective_units": defective_units,
                     "late_lots": late_lots})
df = pd.DataFrame(rows)
df.to_csv(DATA, index=False)

# ---- KPIs -----------------------------------------------------------------
g = df.groupby(["supplier", "month"]).agg(
    lots=("lots_received", "sum"), rej_lots=("rejected_lots", "sum"),
    def_units=("defective_units", "sum"), late=("late_lots", "sum")).reset_index()
g["ppm"] = g["def_units"] / (g["lots"] * UNITS_PER_LOT) * 1e6
g["accept_rate"] = (g["lots"] - g["rej_lots"]) / g["lots"] * 100
g["otd"] = (g["lots"] - g["late"]) / g["lots"] * 100


def composite(r):
    # quality 50% + delivery 30% + acceptance 20%, each 0-100
    s_ppm = max(0.0, 100.0 - r["ppm"] / 150.0)
    return round(0.5 * s_ppm + 0.3 * r["otd"] + 0.2 * r["accept_rate"], 1)


g["composite"] = g.apply(composite, axis=1)

q = g.groupby("supplier").agg(
    lots=("lots", "sum"), ppm=("ppm", "mean"), accept_rate=("accept_rate", "mean"),
    otd=("otd", "mean"), composite=("composite", "mean")).round(1)
q = q.sort_values("composite", ascending=False)


def rating(s):
    return "Preferred" if s >= 85 else ("Approved" if s >= 70 else "Conditional")


q["rating"] = q["composite"].apply(rating)
q.to_csv(SCORECARD)

# ---- chart ----------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.4))
fig.suptitle("Supplier Quality Scorecard — Q3 2026 (synthetic data)", fontsize=12, fontweight="bold")

colors = {"Preferred": "#2e7d4f", "Approved": "#b07e10", "Conditional": "#b3402e"}
bars = ax1.barh(q.index, q["composite"], color=[colors[r] for r in q["rating"]], edgecolor="white")
ax1.set_xlim(0, 100)
ax1.set_xlabel("Composite score (quality 50% · delivery 30% · acceptance 20%)")
ax1.set_title("Quarterly scorecard", fontsize=10)
ax1.grid(axis="x", alpha=0.3)
for b, v, r in zip(bars, q["composite"], q["rating"]):
    ax1.text(v + 1, b.get_y() + b.get_height() / 2, f"{v:.0f} · {r}", va="center", fontsize=8)

for sup in g["supplier"].unique():
    s = g[g["supplier"] == sup].sort_values("month")
    ax2.plot(s["month"], s["composite"], marker="o", label=sup, linewidth=2)
ax2.set_ylim(0, 105)
ax2.set_ylabel("Composite score")
ax2.set_title("Monthly trend — who is improving, who is slipping", fontsize=10)
ax2.legend(fontsize=7, loc="lower left", ncol=2)
ax2.grid(alpha=0.3)

fig.tight_layout()
fig.savefig(OUT, dpi=130)
plt.close(fig)

# ---- stdout summary -------------------------------------------------------
print("Quarterly supplier scorecard (Q3 2026):")
print(q[["ppm", "accept_rate", "otd", "composite", "rating"]].to_string())
print(f"\nWrote: {DATA}\n       {SCORECARD}\n       {OUT}")
print("\nHeadlines:")
print(f"  Best overall: {q.index[0]} (composite {q.iloc[0]['composite']:.0f}, {q.iloc[0]['rating']})")
print(f"  Worst overall: {q.index[-1]} (composite {q.iloc[-1]['composite']:.0f}, {q.iloc[-1]['rating']})")
f_trend = g[g["supplier"] == "Supplier F"].sort_values("month")["composite"].tolist()
print(f"  Watch item: Supplier F deteriorating {f_trend[0]:.0f} → {f_trend[-1]:.0f} across the quarter")
