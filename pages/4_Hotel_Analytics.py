from __future__ import annotations

import pandas as pd
import streamlit as st

from charts import factory as cf
from components.ui import configure_page, page_header, render_sidebar, section_title
from utils.data_loader import filter_hotel, load_hotel_data
from utils.insights import generate_hotel_insights


configure_page("Hotel Analytics")
controls = render_sidebar()
hotel_df = load_hotel_data(controls["hotel_sample"])

page_header(
    "Hotel Analytics",
    "hospitality intelligence",
    "Premium hotel demand, guest, room, lead-time, cancellation, and country analytics in a cyber command-center interface.",
    ["booking trends", "guest segments", "room intelligence", "cancellation risk"],
)

with st.expander("Hotel Filters", expanded=True):
    c1, c2, c3 = st.columns(3)
    hotels = c1.multiselect("Hotel", sorted(hotel_df["hotel"].unique()))
    segments = c2.multiselect("Market segment", sorted(hotel_df["market_segment"].unique()))
    travelers = c3.multiselect("Traveler type", sorted(hotel_df["traveler_type"].unique()))

filtered = filter_hotel(hotel_df, hotels, segments, travelers)
insights = generate_hotel_insights(filtered)

metrics = st.columns(5)
metrics[0].metric("Bookings", f"{len(filtered):,}")
metrics[1].metric("Cancellation Rate", f"{filtered['is_canceled'].mean() * 100:.1f}%")
metrics[2].metric("ADR", f"${filtered['adr'].mean():,.2f}")
metrics[3].metric("Revenue", f"${filtered['total_revenue'].sum():,.0f}")
metrics[4].metric("Avg Stay", f"{filtered['total_nights'].mean():.1f} nights")

for item in insights[:2]:
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="nexus-chip">{item['severity']}</div>
            <div style="font-size:1.05rem;font-weight:900;">{item['title']}</div>
            <div style="color:#cbd5e1;">{item['body']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

section_title("Booking and Cancellation Intelligence")
c1, c2 = st.columns(2)
with c1:
    booking_trend = (
        filtered.dropna(subset=["arrival_date"])
        .groupby(pd.Grouper(key="arrival_date", freq="MS"))
        .agg(bookings=("hotel", "count"), revenue=("total_revenue", "sum"))
        .reset_index()
    )
    st.plotly_chart(cf.line_area(booking_trend, "arrival_date", "bookings", title="Booking Trends"), use_container_width=True)
with c2:
    status = filtered["is_canceled"].map({0: "Stayed", 1: "Canceled"}).value_counts().rename_axis("Status").reset_index(name="Bookings")
    st.plotly_chart(cf.donut(status, "Status", "Bookings", "Cancellation Analysis"), use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    cancel_stack = (
        filtered.groupby(["hotel", "reservation_status"], observed=False)
        .size()
        .reset_index(name="bookings")
    )
    st.plotly_chart(cf.bar(cancel_stack, "hotel", "bookings", "reservation_status", "Reservation Status by Hotel"), use_container_width=True)
with c4:
    st.plotly_chart(cf.histogram(filtered, "lead_time", "is_canceled", "Lead Time Distribution", nbins=60), use_container_width=True)

section_title("Guest, Country, and Segment Analytics")
c5, c6 = st.columns(2)
with c5:
    country = filtered.groupby("country", observed=False).agg(bookings=("hotel", "count"), revenue=("total_revenue", "sum")).reset_index()
    st.plotly_chart(cf.choropleth(country, "country", "bookings", "country", "Guest Country Map"), use_container_width=True)
with c6:
    segment = filtered.groupby(["hotel", "market_segment", "traveler_type"], observed=False).agg(bookings=("hotel", "count")).reset_index()
    st.plotly_chart(cf.sunburst(segment, ["hotel", "market_segment", "traveler_type"], "bookings", title="Customer Segmentation Sunburst"), use_container_width=True)

c7, c8 = st.columns(2)
with c7:
    stay_sample = filtered.sample(min(len(filtered), 12000), random_state=9)
    st.plotly_chart(cf.violin(stay_sample, "traveler_type", "total_nights", "hotel", "Stay Duration Analysis"), use_container_width=True)
with c8:
    room = (
        filtered.pivot_table(index="reserved_room_type", columns="assigned_room_type", values="adr", aggfunc="mean", fill_value=0, observed=False)
    )
    st.plotly_chart(cf.heatmap(room, "Reserved vs Assigned Room ADR Heatmap"), use_container_width=True)

c9, c10 = st.columns(2)
with c9:
    room_comp = filtered.groupby("reserved_room_type", observed=False).agg(bookings=("hotel", "count"), adr=("adr", "mean"), revenue=("total_revenue", "sum")).reset_index()
    st.plotly_chart(cf.bubble(room_comp, "bookings", "adr", "revenue", "reserved_room_type", "Room Type Performance"), use_container_width=True)
with c10:
    family = filtered.groupby("traveler_type", observed=False).agg(bookings=("hotel", "count"), avg_stay=("total_nights", "mean"), adr=("adr", "mean")).reset_index()
    st.plotly_chart(cf.bubble(family, "avg_stay", "adr", "bookings", "traveler_type", "Family vs Solo Traveler Behavior"), use_container_width=True)
