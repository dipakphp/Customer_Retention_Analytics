import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Customer Retention Dashboard", layout="wide")

# Custom Styles
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0e1117 0%, #161a24 100%); color: #f0f2f6; }
    .header-banner { background: linear-gradient(90deg, #1f4068 0%, #162447 50%, #0f1b29 100%); padding: 2rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); text-align: center; margin-bottom: 2rem; }
    .header-banner h1 { font-size: 2.3rem; font-weight: 700; color: white; margin: 0; }
    .header-banner p { font-size: 1.1rem; color: #b0c4de; margin: 0.5rem 0 0 0; }
    .kpi-container { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 2rem; }
    .kpi-card { flex: 1 1 200px; background: rgba(30, 41, 59, 0.45); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 1.5rem; text-align: center; }
    .kpi-value { font-size: 2.1rem; font-weight: 700; color: #6366f1; }
    .kpi-title { font-size: 0.9rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

file_name = "European_Bank.csv"
if not os.path.exists(file_name):
    st.error("Dataset not found!")
    st.stop()
    
df = pd.read_csv(file_name)

# Sidebar Filters
st.sidebar.markdown("### Filter Controls")
geographies = df["Geography"].unique().tolist()
selected_geos = st.sidebar.multiselect("Geography", options=geographies, default=geographies)
balance_threshold = st.sidebar.number_input("Balance Threshold (€)", value=100000.0)
salary_threshold = st.sidebar.number_input("Salary Threshold (€)", value=120000.0)

filtered_df = df[df["Geography"].isin(selected_geos)]

# KPI calculations
active_churn = filtered_df[filtered_df["IsActiveMember"] == 1]["Exited"].mean()
inactive_churn = filtered_df[filtered_df["IsActiveMember"] == 0]["Exited"].mean()
ratio = active_churn / inactive_churn if inactive_churn > 0 else 0

st.markdown("""
    <div class='header-banner'>
        <h1>European Bank Retention Dashboard</h1>
        <p>Live Analytics for Customer Retention & Engagement Strategy</p>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class='kpi-container'>
        <div class='kpi-card'>
            <div class='kpi-title'>Engagement Retention Ratio</div>
            <div class='kpi-value'>{ratio:.3f}</div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-title'>Active Member Churn</div>
            <div class='kpi-value'>{active_churn*100:.2f}%</div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-title'>Inactive Member Churn</div>
            <div class='kpi-value'>{inactive_churn*100:.2f}%</div>
        </div>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📈 Churn & Product Utilization", "⚠️ At-Risk Premium Detector", "🧮 RSI Calculator"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        prod_stats = filtered_df.groupby("NumOfProducts")["Exited"].mean().reset_index()
        fig = px.bar(prod_stats, x="NumOfProducts", y="Exited", text=prod_stats["Exited"].apply(lambda x: f'{x*100:.1f}%'), title="Churn Rate by Product Count", color_discrete_sequence=['#ef4444'])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        act_stats = filtered_df.groupby("IsActiveMember")["Exited"].mean().reset_index()
        act_stats["Status"] = act_stats["IsActiveMember"].map({1: "Active", 0: "Inactive"})
        fig2 = px.bar(act_stats, x="Status", y="Exited", text=act_stats["Exited"].apply(lambda x: f'{x*100:.1f}%'), title="Churn Rate by Activity Status", color_discrete_sequence=['#10b981'])
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    at_risk = filtered_df[
        ((filtered_df["Balance"] >= balance_threshold) | (filtered_df["EstimatedSalary"] >= salary_threshold)) &
        (filtered_df["IsActiveMember"] == 0) &
        (filtered_df["CreditScore"] >= 600)
    ]
    st.metric("At-Risk Premium Customers Count", len(at_risk))
    st.dataframe(at_risk[["CustomerId", "Surname", "CreditScore", "Balance", "EstimatedSalary", "NumOfProducts"]])

with tab3:
    st.markdown("#### Relationship Strength Index")
    calc_active = st.checkbox("Is Active Member", value=True)
    calc_products = st.slider("Product Count", 1, 4, 2)
    calc_has_card = st.checkbox("Has Credit Card", value=True)
    calc_tenure = st.slider("Tenure (Years)", 0, 10, 5)

    score = (40 if calc_active else 0) + (30 if calc_products==2 else (20 if calc_products==3 else (10 if calc_products==1 else 5))) + (15 if calc_has_card else 0) + ((calc_tenure/10)*15)
    st.write(f"### Calculated RSI Score: {score:.1f} / 100")
