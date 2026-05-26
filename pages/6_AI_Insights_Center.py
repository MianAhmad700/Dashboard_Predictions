from __future__ import annotations

import streamlit as st

from charts import factory as cf
from components.ui import ai_terminal, configure_page, glass_panel, page_header, render_sidebar, section_title
from utils.data_loader import load_fraud_data, load_hotel_data
from utils.insights import build_html_report, build_pdf_report, generate_combined_insights, generate_fraud_insights, generate_hotel_insights


configure_page("AI Insights Center")
controls = render_sidebar()
fraud_df = load_fraud_data(controls["fraud_sample"])
hotel_df = load_hotel_data(controls["hotel_sample"])

page_header(
    "AI Insights Center",
    "holographic decision engine",
    "A futuristic Python-built insights engine that converts fraud, transaction, hotel, and revenue telemetry into executive action.",
    ["AI observations", "smart recommendations", "risk alerts", "opportunity detection"],
)

combined = generate_combined_insights(fraud_df, hotel_df)
fraud_insights = generate_fraud_insights(fraud_df)
hotel_insights = generate_hotel_insights(hotel_df)

ai_terminal(
    [
        "booting autonomous insight model...",
        f"loaded {len(fraud_df):,} fraud transactions and {len(hotel_df):,} hotel bookings",
        "running anomaly, segmentation, cancellation, and revenue detectors",
        "compiling executive recommendations",
    ]
)

st.write("")
section_title("Priority AI Observations")
for item in combined:
    severity = item["severity"]
    accent = severity in {"Critical", "High"}
    glass_panel(f"{severity}: {item['title']}", item["body"], accent=accent)
    st.write("")

section_title("Insight Command Matrix")
c1, c2 = st.columns(2)
with c1:
    st.markdown("#### Fraud Intelligence Cards")
    for item in fraud_insights:
        glass_panel(item["title"], item["body"], accent=item["severity"] in {"Critical", "High"})
        st.write("")
with c2:
    st.markdown("#### Hospitality Intelligence Cards")
    for item in hotel_insights:
        glass_panel(item["title"], item["body"], accent=item["severity"] in {"Critical", "High"})
        st.write("")

section_title("AI Signal Gauges")
g1, g2, g3 = st.columns(3)
fraud_pressure = fraud_df["fraud_flag"].mean() * 100
cancel_pressure = hotel_df["is_canceled"].mean() * 100
revenue_quality = min(100, max(0, hotel_df["adr"].mean() / max(hotel_df["adr"].quantile(0.95), 1) * 100))
with g1:
    st.plotly_chart(cf.gauge(fraud_pressure, "Fraud Pressure"), use_container_width=True)
with g2:
    st.plotly_chart(cf.gauge(cancel_pressure, "Cancellation Pressure"), use_container_width=True)
with g3:
    st.plotly_chart(cf.gauge(revenue_quality, "Revenue Quality"), use_container_width=True)

section_title("Recommendation Console")
strategy = [
    "Route high amount-ratio transactions to adaptive step-up authentication.",
    "Create merchant-category fraud thresholds that adapt by device type and transaction velocity.",
    "Trigger hotel re-confirmation journeys for long lead-time, deposit-sensitive reservations.",
    "Use peak-month ADR intelligence to protect premium inventory and reduce low-margin allotments.",
    "Fuse country-level fraud and guest demand signals for regional executive briefings.",
]
for idx, item in enumerate(strategy, start=1):
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="nexus-chip">recommendation {idx:02d}</div>
            <div style="font-size:1.05rem;font-weight:900;">{item}</div>
            <div style="color:#94a3b8;margin-top:.35rem;">Owner: AI Strategy Office | Priority: High | Execution window: 7 days</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

report = build_html_report(fraud_df, hotel_df, combined + fraud_insights + hotel_insights)
pdf = build_pdf_report(fraud_df, hotel_df, combined + fraud_insights + hotel_insights)
dl1, dl2 = st.columns(2)
dl1.download_button("Download AI HTML report", report, "nexus_ai_report.html", "text/html", use_container_width=True)
if pdf:
    dl2.download_button("Download AI PDF report", pdf, "nexus_ai_report.pdf", "application/pdf", use_container_width=True)
else:
    dl2.info("PDF export needs reportlab installed from requirements.txt.")
