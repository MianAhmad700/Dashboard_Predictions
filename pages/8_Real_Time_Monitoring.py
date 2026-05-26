from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

from charts import factory as cf
from components.ui import configure_page, glass_panel, page_header, render_sidebar, section_title
from utils.data_loader import load_fraud_data, load_hotel_data


try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None


configure_page("Real-Time Monitoring")
controls = render_sidebar()
fraud_df = load_fraud_data(controls["fraud_sample"])
hotel_df = load_hotel_data(controls["hotel_sample"])

page_header(
    "Real-Time Monitoring",
    "live operations wall",
    "A simulated real-time command wall with live fraud feed, booking feed, alerts, and streaming signal charts.",
    ["auto-refresh", "live feed", "blinking alerts", "streaming charts"],
)

if controls["refresh_mode"] and st_autorefresh:
    st_autorefresh(interval=5000, key="nexus_live_refresh")
elif controls["refresh_mode"]:
    st.info("Install streamlit-autorefresh from requirements.txt to enable timed auto-refresh.")

tick = int(datetime.now().timestamp() // 5)
rng = np.random.default_rng(tick)

fraud_live = fraud_df.sample(min(18, len(fraud_df)), random_state=tick % 9999).sort_values("risk_score", ascending=False)
hotel_live = hotel_df.sample(min(18, len(hotel_df)), random_state=(tick + 17) % 9999)
signal = np.clip(np.cumsum(rng.normal(0, 2, 48)) + 50 + rng.random(48) * 16, 0, 100).tolist()
booking_signal = np.clip(np.cumsum(rng.normal(0, 1.6, 48)) + 45 + rng.random(48) * 18, 0, 100).tolist()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Live Fraud Events", f"{int(fraud_live['fraud_flag'].sum()):,}", delta="last pulse")
m2.metric("Mean Live Risk", f"{fraud_live['risk_score'].mean():.1f}")
m3.metric("Live Bookings", f"{len(hotel_live):,}")
m4.metric("Live ADR", f"${hotel_live['adr'].mean():,.2f}")

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(cf.live_stream(signal, "Streaming Fraud Risk Pulse"), use_container_width=True)
with c2:
    st.plotly_chart(cf.live_stream(booking_signal, "Streaming Booking Demand Pulse"), use_container_width=True)

section_title("Live Alert Center")
alert_col, feed_col = st.columns([0.78, 1.22])
with alert_col:
    critical = fraud_live[fraud_live["risk_level"].isin(["High", "Critical"])].head(8)
    if critical.empty:
        glass_panel("No critical fraud alerts", "The current pulse has no high or critical transactions.")
    for _, row in critical.iterrows():
        glass_panel(
            f"{row['risk_level']} alert: {row['transaction_id']}",
            f"${row['transaction_amount']:,.2f} {row['merchant_category']} transaction from {row['location']} scored {row['risk_score']:.1f}.",
            accent=True,
        )
        st.write("")
with feed_col:
    st.markdown("#### Live Fraud Feed")
    st.dataframe(
        fraud_live[[
            "transaction_timestamp",
            "transaction_id",
            "transaction_amount",
            "payment_method",
            "device_type",
            "location",
            "merchant_category",
            "risk_level",
            "risk_score",
        ]].style.background_gradient(subset=["risk_score"], cmap="magma").format({"transaction_amount": "${:,.2f}", "risk_score": "{:.1f}"}),
        use_container_width=True,
        height=340,
    )
    st.markdown("#### Live Booking Feed")
    st.dataframe(
        hotel_live[[
            "arrival_date",
            "hotel",
            "country",
            "market_segment",
            "customer_type",
            "adr",
            "total_nights",
            "traveler_type",
            "reservation_status",
        ]].style.format({"adr": "${:,.2f}", "total_nights": "{:.0f}"}),
        use_container_width=True,
        height=320,
    )

section_title("Operations Intelligence")
c3, c4 = st.columns(2)
with c3:
    live_by_device = fraud_live.groupby("device_type", observed=False).agg(volume=("transaction_id", "count"), risk=("risk_score", "mean")).reset_index()
    st.plotly_chart(cf.bar(live_by_device, "device_type", "risk", "device_type", "Live Device Risk"), use_container_width=True)
with c4:
    live_booking = hotel_live.groupby("traveler_type", observed=False).agg(bookings=("hotel", "count"), adr=("adr", "mean")).reset_index()
    st.plotly_chart(cf.bubble(live_booking, "bookings", "adr", "bookings", "traveler_type", "Live Guest Mix"), use_container_width=True)
