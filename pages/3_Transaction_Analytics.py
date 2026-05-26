from __future__ import annotations

import pandas as pd
import streamlit as st

from charts import factory as cf
from components.ui import configure_page, dataframe_download, page_header, render_sidebar, section_title
from utils.data_loader import filter_fraud, load_fraud_data


configure_page("Transaction Analytics")
controls = render_sidebar()
fraud_df = load_fraud_data(controls["fraud_sample"])

page_header(
    "Transaction Analytics",
    "transaction observability",
    "Explore every transaction, isolate suspicious patterns, and monitor high-risk payment activity with analyst-grade controls.",
    ["transaction explorer", "risk search", "live feed", "payment intelligence"],
)

with st.expander("Explorer Filters", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    search = c1.text_input("Search transaction or customer")
    payment = c2.multiselect("Payment method", sorted(fraud_df["payment_method"].unique()))
    device = c3.multiselect("Device type", sorted(fraud_df["device_type"].unique()))
    suspicious_only = c4.toggle("Suspicious detector", value=False)

filtered = filter_fraud(fraud_df, controls["risk_focus"])
if search:
    mask = filtered["transaction_id"].astype(str).str.contains(search, case=False, na=False) | filtered["customer_id"].astype(str).str.contains(search, case=False, na=False)
    filtered = filtered[mask]
if payment:
    filtered = filtered[filtered["payment_method"].isin(payment)]
if device:
    filtered = filtered[filtered["device_type"].isin(device)]
if suspicious_only:
    filtered = filtered[
        filtered[[
            "previous_fraud_flag",
            "unusual_amount_flag",
            "unusual_location_flag",
            "multiple_transactions_short_time",
            "high_risk_device_flag",
            "velocity_flag",
        ]].sum(axis=1).ge(2)
        | filtered["risk_level"].isin(["High", "Critical"])
    ]

metrics = st.columns(5)
metrics[0].metric("Visible Transactions", f"{len(filtered):,}")
metrics[1].metric("Fraud Cases", f"{int(filtered['fraud_flag'].sum()):,}")
metrics[2].metric("Avg Amount", f"${filtered['transaction_amount'].mean():,.2f}")
metrics[3].metric("International", f"{int(filtered['is_international'].sum()):,}")
metrics[4].metric("Critical Risk", f"{filtered['risk_level'].eq('Critical').sum():,}")

section_title("Real-Time Style Transaction Feed", "Latest transactions are ranked by timestamp and colored by risk state.")
feed_cols = st.columns([1.2, 0.8])
with feed_cols[0]:
    display_cols = [
        "transaction_timestamp",
        "transaction_id",
        "customer_id",
        "transaction_amount",
        "payment_method",
        "device_type",
        "location",
        "merchant_category",
        "fraud_flag",
        "risk_level",
        "risk_score",
    ]
    styled = (
        filtered.sort_values("transaction_timestamp", ascending=False)[display_cols]
        .head(800)
        .style.background_gradient(subset=["risk_score"], cmap="magma")
        .format({"transaction_amount": "${:,.2f}", "risk_score": "{:.1f}"})
    )
    st.markdown('<div class="nexus-table">', unsafe_allow_html=True)
    st.dataframe(styled, use_container_width=True, height=560)
    st.markdown("</div>", unsafe_allow_html=True)
    dataframe_download(filtered[display_cols], "Export filtered transactions", "nexus_transactions.csv")

with feed_cols[1]:
    high_risk = filtered.sort_values(["risk_score", "transaction_amount"], ascending=False).head(8)
    for _, row in high_risk.iterrows():
        st.markdown(
            f"""
            <div class="glass-card alert-critical">
                <div class="nexus-chip">{row['risk_level']} risk</div>
                <div style="font-weight:900;">{row['transaction_id']} | ${row['transaction_amount']:,.2f}</div>
                <div style="color:#94a3b8;">{row['merchant_category']} via {row['payment_method']} on {row['device_type']}</div>
                <div style="color:#bae6fd;margin-top:.35rem;">Score {row['risk_score']:.1f} | Fraud flag {int(row['fraud_flag'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")

section_title("Payment and International Intelligence")
c1, c2 = st.columns(2)
with c1:
    payment_df = filtered.groupby("payment_method", observed=False).agg(volume=("transaction_id", "count"), fraud_rate=("fraud_flag", "mean"), amount=("transaction_amount", "sum")).reset_index()
    payment_df["fraud_rate"] *= 100
    st.plotly_chart(cf.bubble(payment_df, "amount", "fraud_rate", "volume", "payment_method", "Payment Method Risk Matrix"), use_container_width=True)
with c2:
    intl = filtered.groupby("is_international", observed=False).agg(transactions=("transaction_id", "count"), fraud_rate=("fraud_flag", "mean")).reset_index()
    intl["is_international"] = intl["is_international"].map({0: "Domestic", 1: "International"})
    intl["fraud_rate"] *= 100
    st.plotly_chart(cf.bar(intl, "is_international", "fraud_rate", "is_international", "Domestic vs International Fraud"), use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    merchant = filtered.groupby("merchant_category", observed=False).agg(transactions=("transaction_id", "count"), avg_amount=("transaction_amount", "mean")).reset_index()
    st.plotly_chart(cf.bar(merchant.sort_values("transactions", ascending=False), "merchant_category", "transactions", title="Merchant Volume"), use_container_width=True)
with c4:
    pivot = filtered.pivot_table(index="payment_method", columns="device_type", values="fraud_flag", aggfunc="mean", fill_value=0, observed=False) * 100
    st.plotly_chart(cf.heatmap(pivot, "Payment x Device Fraud Heatmap"), use_container_width=True)
