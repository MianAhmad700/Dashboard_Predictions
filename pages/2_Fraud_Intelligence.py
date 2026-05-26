from __future__ import annotations

import pandas as pd
import streamlit as st

from charts import factory as cf
from components.ui import configure_page, glass_panel, page_header, render_sidebar, section_title
from utils.data_loader import filter_fraud, load_fraud_data
from utils.insights import generate_fraud_insights


configure_page("Fraud Intelligence")
controls = render_sidebar()
fraud_df = load_fraud_data(controls["fraud_sample"])

page_header(
    "Fraud Intelligence",
    "cyber risk operations",
    "Detect fraud clusters, behavioral anomalies, risky merchants, risky devices, and global threat hotspots.",
    ["risk distribution", "velocity signals", "geo heat", "behavioral clusters"],
)

with st.expander("Advanced Fraud Filters", expanded=True):
    c1, c2, c3 = st.columns(3)
    merchants = c1.multiselect("Merchant category", sorted(fraud_df["merchant_category"].unique()))
    countries = c2.multiselect("Country", sorted(fraud_df["location"].unique()))
    amount_min, amount_max = float(fraud_df["transaction_amount"].min()), float(fraud_df["transaction_amount"].max())
    amount_range = c3.slider("Amount range", amount_min, amount_max, (amount_min, amount_max))

filtered = filter_fraud(fraud_df, controls["risk_focus"], merchants, countries, amount_range)
insights = generate_fraud_insights(filtered)

top = st.columns(4)
top[0].metric("Transactions", f"{len(filtered):,}")
top[1].metric("Fraud Cases", f"{int(filtered['fraud_flag'].sum()):,}")
top[2].metric("Fraud Rate", f"{filtered['fraud_flag'].mean() * 100:.2f}%")
top[3].metric("Mean Risk Score", f"{filtered['risk_score'].mean():.1f}")

for item in insights[:2]:
    glass_panel(item["title"], item["body"], accent=item["severity"] in {"Critical", "High"})
    st.write("")

col1, col2 = st.columns(2)
with col1:
    risk_counts = filtered["risk_level"].value_counts().rename_axis("Risk").reset_index(name="Transactions")
    st.plotly_chart(cf.donut(risk_counts, "Risk", "Transactions", "Fraud Risk Distribution"), use_container_width=True)
with col2:
    granularity = st.radio("Trend granularity", ["Daily", "Weekly", "Monthly"], horizontal=True)
    if granularity == "Daily":
        trend = filtered.groupby("date", observed=False).agg(transactions=("transaction_id", "count"), fraud=("fraud_flag", "sum")).reset_index()
        x_col = "date"
    elif granularity == "Weekly":
        trend = filtered.set_index("transaction_timestamp").resample("W").agg(transactions=("transaction_id", "count"), fraud=("fraud_flag", "sum")).reset_index()
        x_col = "transaction_timestamp"
    else:
        trend = filtered.groupby("month", observed=False).agg(transactions=("transaction_id", "count"), fraud=("fraud_flag", "sum")).reset_index()
        x_col = "month"
    trend["fraud_rate"] = trend["fraud"] / trend["transactions"].clip(lower=1) * 100
    st.plotly_chart(cf.line_area(trend, x_col, "fraud_rate", title="Fraud Trend Analysis"), use_container_width=True)

section_title("Fraud Heatmaps")
h1, h2, h3 = st.columns(3)
with h1:
    hour_pivot = filtered.pivot_table(index="hour", columns="fraud_risk", values="fraud_flag", aggfunc="mean", fill_value=0, observed=False) * 100
    st.plotly_chart(cf.heatmap(hour_pivot, "Hour vs Fraud Activity"), use_container_width=True)
with h2:
    device_pivot = filtered.pivot_table(index="device_type", columns="fraud_risk", values="fraud_flag", aggfunc="mean", fill_value=0, observed=False) * 100
    st.plotly_chart(cf.heatmap(device_pivot, "Device vs Fraud"), use_container_width=True)
with h3:
    country_pivot = filtered.pivot_table(index="location", columns="fraud_risk", values="fraud_flag", aggfunc="mean", fill_value=0, observed=False) * 100
    st.plotly_chart(cf.heatmap(country_pivot.head(14), "Country vs Fraud"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    merchant = (
        filtered.groupby("merchant_category", observed=False)
        .agg(transactions=("transaction_id", "count"), fraud_rate=("fraud_flag", "mean"), amount=("transaction_amount", "sum"))
        .reset_index()
    )
    merchant["fraud_rate"] *= 100
    st.plotly_chart(cf.treemap(merchant, ["merchant_category"], "transactions", "fraud_rate", "Merchant Risk Treemap"), use_container_width=True)
with col4:
    st.plotly_chart(cf.histogram(filtered, "transaction_amount", "risk_level", "Transaction Amount Distribution"), use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    st.plotly_chart(cf.box(filtered, "risk_level", "transaction_amount", "risk_level", "Amount Outlier Detection"), use_container_width=True)
with col6:
    device = (
        filtered.groupby("device_type", observed=False)
        .agg(fraud_rate=("fraud_flag", "mean"), risk_score=("risk_score", "mean"), volume=("transaction_id", "count"))
        .reset_index()
    )
    device["fraud_rate"] *= 100
    st.plotly_chart(cf.bubble(device, "risk_score", "fraud_rate", "volume", "device_type", "Device Risk Bubble Matrix"), use_container_width=True)

col7, col8 = st.columns(2)
with col7:
    radar_metrics = [
        filtered["previous_fraud_flag"].mean() * 100,
        filtered["unusual_amount_flag"].mean() * 100,
        filtered["unusual_location_flag"].mean() * 100,
        filtered["velocity_flag"].mean() * 100,
        filtered["high_risk_device_flag"].mean() * 100,
    ]
    st.plotly_chart(cf.radar(["Previous", "Amount", "Location", "Velocity", "Device"], radar_metrics, "Device and Behavior Radar"), use_container_width=True)
with col8:
    scatter_df = filtered.sample(min(len(filtered), 9000), random_state=3)
    st.plotly_chart(cf.scatter(scatter_df, "transaction_amount", "transaction_frequency_24h", "risk_level", "risk_score", "Behavioral Fraud Clusters"), use_container_width=True)

geo = (
    filtered.groupby(["iso3", "location"], observed=False)
    .agg(fraud_cases=("fraud_flag", "sum"), transactions=("transaction_id", "count"), avg_amount=("transaction_amount", "mean"))
    .reset_index()
)
geo["fraud_rate"] = geo["fraud_cases"] / geo["transactions"].clip(lower=1) * 100
st.plotly_chart(cf.choropleth(geo, "iso3", "fraud_rate", "location", "Interactive World Fraud Hotspots"), use_container_width=True)
