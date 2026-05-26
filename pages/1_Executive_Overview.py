from __future__ import annotations

import pandas as pd
import streamlit as st

from charts import factory as cf
from components.ui import configure_page, format_number, glass_panel, metric_grid, page_header, render_sidebar, section_title
from utils.data_loader import load_fraud_data, load_hotel_data
from utils.insights import generate_combined_insights
from utils.kpis import executive_kpis


configure_page("Executive Overview")
controls = render_sidebar()
fraud_df = load_fraud_data(controls["fraud_sample"])
hotel_df = load_hotel_data(controls["hotel_sample"])
kpis = executive_kpis(fraud_df, hotel_df)
insights = generate_combined_insights(fraud_df, hotel_df)

page_header(
    "Executive Overview",
    "enterprise command deck",
    "A single-pane command center for fraud risk, transaction flow, hospitality demand, revenue, and AI-generated decisions.",
    ["live KPIs", "smart alerts", "global telemetry", "board-ready"],
)

metrics = [
    {"label": "Total Transactions", "value": format_number(kpis["total_transactions"]), "delta": "sampled transaction universe", "icon": "TX"},
    {"label": "Fraud Cases", "value": format_number(kpis["fraud_cases"]), "delta": f"{kpis['fraud_rate']:.2f}% global fraud rate", "icon": "FR"},
    {"label": "Fraud Rate", "value": f"{kpis['fraud_rate']:.2f}%", "delta": "risk pressure index", "icon": "%"},
    {"label": "Total Revenue", "value": format_number(kpis["total_revenue"], "$"), "delta": "transactions + hotel revenue", "icon": "$"},
    {"label": "Hotel Bookings", "value": format_number(kpis["hotel_bookings"]), "delta": f"{kpis['cancellation_rate']:.1f}% cancellation rate", "icon": "HB"},
    {"label": "Cancellation Rate", "value": f"{kpis['cancellation_rate']:.1f}%", "delta": "hospitality leakage signal", "icon": "CX"},
    {"label": "Average Daily Rate", "value": format_number(kpis["average_daily_rate"], "$"), "delta": "ADR performance", "icon": "ADR"},
    {"label": "High Risk Transactions", "value": format_number(kpis["high_risk_transactions"]), "delta": "high + critical risk levels", "icon": "HI"},
    {"label": "International Transactions", "value": format_number(kpis["international_transactions"]), "delta": "cross-border exposure", "icon": "GL"},
    {"label": "Average Stay Duration", "value": f"{kpis['average_stay_duration']:.1f}", "delta": "nights per booking", "icon": "ST"},
]
metric_grid(metrics, columns=5)

st.write("")
left, right = st.columns([1.15, 0.85])
with left:
    section_title("AI Executive Summary", "Generated from the active fraud and hotel samples.")
    st.markdown(
        """
        <div class="ai-terminal">
            <div class="ai-line">nexus:// analyzing blended enterprise telemetry...</div>
            <div class="ai-line">nexus:// fraud velocity, revenue seasonality, and booking leakage detected</div>
            <div class="ai-line">nexus:// recommendation package compiled for leadership review</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with right:
    section_title("Smart Alerts")
    for item in insights[:3]:
        glass_panel(item["title"], item["body"], accent=item["severity"] in {"Critical", "High"})
        st.write("")

st.write("")
chart_a, chart_b = st.columns(2)
with chart_a:
    risk_counts = fraud_df["risk_level"].value_counts().rename_axis("Risk").reset_index(name="Transactions")
    st.plotly_chart(cf.donut(risk_counts, "Risk", "Transactions", "Fraud Risk Distribution"), use_container_width=True)
with chart_b:
    hotel_status = hotel_df["reservation_status"].value_counts().rename_axis("Status").reset_index(name="Bookings")
    st.plotly_chart(cf.donut(hotel_status, "Status", "Bookings", "Hotel Reservation Status"), use_container_width=True)

chart_c, chart_d = st.columns(2)
with chart_c:
    fraud_trend = (
        fraud_df.groupby("date", observed=False)
        .agg(transactions=("transaction_id", "count"), fraud=("fraud_flag", "sum"))
        .reset_index()
    )
    fraud_trend["fraud_rate"] = fraud_trend["fraud"] / fraud_trend["transactions"].clip(lower=1) * 100
    st.plotly_chart(cf.line_area(fraud_trend, "date", "fraud_rate", title="Daily Fraud Pressure"), use_container_width=True)
with chart_d:
    revenue_trend = (
        hotel_df.dropna(subset=["arrival_date"])
        .groupby(pd.Grouper(key="arrival_date", freq="MS"))["total_revenue"]
        .sum()
        .reset_index()
    )
    st.plotly_chart(cf.line_area(revenue_trend, "arrival_date", "total_revenue", title="Hotel Revenue Trajectory"), use_container_width=True)

map_left, map_right = st.columns(2)
with map_left:
    fraud_geo = (
        fraud_df.groupby(["iso3", "location"], observed=False)
        .agg(fraud_cases=("fraud_flag", "sum"), transactions=("transaction_id", "count"))
        .reset_index()
    )
    fraud_geo["fraud_rate"] = fraud_geo["fraud_cases"] / fraud_geo["transactions"].clip(lower=1) * 100
    st.plotly_chart(cf.choropleth(fraud_geo, "iso3", "fraud_rate", "location", "Global Fraud Hotspots"), use_container_width=True)
with map_right:
    country_revenue = (
        hotel_df.groupby("country", observed=False)
        .agg(bookings=("hotel", "count"), revenue=("total_revenue", "sum"))
        .reset_index()
    )
    st.plotly_chart(cf.choropleth(country_revenue, "country", "revenue", "country", "Hotel Guest Revenue Map"), use_container_width=True)
