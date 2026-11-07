# Project 1 — SPC Process Monitoring

**Business question:** A stamping cell's critical dimension (target 25.00 mm, tolerance ±0.10) started drifting. When did it shift, and is the process still capable?

**Method:** X-bar & R control charts (subgroup size n=5), Western Electric rules, and Cp/Cpk capability vs. spec limits. Control limits were established from the stable baseline (Phase 1 practice: subgroups 1–11, 13–19), then applied to all 30 subgroups. SQL in `sql/` reproduces the subgroup aggregates.

**Data:** `data/spc_measurements.csv` — 30 subgroups × 5 measurements. **Synthetic**: built to resemble real SPC data; no employer data was used.

## Findings
- **Baseline is healthy:** subgroups 1–11 and 13–19 are in statistical control. Cp = 1.51, Cpk = 1.50 — a capable, centered process.
- **Subgroup 12 — one-off spike** (Rule 1: beyond 3σ, mean 25.1241). Classic assignable cause: worth a logbook check (tool change? material lot?) but not a process redesign.
- **Subgroups 20–30 — sustained mean shift** (Rule 1 + Rule 2 + Rule 4 violations on nearly every subgroup). The process moved ~+0.06 mm and never came back. This is the real story: something changed at subgroup 20 and it stuck.

## So what (the part hiring managers care about)
The chart separates noise from signal: one bad subgroup is an event; eleven consecutive out-of-control subgroups are a new process. The right response isn't "inspect harder" — it's "find what changed at subgroup 20" (die wear, fixture, setup) and re-baseline after the fix. Note Cpk was computed on the baseline only — capability claims are meaningless once the process has shifted.

## Run it
```
python3 analyze_spc.py        # regenerates data, chart -> output/xbar_r_chart.png
```
Requires: Python 3, pandas, matplotlib, numpy.
