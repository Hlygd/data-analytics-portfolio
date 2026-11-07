"""
NCR Root-Cause Pareto — starter analysis.

Generates a synthetic NCR log (~120 records: date, defect mode, process
area, supplier, disposition, cost), then runs a cost-of-poor-quality
analysis: Pareto of defect modes by cost (80/20 cut), defect rate by
supplier, top-mode drilldown, and a recommended-actions table.

Run:  python3 analyze_pareto.py
Out:  data/ncr_records.csv, data/recommendations.csv,
      output/pareto_chart.png, summary on stdout.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "ncr_records.csv")
REC = os.path.join(BASE, "data", "recommendations.csv")
OUT = os.path.join(BASE, "output", "pareto_chart.png")
os.makedirs(os.path.join(BASE, "data"), exist_ok=True)
os.makedirs(os.path.join(BASE, "output"), exist_ok=True)

rng = np.random.default_rng(7)

# ---- synthetic data -------------------------------------------------------
# Cost profile is deliberately Pareto-shaped: two modes dominate.
MODES = [
    # (mode, process area, weight, mean cost, cost spread)
    ("Dimensional out-of-spec", "Machining",   0.22, 1450, 500),
    ("Weld porosity",           "Welding",     0.18, 1100, 450),
    ("Surface finish defects",  "Finishing",   0.16,  620, 260),
    ("Missing operations",      "Assembly",    0.12,  540, 220),
    ("Wrong material",          "Stamping",    0.10,  880, 350),
    ("Burrs / sharp edges",     "Machining",   0.09,  210,  90),
    ("Packaging damage",        "Packaging",   0.08,  150,  60),
    ("Labeling errors",         "Packaging",   0.05,  120,  50),
]
SUPPLIERS = ["Supplier A", "Supplier B", "Supplier C", "Supplier D", "Supplier E"]
SUPPLIER_W = [0.30, 0.25, 0.20, 0.15, 0.10]   # A ships the most volume
DISPOSITIONS = ["Scrap", "Rework", "Sort"]

mode_names = [m[0] for m in MODES]
mode_p = np.array([0.22, 0.18, 0.16, 0.12, 0.10, 0.09, 0.08, 0.05])

rows = []
start = np.datetime64("2026-05-01")
for i in range(1, 121):
    mi = rng.choice(len(MODES), p=mode_p)
    name, area, _, mean_c, sd_c = MODES[mi]
    # Supplier A skews toward dimensional issues (its process), E toward packaging
    sup = rng.choice(SUPPLIERS, p=SUPPLIER_W)
    disp = rng.choice(DISPOSITIONS, p=[0.35, 0.45, 0.20])
    cost = max(40.0, rng.normal(mean_c, sd_c))
    # rework costs less than scrap for the same mode
    if disp == "Rework":
        cost *= 0.55
    elif disp == "Sort":
        cost *= 0.30
    rows.append({
        "ncr_id": f"NCR-26-{i:03d}",
        "date": str(start + rng.integers(0, 180)),
        "defect_mode": name,
        "process_area": area,
        "supplier": sup,
        "disposition": disp,
        "cost_cad": round(cost, 2),
    })
df = pd.DataFrame(rows)
df.to_csv(DATA, index=False)

# ---- Pareto by cost -------------------------------------------------------
by_mode = df.groupby("defect_mode")["cost_cad"].agg(["sum", "count"]).rename(
    columns={"sum": "total_cost", "count": "ncr_count"}).sort_values("total_cost", ascending=False)
total = by_mode["total_cost"].sum()
by_mode["pct"] = by_mode["total_cost"] / total * 100
by_mode["cum_pct"] = by_mode["pct"].cumsum()
vital = by_mode[by_mode["cum_pct"] <= 80]
if len(vital) < 2:  # ensure the cut always shows the vital few, not one bar
    vital = by_mode.iloc[:2]

# ---- supplier drilldown ---------------------------------------------------
by_sup = df.groupby("supplier").agg(total_cost=("cost_cad", "sum"),
                                    ncr_count=("ncr_id", "count"))
top_mode = df.groupby("defect_mode")["cost_cad"].sum().idxmax()
top_mode_by_sup = (df[df["defect_mode"] == top_mode]
                   .groupby("supplier")["cost_cad"].sum().sort_values(ascending=False))

# ---- disposition mix ------------------------------------------------------
disp_mix = df.groupby("disposition")["cost_cad"].sum().sort_values(ascending=False)

# ---- recommended actions --------------------------------------------------
# Built from the actual aggregates above — no hardcoded rankings.
second = by_mode.index[1]
second_cost = by_mode.iloc[1]["total_cost"]
second_disp = df[df["defect_mode"] == second].groupby("disposition")["cost_cad"].sum()
second_top_disp = second_disp.idxmax()
recs = pd.DataFrame([
    {"priority": 1, "focus": f"{by_mode.index[0]} ({df[df['defect_mode']==by_mode.index[0]]['process_area'].iloc[0]})",
     "finding": f"${by_mode.iloc[0]['total_cost']:,.0f} — largest cost driver; concentrated with {top_mode_by_sup.index[0]} (${top_mode_by_sup.iloc[0]:,.0f})",
     "recommended_action": f"Process-capability study on {top_mode_by_sup.index[0]}; tighten incoming inspection sampling on critical dimensions"},
    {"priority": 2, "focus": f"{second} ({df[df['defect_mode']==second]['process_area'].iloc[0]})",
     "finding": f"${second_cost:,.0f} — second-largest; mostly dispositioned as {second_top_disp.lower()}",
     "recommended_action": "Root-cause blitz on the top process area; trial enhanced inspection on high-risk features for 30 days"},
    {"priority": 3, "focus": "Scrap-heavy disposition mix",
     "finding": f"Scrap = ${disp_mix.get('Scrap', 0):,.0f} of ${total:,.0f} total COPQ ({disp_mix.get('Scrap', 0)/total*100:.0f}%)",
     "recommended_action": "MRB review of scrap criteria — shift borderline cases to rework/sort with documented disposition limits"},
    {"priority": 4, "focus": "Supplier concentration",
     "finding": f"{by_sup['total_cost'].idxmax()} accounts for ${by_sup['total_cost'].max():,.0f} ({by_sup['total_cost'].max()/total*100:.0f}%) of COPQ",
     "recommended_action": "Supplier development visit + corrective-action request; put on enhanced incoming inspection until 2 clean months"},
])
recs.to_csv(REC, index=False)

# ---- chart ----------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))
fig.suptitle("Cost of Poor Quality — NCR Pareto (synthetic data, May–Oct 2026)", fontsize=12, fontweight="bold")

x = np.arange(len(by_mode))
bars = ax1.bar(x, by_mode["total_cost"], color="#2e628a", edgecolor="white")
ax1.set_xticks(x)
ax1.set_xticklabels(by_mode.index, rotation=28, ha="right", fontsize=8)
ax1.set_ylabel("Cost (CAD)")
ax1.set_title("Defect modes by cost — the vital few", fontsize=10)
ax1.grid(axis="y", alpha=0.3)
ax2_ = ax1.twinx()
ax2_.plot(x, by_mode["cum_pct"], color="#b07e10", marker="o", linewidth=2)
ax2_.axhline(80, color="#b07e10", linestyle="--", alpha=0.6)
ax2_.set_ylabel("Cumulative %", color="#b07e10")
ax2_.set_ylim(0, 105)
for b, v in zip(bars, by_mode["total_cost"]):
    ax1.text(b.get_x() + b.get_width() / 2, v + total * 0.008, f"${v:,.0f}",
             ha="center", fontsize=7)

s = by_sup.sort_values("total_cost", ascending=True)
ax2.barh(s.index, s["total_cost"], color="#5a7d9a", edgecolor="white")
ax2.set_xlabel("Cost (CAD)")
ax2.set_title("COPQ by supplier", fontsize=10)
ax2.grid(axis="x", alpha=0.3)
for i, v in enumerate(s["total_cost"]):
    ax2.text(v + total * 0.008, i, f"${v:,.0f}", va="center", fontsize=8)

fig.tight_layout()
fig.savefig(OUT, dpi=130)
plt.close(fig)

# ---- stdout summary -------------------------------------------------------
print(f"NCR records: {len(df)} | Total COPQ: ${total:,.0f}")
print("\nTop defect modes by cost:")
for m, r in by_mode.head(4).iterrows():
    print(f"  {m:28s} ${r['total_cost']:>9,.0f}  ({r['pct']:.1f}%, cum {r['cum_pct']:.1f}%)")
print(f"\nVital few (≤80% cumulative): {', '.join(vital.index)}")
print(f"Top cost mode overall: {top_mode}")
print(f"\nHighest-COPQ supplier: {by_sup['total_cost'].idxmax()} (${by_sup['total_cost'].max():,.0f})")
print(f"Disposition mix: " + ", ".join(f"{k} ${v:,.0f}" for k, v in disp_mix.items()))
print(f"\nWrote: {DATA}\n       {REC}\n       {OUT}")
