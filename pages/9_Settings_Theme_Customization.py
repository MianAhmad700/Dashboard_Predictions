from __future__ import annotations

import streamlit as st

from components.ui import configure_page, dataframe_download, glass_panel, page_header, render_sidebar, section_title
from config.settings import FRAUD_DATA_CANDIDATES, HOTEL_DATA_CANDIDATES, THEMES
from utils.data_loader import load_fraud_data, load_hotel_data
from utils.insights import build_html_report, build_pdf_report, generate_combined_insights


configure_page("Settings / Theme Customization")
controls = render_sidebar()
fraud_df = load_fraud_data(controls["fraud_sample"])
hotel_df = load_hotel_data(controls["hotel_sample"])

page_header(
    "Settings / Theme Customization",
    "control surface",
    "Tune the visual theme, verify dataset health, export active datasets, and download executive reports.",
    ["theme switcher", "dataset health", "exports", "AI assistant"],
)

section_title("Theme Engine")
cols = st.columns(len(THEMES))
for idx, (name, theme) in enumerate(THEMES.items()):
    with cols[idx]:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="nexus-chip">{name}</div>
                <div style="display:flex;gap:.35rem;margin:.8rem 0;">
                    <div style="width:34px;height:34px;border-radius:12px;background:{theme['primary']};"></div>
                    <div style="width:34px;height:34px;border-radius:12px;background:{theme['secondary']};"></div>
                    <div style="width:34px;height:34px;border-radius:12px;background:{theme['accent']};"></div>
                </div>
                <div style="color:#cbd5e1;">Select this theme from the sidebar to re-skin the full dashboard.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

section_title("Dataset Health")
health_cols = st.columns(2)
with health_cols[0]:
    fraud_path = next((path for path in FRAUD_DATA_CANDIDATES if path.exists()), None)
    glass_panel(
        "Fraud Dataset",
        f"Rows: {len(fraud_df):,}<br>Columns: {len(fraud_df.columns):,}<br>Path: {fraud_path or 'not found'}",
    )
with health_cols[1]:
    hotel_path = next((path for path in HOTEL_DATA_CANDIDATES if path.exists()), None)
    glass_panel(
        "Hotel Dataset",
        f"Rows: {len(hotel_df):,}<br>Columns: {len(hotel_df.columns):,}<br>Path: {hotel_path or 'not found'}",
    )

section_title("Export Center")
e1, e2, e3, e4 = st.columns(4)
with e1:
    dataframe_download(fraud_df, "Download fraud CSV", "nexus_fraud_export.csv")
with e2:
    dataframe_download(hotel_df, "Download hotel CSV", "nexus_hotel_export.csv")
insights = generate_combined_insights(fraud_df, hotel_df)
with e3:
    st.download_button(
        "Download HTML report",
        build_html_report(fraud_df, hotel_df, insights),
        "nexus_executive_report.html",
        "text/html",
        use_container_width=True,
    )
with e4:
    pdf = build_pdf_report(fraud_df, hotel_df, insights)
    if pdf:
        st.download_button("Download PDF report", pdf, "nexus_executive_report.pdf", "application/pdf", use_container_width=True)
    else:
        st.info("Install reportlab for PDF export.")

section_title("AI Assistant Popup Simulation")
query = st.text_area("Ask the dashboard assistant", placeholder="Example: What should leadership do about high-risk merchants?")
if st.button("Generate Assistant Response", use_container_width=True):
    if query:
        glass_panel(
            "Assistant Response",
            "NEXUS recommends combining the AI Insights Center with Fraud Intelligence drilldowns. "
            "Prioritize merchant categories with high fraud probability, then validate lift through the Predictive Analytics feature importance panel.",
            accent=True,
        )
    else:
        st.warning("Enter a question to activate the assistant.")

section_title("Notification Center")
notifications = [
    "Theme engine is session-based and updates the dashboard instantly.",
    "Data loaders automatically use files in data/ first, then the provided download paths.",
    "ML models use cached training for smooth exploration after the first run.",
    "CSV, HTML, and PDF exports are available from this control surface.",
]
for note in notifications:
    glass_panel("System Notification", note)
    st.write("")
