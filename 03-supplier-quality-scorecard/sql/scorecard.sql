-- Supplier Quality Scorecard — KPI queries.
-- Run against data/inspection_log.csv loaded as table inspection_log
-- (supplier, month, lots_received, rejected_lots, defective_units, late_lots).
-- Same math as analyze_scorecard.py. SQLite / Postgres compatible.

-- 1) Monthly KPIs per supplier ----------------------------------------------
WITH monthly AS (
    SELECT
        supplier,
        month,
        SUM(lots_received)  AS lots,
        SUM(rejected_lots)  AS rej_lots,
        SUM(defective_units) AS def_units,
        SUM(late_lots)      AS late_lots
    FROM inspection_log
    GROUP BY supplier, month
),
kpis AS (
    SELECT
        supplier,
        month,
        lots,
        -- defect PPM: defective units per million received (1000 units/lot)
        ROUND(def_units * 1000000.0 / (lots * 1000), 1) AS ppm,
        -- lot acceptance rate %
        ROUND((lots - rej_lots) * 100.0 / lots, 1)      AS accept_rate,
        -- on-time delivery %
        ROUND((lots - late_lots) * 100.0 / lots, 1)     AS otd
    FROM monthly
),
scored AS (
    SELECT
        supplier,
        month,
        lots, ppm, accept_rate, otd,
        -- composite: quality 50% + delivery 30% + acceptance 20% (each 0-100)
        ROUND(
            0.5 * MAX(0.0, 100.0 - ppm / 150.0)
          + 0.3 * otd
          + 0.2 * accept_rate, 1) AS composite
    FROM kpis
)
-- 2) Quarterly scorecard -----------------------------------------------------
SELECT
    supplier,
    SUM(lots)             AS total_lots,
    ROUND(AVG(ppm), 1)    AS avg_ppm,
    ROUND(AVG(accept_rate), 1) AS avg_accept_rate,
    ROUND(AVG(otd), 1)    AS avg_otd,
    ROUND(AVG(composite), 1)   AS composite,
    CASE
        WHEN AVG(composite) >= 85 THEN 'Preferred'
        WHEN AVG(composite) >= 70 THEN 'Approved'
        ELSE 'Conditional'
    END                   AS rating
FROM scored
GROUP BY supplier
ORDER BY composite DESC;

-- 3) Monthly trend (who is improving, who is slipping) ------------------------
-- SELECT supplier, month, composite FROM scored ORDER BY supplier, month;
