import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Customer Churn Command Center", page_icon="🛰️", layout="wide")
ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(ROOT, "data", "customer_churn_data.csv")

df = pd.read_csv(DATA_PATH)
df["churn_flag"] = (df["churn"] == "Yes").astype(int)
df["estimated_revenue_at_risk"] = df["monthly_charges"] * 12 * df["churn_flag"]
df["customer_value_band"] = pd.qcut(df["monthly_charges"], q=4, labels=["Value", "Core", "Premium", "Elite"])
df["tenure_stage"] = pd.cut(df["tenure_months"], bins=[0, 6, 18, 36, 72], labels=["New", "Growing", "Established", "Loyal"])
df["risk_score"] = (
    df["support_tickets_90d"] * 9
    + df["late_payments_12m"] * 11
    + df["contract_type"].eq("Month-to-month") * 22
    + df["internet_service"].eq("Fiber optic") * 8
    + (df["tenure_months"] < 12) * 13
    + df["value_added_services"].eq("No") * 7
).clip(0, 100)
df["risk_tier"] = pd.cut(df["risk_score"], bins=[-1, 35, 65, 101], labels=["Low", "Medium", "High"])

THEME = ["#6C63FF", "#00D4FF", "#FF4B4B", "#21E6C1", "#FFD166", "#B5179E"]

st.markdown(
    """
    <style>
    .stApp {background: radial-gradient(circle at top left, #151a33 0%, #0b1020 42%, #08090f 100%); color: #F8FAFC;}
    section[data-testid="stSidebar"] {background: linear-gradient(180deg, #111827 0%, #1F2937 100%); border-right: 1px solid #334155;}
    div[data-testid="stMetric"] {background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.14); padding: 18px; border-radius: 18px; box-shadow: 0 10px 30px rgba(0,0,0,.25);}
    h1, h2, h3 {letter-spacing: -0.03em;}
    .hero {padding: 22px 26px; border-radius: 24px; background: linear-gradient(135deg, rgba(108,99,255,.28), rgba(0,212,255,.12)); border: 1px solid rgba(255,255,255,.16); margin-bottom: 18px;}
    .chip {display:inline-block; padding: 8px 12px; margin: 5px 6px 0 0; border-radius: 999px; background: rgba(255,255,255,.09); border:1px solid rgba(255,255,255,.14);}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
<div class='hero'>
<h1>🛰️ Customer Churn Prediction & Retention Command Center</h1>
<p>A portfolio-grade executive dashboard with risk scoring, revenue leakage, customer micro-segments, and novel visual views built for quick business decisions.</p>
<span class='chip'>Risk DNA</span><span class='chip'>Revenue Leak Radar</span><span class='chip'>Churn Galaxy</span><span class='chip'>Retention Action Queue</span>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("🎛️ Filters")
    contract = st.multiselect("Contract type", sorted(df.contract_type.unique()), default=sorted(df.contract_type.unique()))
    internet = st.multiselect("Internet service", sorted(df.internet_service.unique()), default=sorted(df.internet_service.unique()))
    payment = st.multiselect("Payment method", sorted(df.payment_method.unique()), default=sorted(df.payment_method.unique()))
    gender = st.multiselect("Gender", sorted(df.gender.unique()), default=sorted(df.gender.unique()))
    senior = st.multiselect("Senior citizen", sorted(df.senior_citizen.unique()), default=sorted(df.senior_citizen.unique()))
    partner = st.multiselect("Partner", sorted(df.partner.unique()), default=sorted(df.partner.unique()))
    dependents = st.multiselect("Dependents", sorted(df.dependents.unique()), default=sorted(df.dependents.unique()))
    vas = st.multiselect("Value-added services", sorted(df.value_added_services.unique()), default=sorted(df.value_added_services.unique()))
    risk_filter = st.multiselect("Risk tier", ["Low", "Medium", "High"], default=["Low", "Medium", "High"])
    tenure_range = st.slider("Tenure months", int(df.tenure_months.min()), int(df.tenure_months.max()), (int(df.tenure_months.min()), int(df.tenure_months.max())))
    charge_range = st.slider("Monthly charge", float(df.monthly_charges.min()), float(df.monthly_charges.max()), (float(df.monthly_charges.min()), float(df.monthly_charges.max())))

f = df[
    df.contract_type.isin(contract)
    & df.internet_service.isin(internet)
    & df.payment_method.isin(payment)
    & df.gender.isin(gender)
    & df.senior_citizen.isin(senior)
    & df.partner.isin(partner)
    & df.dependents.isin(dependents)
    & df.value_added_services.isin(vas)
    & df.risk_tier.astype(str).isin(risk_filter)
    & df.tenure_months.between(*tenure_range)
    & df.monthly_charges.between(*charge_range)
].copy()

if f.empty:
    st.warning("No customers match the selected filters. Select more options in the sidebar.")
    st.stop()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Customers", f"{len(f):,}")
k2.metric("Churn rate", f"{f.churn_flag.mean()*100:.1f}%")
k3.metric("Avg risk score", f"{f.risk_score.mean():.0f}/100")
k4.metric("Monthly revenue", f"${f.monthly_charges.sum():,.0f}")
k5.metric("Annual revenue at risk", f"${f.estimated_revenue_at_risk.sum():,.0f}")

st.subheader("🚨 Novel View 1: Churn Galaxy Map")
sample = f.sample(min(len(f), 2500), random_state=9)
fig = px.scatter(
    sample,
    x="tenure_months",
    y="monthly_charges",
    size="risk_score",
    color="risk_tier",
    symbol="churn",
    hover_data=["customer_id", "contract_type", "internet_service", "payment_method", "support_tickets_90d", "late_payments_12m"],
    title="Each customer is a star: size = risk score, color = risk tier, symbol = churn status",
    labels={"tenure_months": "Tenure months", "monthly_charges": "Monthly charges"},
    color_discrete_sequence=THEME,
)
fig.update_layout(height=560, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.03)")
st.plotly_chart(fig, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.subheader("🧬 Novel View 2: Segment Risk DNA")
    radar = pd.DataFrame({
        "driver": ["Tickets", "Late payments", "Month-to-month", "Fiber optic", "Low tenure", "No value services"],
        "score": [
            f.support_tickets_90d.mean() / max(df.support_tickets_90d.max(), 1) * 100,
            f.late_payments_12m.mean() / max(df.late_payments_12m.max(), 1) * 100,
            f.contract_type.eq("Month-to-month").mean() * 100,
            f.internet_service.eq("Fiber optic").mean() * 100,
            (f.tenure_months < 12).mean() * 100,
            f.value_added_services.eq("No").mean() * 100,
        ],
    })
    fig = go.Figure(go.Scatterpolar(r=radar.score, theta=radar.driver, fill="toself", name="Risk DNA"))
    fig.update_layout(height=450, polar=dict(radialaxis=dict(visible=True, range=[0, 100])), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    st.subheader("💧 Revenue Leak Waterfall")
    leak = f.groupby("risk_tier", observed=True, as_index=False)["estimated_revenue_at_risk"].sum()
    leak = leak.set_index("risk_tier").reindex(["Low", "Medium", "High"]).fillna(0).reset_index()
    fig = go.Figure(go.Waterfall(
        x=leak.risk_tier.astype(str), y=leak.estimated_revenue_at_risk,
        measure=["relative", "relative", "total"], text=[f"${v:,.0f}" for v in leak.estimated_revenue_at_risk]
    ))
    fig.update_layout(title="Annual revenue leakage by risk tier", height=450, yaxis_title="Revenue at risk", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.subheader("🔥 Churn Heatmap")
    heat = f.pivot_table(index="payment_method", columns="internet_service", values="churn_flag", aggfunc="mean") * 100
    fig = px.imshow(heat, text_auto=".1f", aspect="auto", title="Payment Method × Internet Service Churn %", labels=dict(color="Churn %"), color_continuous_scale="Plasma")
    fig.update_layout(height=430, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
with c4:
    st.subheader("🌞 Customer Segment Sunburst")
    fig = px.sunburst(f, path=["risk_tier", "contract_type", "tenure_stage"], values="monthly_charges", color="churn_flag", color_continuous_scale="RdYlGn_r", title="Revenue-weighted customer segments")
    fig.update_layout(height=430, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

c5, c6 = st.columns(2)
with c5:
    st.subheader("📊 Churn by Contract")
    churn_contract = f.groupby("contract_type", as_index=False).agg(churn_rate=("churn_flag", "mean"), customers=("customer_id", "count"))
    churn_contract["churn_rate"] *= 100
    fig = px.bar(churn_contract, x="contract_type", y="churn_rate", text="churn_rate", color="customers", title="Contract churn rate and customer count", color_continuous_scale="Turbo")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(height=410, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
with c6:
    st.subheader("⚡ Retention Funnel")
    funnel = pd.DataFrame({
        "stage": ["All customers", "Medium + High risk", "High risk", "High risk + high value", "Immediate outreach"],
        "customers": [len(f), int((f.risk_tier != "Low").sum()), int((f.risk_tier == "High").sum()), int(((f.risk_tier == "High") & (f.customer_value_band.isin(["Premium", "Elite"]))).sum()), int(((f.risk_tier == "High") & (f.monthly_charges >= f.monthly_charges.quantile(.75))).sum())]
    })
    fig = px.funnel(funnel, y="stage", x="customers", title="Retention prioritization funnel", color="stage", color_discrete_sequence=THEME)
    fig.update_layout(height=410, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("🎯 Retention Priority Action Queue")
queue = f.sort_values(["risk_score", "monthly_charges"], ascending=[False, False])[
    ["customer_id", "risk_tier", "risk_score", "contract_type", "internet_service", "payment_method", "tenure_months", "monthly_charges", "support_tickets_90d", "late_payments_12m", "value_added_services", "churn"]
].head(40)
st.dataframe(queue, use_container_width=True, hide_index=True)
