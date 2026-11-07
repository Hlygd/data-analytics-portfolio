-- Subgroup aggregates for the SPC dataset (n = 5).
-- Same math as analyze_spc.py, in SQL. Swap the FROM for your own table.
WITH subgroups AS (
    SELECT
        subgroup,
        AVG(measurement)              AS xbar,
        MAX(measurement) - MIN(measurement) AS r
    FROM spc_measurements
    GROUP BY subgroup
),
overall AS (
    SELECT AVG(xbar) AS xbarbar, AVG(r) AS rbar FROM subgroups
)
SELECT
    s.subgroup,
    ROUND(s.xbar, 4) AS subgroup_mean,
    ROUND(s.r, 4)    AS subgroup_range,
    ROUND(o.xbarbar + 0.577 * o.rbar, 4) AS ucl_x,
    ROUND(o.xbarbar - 0.577 * o.rbar, 4) AS lcl_x,
    ROUND(2.114 * o.rbar, 4)             AS ucl_r,
    CASE
        WHEN ABS(s.xbar - o.xbarbar) > 3 * (0.577 * o.rbar / 3) THEN 'RULE 1 VIOLATION'
        ELSE 'in control'
    END AS rule_1_check
FROM subgroups s CROSS JOIN overall o
ORDER BY s.subgroup;
