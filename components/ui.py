from __future__ import annotations

from datetime import datetime
from typing import Iterable

import pandas as pd
import streamlit as st

from config.settings import APP_NAME, APP_SUBTITLE, DEFAULT_THEME, PAGES, THEMES
from styles.neon import apply_global_styles, get_theme


def configure_page(title: str) -> None:
    st.set_page_config(
        page_title=f"{title} | {APP_NAME}",
        page_icon=":material/analytics:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    if "theme_name" not in st.session_state:
        st.session_state.theme_name = DEFAULT_THEME
    apply_global_styles()


def render_sidebar() -> dict:
    theme_name = st.session_state.get("theme_name", DEFAULT_THEME)
    with st.sidebar:
        st.markdown(
            f"""
            <div class="glass-card" style="text-align:center;margin-bottom:1rem;">
                <div style="font-size:2rem;font-weight:900;letter-spacing:-0.08em;">NEXUS</div>
                <div style="color:#94a3b8;font-size:.78rem;letter-spacing:.17em;text-transform:uppercase;">AI Command Center</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption("Navigation Matrix")
        for label, path in PAGES:
            st.page_link(path, label=label)

        st.divider()
        selected_theme = st.selectbox(
            "Theme Engine",
            list(THEMES.keys()),
            index=list(THEMES.keys()).index(theme_name),
            key="theme_name",
        )

        st.caption("Global Controls")
        fraud_sample = st.slider("Fraud sample size", 5_000, 100_000, 50_000, step=5_000)
        hotel_sample = st.slider("Hotel sample size", 5_000, 120_000, 60_000, step=5_000)
        risk_focus = st.multiselect("Risk focus", ["Low", "Medium", "High", "Critical"], default=["Medium", "High", "Critical"])
        refresh_mode = st.toggle("Real-time pulse mode", value=False)

        st.divider()
        st.markdown(
            """
            <div class="ai-terminal">
                <div class="ai-line">AI ASSISTANT: online</div>
                <div class="ai-line">Mode: executive intelligence</div>
                <div class="ai-line">Signal quality: premium</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown(
            f"""
            <div class="glass-card">
                <div style="font-weight:800;">Ava Morgan</div>
                <div style="color:#94a3b8;font-size:.85rem;">Chief Analytics Officer</div>
                <div class="nexus-chip">secure session</div>
                <div style="color:#94a3b8;font-size:.76rem;margin-top:.4rem;">{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return {
        "theme": selected_theme,
        "fraud_sample": fraud_sample,
        "hotel_sample": hotel_sample,
        "risk_focus": risk_focus,
        "refresh_mode": refresh_mode,
    }


def page_header(title: str, eyebrow: str, description: str, chips: Iterable[str] | None = None) -> None:
    chip_html = "".join(f'<span class="nexus-chip">{chip}</span>' for chip in (chips or []))
    st.markdown(
        f"""
        <section class="nexus-hero">
            <div class="nexus-chip">{eyebrow}</div>
            <h1 class="nexus-title">{title}</h1>
            <p class="nexus-subtitle">{description}</p>
            <div>{chip_html}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str | int | float, delta: str, icon: str = "AI") -> None:
    st.markdown(
        f"""
        <div class="glass-card kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-delta">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def glass_panel(title: str, body: str, accent: bool = False) -> None:
    cls = "glass-card alert-critical" if accent else "glass-card"
    st.markdown(
        f"""
        <div class="{cls}">
            <div style="font-weight:900;font-size:1.04rem;margin-bottom:.45rem;">{title}</div>
            <div style="color:#cbd5e1;line-height:1.55;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def ai_terminal(lines: Iterable[str]) -> None:
    html = "".join(f'<div class="ai-line">nexus:// {line}</div>' for line in lines)
    st.markdown(f'<div class="ai-terminal">{html}</div>', unsafe_allow_html=True)


def section_title(title: str, subtitle: str | None = None) -> None:
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)


def dataframe_download(df: pd.DataFrame, label: str, file_name: str) -> None:
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=file_name,
        mime="text/csv",
        use_container_width=True,
    )


def format_number(value: float | int, prefix: str = "", suffix: str = "") -> str:
    if pd.isna(value):
        return f"{prefix}0{suffix}"
    value = float(value)
    if abs(value) >= 1_000_000_000:
        return f"{prefix}{value / 1_000_000_000:.2f}B{suffix}"
    if abs(value) >= 1_000_000:
        return f"{prefix}{value / 1_000_000:.2f}M{suffix}"
    if abs(value) >= 1_000:
        return f"{prefix}{value / 1_000:.1f}K{suffix}"
    if value.is_integer():
        return f"{prefix}{int(value):,}{suffix}"
    return f"{prefix}{value:,.2f}{suffix}"


def metric_grid(metrics: list[dict], columns: int = 5) -> None:
    cols = st.columns(columns)
    for idx, metric in enumerate(metrics):
        with cols[idx % columns]:
            kpi_card(
                metric["label"],
                metric["value"],
                metric.get("delta", ""),
                metric.get("icon", "AI"),
            )


def active_theme_palette() -> list[str]:
    theme = get_theme()
    return [theme["primary"], theme["secondary"], theme["accent"], theme["success"], theme["warning"], theme["danger"]]
