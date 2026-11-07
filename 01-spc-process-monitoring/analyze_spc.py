"""
SPC Process Monitoring — starter analysis.

Generates a synthetic dataset (30 subgroups x 5 measurements of a critical
dimension on a stamping cell), computes X-bar & R control limits, applies
Western Electric rules, and estimates process capability (Cp/Cpk).

Run:  python3 analyze_spc.py
Out:  data/spc_measurements.csv, output/xbar_r_chart.png, summary on stdout.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "spc_measurements.csv")
OUT = os.path.join(BASE, "output", "xbar_r_chart.png")

rng = np.random.default_rng(42)

# ---- synthetic data -------------------------------------------------------
N_SUBGROUPS, N = 30, 5
TARGET, WITHIN_SIGMA = 25.00, 0.03
USL, LSL = 25.10, 24.90

rows = []
for g in range(1, N_SUBGROUPS + 1):
    shift = 0.06 if g >= 20 else 0.0          # process mean shift, late in run
    spike = 0.12 if g == 12 else 0.0          # one-off out-of-control event
    for p in range(1, N + 1):
        rows.append((g, p, TARGET + shift + spike + rng.normal(0, WITHIN_SIGMA)))
df = pd.DataFrame(rows, columns=["subgroup", "part", "measurement"])
df.to_csv(DATA, index=False)

# ---- control chart statistics --------------------------------------------
# Phase 1 / Phase 2 practice: establish limits from the stable baseline
# (subgroups 1-11 and 13-19), excluding the subgroup-12 spike and the
# post-shift run (20+). Then judge every subgroup against those limits.
A2, D3, D4, D2 = 0.577, 0.0, 2.114, 2.326
grp = df.groupby("subgroup")["measurement"]
xbar = grp.mean()
r = grp.max() - grp.min()

baseline = [g for g in xbar.index if g < 20 and g != 12]
xbarbar = xbar.loc[baseline].mean()
rbar = r.loc[baseline].mean()

ucl_x, lcl_x = xbarbar + A2 * rbar, xbarbar - A2 * rbar
ucl_r, lcl_r = D4 * rbar, D3 * rbar
sig_x = (ucl_x - xbarbar) / 3.0

# ---- Western Electric rules (X-bar chart) ---------------------------------
flags = {g: [] for g in xbar.index}
z = (xbar - xbarbar) / sig_x
for g in xbar.index:
    if abs(z[g]) > 3:
        flags[g].append("Rule 1: beyond 3-sigma")
for g in range(1, N_SUBGROUPS - 1):
    window = z.iloc[g - 1:g + 2]
    if ((window > 2).sum() >= 2) or ((window < -2).sum() >= 2):
        flags[g + 1].append("Rule 2: 2 of 3 beyond 2-sigma, same side")
signs = np.sign(z.values)
for g in range(8, N_SUBGROUPS + 1):
    if np.all(signs[g - 8:g] == signs[g - 8]) and signs[g - 8] != 0:
        flags[g].append("Rule 4: 8 consecutive, same side of centerline")

# ---- capability ------------------------------------------------------------
sigma = rbar / D2
cp = (USL - LSL) / (6 * sigma)
cpk = min(USL - xbarbar, xbarbar - LSL) / (3 * sigma)

# ---- chart -----------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
fig.suptitle("Stamping Cell — Critical Dimension (mm)\nX-bar & R Chart, n=5", fontsize=14, fontweight="bold")

xs = xbar.index.values
ax1.plot(xs, xbar.values, "o-", color="#1f3a5f", ms=5)
ax1.axhline(xbarbar, color="green", ls="--", label=f"CL {xbarbar:.4f}")
ax1.axhline(ucl_x, color="red", ls=":", label=f"UCL {ucl_x:.4f}")
ax1.axhline(lcl_x, color="red", ls=":", label=f"LCL {lcl_x:.4f}")
flagged = [g for g in xs if flags[g]]
if flagged:
    ax1.plot(flagged, xbar.loc[flagged], "o", color="red", ms=9, label="Rule violation")
ax1.set_ylabel("Subgroup mean")
ax1.legend(fontsize=9, loc="best")
ax1.grid(alpha=0.3)

ax2.plot(xs, r.values, "o-", color="#1f3a5f", ms=5)
ax2.axhline(rbar, color="green", ls="--", label=f"CL {rbar:.4f}")
ax2.axhline(ucl_r, color="red", ls=":", label=f"UCL {ucl_r:.4f}")
ax2.set_ylabel("Subgroup range")
ax2.set_xlabel("Subgroup")
ax2.legend(fontsize=9, loc="best")
ax2.grid(alpha=0.3)

fig.tight_layout()
fig.savefig(OUT, dpi=150)
print(f"chart -> {OUT}")

# ---- summary ----------------------------------------------------------------
print(f"\nSubgroups: {N_SUBGROUPS} x {N} | X-double-bar: {xbarbar:.4f} | R-bar: {rbar:.4f}")
print(f"Cp: {cp:.2f} | Cpk: {cpk:.2f} (spec {LSL:.2f}–{USL:.2f})")
print("\nRule violations:")
any_flag = False
for g in sorted(flagged):
    any_flag = True
    print(f"  subgroup {g:2d}  mean={xbar[g]:.4f}  :: {'; '.join(flags[g])}")
if not any_flag:
    print("  none — process in statistical control")
