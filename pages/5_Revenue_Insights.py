from __future__ import annotations

import pandas as pd
import streamlit as st

from charts import factory as cf
from components.ui import configure_page, format_number, glass_panel, page_header, render_sidebar, section_title
from utils.data_loader import load_hotel_data
from utils.ml import monthly_revenue_forecast


configure_page("Revenue Insights")
controls = render_sidebar()
hotel_df = load_hotel_data(controls["hotel_sample"])

page_header(
    "Revenue Insights",
    "profitability cockpit",
    "Forecast revenue, detect ADR peaks, identify seasonality, and convert booking behavior into pricing strategy.",
    ["forecasting", "ADR intelligence", "seasonality", "profit radar"],
)

history, forecast = monthly_revenue_forecast(hotel_df)

total_revenue = hotel_df["total_revenue"].sum()
adr = hotel_df["adr"].mean()
peak_month = hotel_df.groupby("arrival_date_month", observed=False)["total_revenue"].sum().sort_values(ascending=False).index[0]
best_segment = hotel_df.groupby("market_segment", observed=False)["total_revenue"].sum().sort_values(ascending=False).index[0]

cols = st.columns(4)
cols[0].metric("Total Hotel Revenue", format_number(total_revenue, "$"))
cols[1].metric("Average Daily Rate", format_number(adr, "$"))
cols[2].metric("Peak Revenue Month", str(peak_month))
cols[3].metric("Best Segment", str(best_segment))

if not forecast.empty:
    st.plotly_chart(cf.forecast_chart(history, forecast, "month", "revenue", "forecast", "Revenue Forecasting Lines"), use_container_width=True)
else:
    glass_panel("Forecast unavailable", "At least three revenue-positive months are required to render the forecasting model.")

section_title("ADR and Peak Season Analysis")
c1, c2 = st.columns(2)
with c1:
    adr_month = hotel_df.groupby("arrival_date_month", observed=False).agg(adr=("adr", "mean"), revenue=("total_revenue", "sum"), bookings=("hotel", "count")).reset_index()
    st.plotly_chart(cf.bubble(adr_month, "bookings", "adr", "revenue", "arrival_date_month", "Monthly ADR and Revenue Power"), use_container_width=True)
with c2:
    revenue_heat = hotel_df.pivot_table(index="arrival_date_month", columns="hotel", values="total_revenue", aggfunc="sum", fill_value=0, observed=False)
    st.plotly_chart(cf.heatmap(revenue_heat, "Revenue Heatmap by Hotel and Month"), use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    weekly = hotel_df.groupby("arrival_date_week_number", observed=False).agg(revenue=("total_revenue", "sum"), adr=("adr", "mean")).reset_index()
    st.plotly_chart(cf.line(weekly, "arrival_date_week_number", "revenue", title="Weekly Profitability Trends"), use_container_width=True)
with c4:
    segment = hotel_df.groupby("market_segment", observed=False).agg(revenue=("total_revenue", "sum"), adr=("adr", "mean"), bookings=("hotel", "count")).reset_index()
    st.plotly_chart(cf.treemap(segment, ["market_segment"], "revenue", "adr", "Market Segment Revenue Treemap"), use_container_width=True)

section_title("Booking Behavior and Profitability")
c5, c6 = st.columns(2)
with c5:
    lead = hotel_df.groupby("lead_time_bucket", observed=False).agg(revenue=("total_revenue", "sum"), cancellation=("is_canceled", "mean"), bookings=("hotel", "count")).reset_index()
    lead["cancellation"] *= 100
    st.plotly_chart(cf.bubble(lead, "bookings", "revenue", "cancellation", "lead_time_bucket", "Lead Time Revenue Behavior"), use_container_width=True)
with c6:
    room = hotel_df.groupby("reserved_room_type", observed=False).agg(revenue=("total_revenue", "sum"), adr=("adr", "mean"), bookings=("hotel", "count")).reset_index()
    st.plotly_chart(cf.bar(room.sort_values("revenue", ascending=False), "reserved_room_type", "revenue", title="Room Type Revenue Ranking"), use_container_width=True)

recommendations = [
    f"Prioritize yield management in {peak_month}; this is the highest revenue window in the active dataset.",
    f"Protect {best_segment} inventory with premium availability and cancellation-risk rules.",
    "Use long lead-time cancellation lift to trigger pre-arrival confirmation and deposit nudges.",
    "Bundle family rooms and extended stays during ADR peaks to raise total booking value.",
]
st.markdown("### AI Revenue Strategy")
for rec in recommendations:
    glass_panel("Revenue Recommendation", rec)
    st.write("")
