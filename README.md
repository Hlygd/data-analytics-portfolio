# Data Analytics Portfolio — Vishal Joshi

Three projects that turn 5 years of manufacturing quality-assurance data work into visible proof for data-analyst roles. Employers hiring for operations/quality analytics care less about certificates and more about "can this person find a signal in messy operational data and explain it." Each project maps 1:1 onto work genuinely done (SPC, NCR/SCAR, supplier quality, SAP QM data), rebuilt on synthetic data.

**Anonymization note:** all datasets here are synthetic, built to *resemble* the shape of real QA data. No real employer names, part numbers, customer names, or actual production data appear anywhere.

## Projects

### 1. SPC Process Monitoring — "Is the line in control?"
A stamping cell's critical dimension started drifting. Find when, flag it, and quantify capability.
- X-bar & R control charts (n=5), Western Electric rules, process capability Cp / Cpk vs. spec limits
- Deliverables: control-chart PNG, `subgroup_aggregates.sql` (the same math in SQL)
- Skills: SPC, Python (pandas, matplotlib), SQL
- [01-spc-process-monitoring](01-spc-process-monitoring/)

### 2. NCR Root-Cause Pareto — "Where is the cost of poor quality?"
Which defect modes and suppliers drive scrap/rework cost?
- Pareto of defect modes by cost (80/20 cut), defect rate by supplier, recommended-actions table
- Deliverables: Pareto chart PNG, data-driven recommendations table
- Skills: pandas, data storytelling, cost analysis
- [02-ncr-root-cause-pareto](02-ncr-root-cause-pareto/)

### 3. Supplier Quality Scorecard — "Who earns more business?"
Rank suppliers on quality + delivery for the quarter.
- Defect PPM, lot acceptance rate, on-time delivery %, composite score with weights
- Deliverables: scorecard visual, `scorecard.sql` (KPI queries verified to reproduce the Python numbers exactly)
- Skills: SQL, KPI design, BI reporting
- [03-supplier-quality-scorecard](03-supplier-quality-scorecard/)

## Repo shape

Each project keeps the same shape: `data/` (synthetic CSV) · `sql/` (the KPI queries) · `output/` (charts) · `README.md` (business question → method → findings → "so what").

## About

Vishal Joshi, PMP — Quality Assurance Specialist, Brampton ON. McMaster Data Analytics certificate (2023). Tools: SQL, Python (pandas), Power BI, Tableau, SAP QM/WMS, advanced Excel.
