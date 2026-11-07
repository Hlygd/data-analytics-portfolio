# Project 3 — Supplier Quality Scorecard

**Business question:** Which suppliers earn more business next quarter — and which ones need a corrective-action plan?

**Method:** Standard supplier KPIs from an incoming-inspection log — defect PPM, lot acceptance rate, on-time delivery % — rolled into a weighted composite score (quality 50%, delivery 30%, acceptance 20%) with Preferred / Approved / Conditional ratings. Monthly trends show who is improving and who is slipping. The same KPI math is reproduced in SQL (`sql/scorecard.sql`, verified to match the Python output exactly).

**Data:** `data/inspection_log.csv` — 6 suppliers × 3 months (lots received, rejected lots, defective units, late lots). **Synthetic**: built to resemble real incoming-inspection data; no employer data was used.

## Findings
- **Supplier A (96) and B (94) are Preferred** — low PPM, high acceptance, solid delivery. These earn more volume.
- **Supplier D is Conditional (54)** — 14,392 PPM, nearly 12% lot rejection. This is SCAR territory, not a scorecard debate.
- **Supplier E is the interesting case:** quality is fine (872 PPM) but on-time delivery is 84% — a logistics problem wearing a quality costume. Fix the delivery, keep the volume.
- **Supplier F is the watch item:** composite slid 82 → 56 across the quarter. Deteriorating suppliers are how you get surprise line-stops — this one needs a development visit now, not next quarter.

## So what (the part hiring managers care about)
Scorecards are the staple BI artifact of operations analytics — every analyst builds or consumes them. This one shows the full loop: raw inspection data → KPIs → a single composite a buyer can act on → the trend that catches problems before they become line-stops. The Supplier E finding is the interview story: the scorecard separates *what kind* of problem each supplier has, so the fix matches the cause.

## Run it
```
python3 analyze_scorecard.py        # regenerates data, scorecard -> data/, chart -> output/scorecard.png
```
Requires: Python 3, pandas, matplotlib, numpy.
