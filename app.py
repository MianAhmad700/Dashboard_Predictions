from __future__ import annotations

import streamlit as st

from components.ui import configure_page, glass_panel, page_header, render_sidebar
from config.settings import APP_NAME, APP_SUBTITLE, APP_VERSION, PAGES
from utils.data_loader import load_fraud_data, load_hotel_data
from utils.insights import generate_combined_insights


configure_page("Mission Control")
controls = render_sidebar()

page_header(
    "NEXUS AI Analytics",
    "mission control",
    APP_SUBTITLE,
    ["fraud intelligence", "hotel revenue", "predictive ML", "real-time monitoring"],
)

fraud_df = load_fraud_data(controls["fraud_sample"])
hotel_df = load_hotel_data(controls["hotel_sample"])
insights = generate_combined_insights(fraud_df, hotel_df)

left, right = st.columns([1.15, 0.85])
with left:
    st.markdown(
        """
        <div class="ai-terminal">
            <div class="ai-line">nexus:// boot sequence complete</div>
            <div class="ai-line">nexus:// fraud telemetry linked</div>
            <div class="ai-line">nexus:// hospitality revenue graph online</div>
            <div class="ai-line">nexus:// predictive models available in analytics bay</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    glass_panel(
        "Launch Path",
        "Use the sidebar navigation to enter the executive overview or any specialized intelligence bay. "
        "The app is pure Python: Streamlit, Plotly, Pandas, NumPy, and Scikit-learn power the full experience.",
    )

with right:
    for item in insights[:4]:
        glass_panel(item["title"], item["body"], accent=item["severity"] in {"Critical", "High"})
        st.write("")

st.markdown("### Analytics Pages")
cols = st.columns(3)
for idx, (label, path) in enumerate(PAGES):
    with cols[idx % 3]:
        with st.container(border=False):
            st.markdown(
                f"""
                <div class="glass-card">
                    <div class="nexus-chip">module {idx + 1:02d}</div>
                    <div style="font-size:1.15rem;font-weight:900;margin:.35rem 0;">{label}</div>
                    <div style="color:#94a3b8;font-size:.9rem;">Open the dedicated intelligence view.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link(path, label=f"Open {label}")

st.caption(f"{APP_NAME} v{APP_VERSION} | Python-only enterprise analytics dashboard")
