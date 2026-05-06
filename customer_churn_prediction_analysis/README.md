
# Customer Churn Prediction & Analysis

A complete end-to-end data analyst / data science portfolio project with synthetic customer data, EDA, SQL-style churn-driver analysis, machine-learning training scripts, and a professional Streamlit dashboard.

## Business Goal
Identify high-risk customers, quantify annual revenue at risk, and explain churn drivers so the retention team can prioritize outreach.

## Project Structure
```text
customer_churn_prediction_analysis/
├── data/customer_churn_data.csv
├── src/train_churn_model.py
├── src/churn_driver_queries.sql
├── dashboard/app.py
├── models/
├── requirements.txt
└── README.md
```

## How to Run
```bash
pip install -r requirements.txt
python src/train_churn_model.py
streamlit run dashboard/app.py
```

## Dashboard Pages / Visuals
- Executive KPI cards: customers, churn rate, revenue, annual revenue at risk
- Churn by contract type
- Tenure distribution by churn status
- Churn heatmap by payment method and internet service
- Customer risk scatter map
- Retention priority table

## Modeling
The training script compares Logistic Regression and Random Forest using Accuracy, ROC AUC, Confusion Matrix, and Classification Report. The best model is saved under `models/churn_model.joblib`.
