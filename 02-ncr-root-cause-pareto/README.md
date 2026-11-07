# Project 2 — NCR Root-Cause Pareto

**Business question:** Which defect modes and suppliers drive scrap and rework cost — and where should corrective action start?

**Method:** Pareto analysis of cost-of-poor-quality (COPQ) across ~120 NCR records: defect modes ranked by total cost with an 80% cumulative cut ("the vital few"), supplier drilldown on the top mode, and disposition-mix analysis. Recommendations in `data/recommendations.csv` are generated from the actual aggregates — no hardcoded rankings.

**Data:** `data/ncr_records.csv` — 120 records (date, defect mode, process area, supplier, disposition, cost). **Synthetic**: built to resemble real NCR data; no employer data was used.

## Findings
- **Three modes carry 78% of the cost:** Dimensional out-of-spec ($23,637), Wrong material ($12,994), Weld porosity ($10,904). The other five modes combined are noise by comparison.
- **Dimensional issues concentrate with Supplier A** ($9,940 of the $23,637) — a supplier problem more than a process problem.
- **Scrap is 53% of COPQ** ($32,536 of $60,974). Over half the cost is material thrown away, not reworked.
- **Supplier C is the costliest overall** ($17,603, 29% of COPQ) despite not leading any single defect mode — death by a thousand cuts.

## So what (the part hiring managers care about)
Pareto turns a 120-row complaint log into a one-page action plan: fix Supplier A's dimensional capability, blitz wrong-material controls in Stamping, and put Supplier C on a development plan. The scrap finding is the money slide — every point of scrap converted to rework or sort is margin recovered. That's the language operations managers speak: cost, not charts.

## Run it
```
python3 analyze_pareto.py        # regenerates data, recommendations -> data/, chart -> output/pareto_chart.png
```
Requires: Python 3, pandas, matplotlib, numpy.
