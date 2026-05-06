
-- Customer churn risk and driver analysis
WITH customer_features AS (
    SELECT
        customer_id,
        contract_type,
        payment_method,
        internet_service,
        tenure_months,
        monthly_charges,
        support_tickets_90d,
        late_payments_12m,
        CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END AS churn_flag
    FROM customer_churn_data
), risk_segments AS (
    SELECT *,
        CASE
            WHEN tenure_months < 12 AND contract_type = 'Month-to-month' THEN 'New high-risk'
            WHEN support_tickets_90d >= 3 OR late_payments_12m >= 2 THEN 'Service/payment risk'
            WHEN monthly_charges >= 85 THEN 'High-value risk'
            ELSE 'Stable'
        END AS risk_segment
    FROM customer_features
)
SELECT
    risk_segment,
    COUNT(*) AS customers,
    ROUND(AVG(churn_flag) * 100, 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges
FROM risk_segments
GROUP BY risk_segment
ORDER BY churn_rate_pct DESC;
