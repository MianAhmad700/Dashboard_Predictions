from __future__ import annotations

import streamlit as st

from config.settings import DEFAULT_THEME, THEMES


def get_theme() -> dict:
    name = st.session_state.get("theme_name", DEFAULT_THEME)
    return THEMES.get(name, THEMES[DEFAULT_THEME])


def apply_global_styles() -> None:
    theme = get_theme()
    st.markdown(
        f"""
        <style>
        :root {{
            --nexus-bg: {theme["bg"]};
            --nexus-panel: {theme["panel"]};
            --nexus-primary: {theme["primary"]};
            --nexus-secondary: {theme["secondary"]};
            --nexus-accent: {theme["accent"]};
            --nexus-success: {theme["success"]};
            --nexus-warning: {theme["warning"]};
            --nexus-danger: {theme["danger"]};
            --nexus-text: {theme["text"]};
            --nexus-muted: #94a3b8;
        }}

        html, body, [data-testid="stAppViewContainer"] {{
            background:
                radial-gradient(circle at 8% 12%, color-mix(in srgb, var(--nexus-primary) 24%, transparent), transparent 26rem),
                radial-gradient(circle at 92% 10%, color-mix(in srgb, var(--nexus-secondary) 22%, transparent), transparent 28rem),
                radial-gradient(circle at 50% 100%, color-mix(in srgb, var(--nexus-accent) 16%, transparent), transparent 32rem),
                linear-gradient(135deg, #020617 0%, var(--nexus-bg) 48%, #050816 100%);
            color: var(--nexus-text);
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        [data-testid="stSidebar"] {{
            background:
                linear-gradient(180deg, rgba(2, 6, 23, 0.94), rgba(15, 23, 42, 0.88)),
                radial-gradient(circle at 30% 15%, color-mix(in srgb, var(--nexus-primary) 28%, transparent), transparent 12rem);
            border-right: 1px solid color-mix(in srgb, var(--nexus-secondary) 40%, transparent);
            box-shadow: 0 0 28px color-mix(in srgb, var(--nexus-primary) 22%, transparent);
        }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1480px;
        }}

        .nexus-orbit {{
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 0;
            opacity: 0.52;
            background-image:
                radial-gradient(circle, rgba(255,255,255,0.12) 1px, transparent 1px),
                radial-gradient(circle, color-mix(in srgb, var(--nexus-secondary) 34%, transparent) 1px, transparent 1px);
            background-size: 42px 42px, 78px 78px;
            animation: nexusDrift 26s linear infinite;
        }}

        @keyframes nexusDrift {{
            from {{ transform: translate3d(0, 0, 0); }}
            to {{ transform: translate3d(-80px, -120px, 0); }}
        }}

        @keyframes pulseGlow {{
            0%, 100% {{ box-shadow: 0 0 18px color-mix(in srgb, var(--nexus-primary) 18%, transparent); }}
            50% {{ box-shadow: 0 0 36px color-mix(in srgb, var(--nexus-secondary) 38%, transparent); }}
        }}

        @keyframes floatPanel {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-5px); }}
        }}

        @keyframes shimmer {{
            0% {{ background-position: -240% 0; }}
            100% {{ background-position: 240% 0; }}
        }}

        .nexus-hero {{
            position: relative;
            overflow: hidden;
            padding: 1.6rem 1.8rem;
            border-radius: 28px;
            border: 1px solid color-mix(in srgb, var(--nexus-secondary) 42%, transparent);
            background:
                linear-gradient(135deg, rgba(15, 23, 42, 0.72), rgba(30, 41, 59, 0.38)),
                radial-gradient(circle at 18% 12%, color-mix(in srgb, var(--nexus-primary) 22%, transparent), transparent 22rem);
            backdrop-filter: blur(18px);
            box-shadow: 0 18px 80px rgba(0,0,0,0.38), inset 0 1px 0 rgba(255,255,255,0.12);
            margin-bottom: 1.3rem;
            animation: floatPanel 8s ease-in-out infinite;
        }}

        .nexus-title {{
            font-size: clamp(2.2rem, 5vw, 4.8rem);
            line-height: 0.95;
            margin: 0;
            font-weight: 900;
            letter-spacing: -0.07em;
            background: linear-gradient(90deg, #fff, var(--nexus-secondary), var(--nexus-accent), var(--nexus-primary));
            background-size: 220% 100%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 7s linear infinite;
        }}

        .nexus-subtitle {{
            color: #cbd5e1;
            font-size: 1.05rem;
            margin-top: 0.7rem;
            max-width: 900px;
        }}

        .nexus-chip {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.35rem 0.75rem;
            margin: 0.2rem 0.25rem 0.2rem 0;
            border-radius: 999px;
            color: #e0f2fe;
            background: rgba(14, 165, 233, 0.12);
            border: 1px solid color-mix(in srgb, var(--nexus-secondary) 42%, transparent);
            box-shadow: 0 0 18px color-mix(in srgb, var(--nexus-secondary) 16%, transparent);
            font-size: 0.78rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        .glass-card {{
            padding: 1.1rem;
            border-radius: 24px;
            border: 1px solid rgba(148, 163, 184, 0.22);
            background:
                linear-gradient(145deg, rgba(15, 23, 42, 0.78), rgba(15, 23, 42, 0.38)),
                radial-gradient(circle at 20% 0%, color-mix(in srgb, var(--nexus-primary) 15%, transparent), transparent 14rem);
            backdrop-filter: blur(18px);
            box-shadow: 0 16px 55px rgba(0,0,0,0.32), inset 0 1px 0 rgba(255,255,255,0.08);
            transition: all 220ms ease;
            height: 100%;
        }}

        .glass-card:hover {{
            transform: translateY(-4px);
            border-color: color-mix(in srgb, var(--nexus-secondary) 56%, transparent);
            box-shadow: 0 24px 80px rgba(0,0,0,0.46), 0 0 26px color-mix(in srgb, var(--nexus-primary) 24%, transparent);
        }}

        .kpi-card {{
            min-height: 148px;
            position: relative;
            overflow: hidden;
        }}

        .kpi-label {{
            color: #94a3b8;
            font-size: 0.76rem;
            letter-spacing: 0.11em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }}

        .kpi-value {{
            font-size: 2.1rem;
            font-weight: 900;
            letter-spacing: -0.04em;
            color: #f8fafc;
        }}

        .kpi-delta {{
            margin-top: 0.55rem;
            font-size: 0.86rem;
            color: var(--nexus-secondary);
        }}

        .kpi-icon {{
            position: absolute;
            right: 1rem;
            top: 1rem;
            width: 42px;
            height: 42px;
            border-radius: 16px;
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, color-mix(in srgb, var(--nexus-primary) 44%, transparent), color-mix(in srgb, var(--nexus-secondary) 28%, transparent));
            color: #fff;
            font-weight: 900;
            box-shadow: 0 0 22px color-mix(in srgb, var(--nexus-secondary) 30%, transparent);
        }}

        .ai-terminal {{
            border-radius: 26px;
            padding: 1.2rem;
            border: 1px solid color-mix(in srgb, var(--nexus-secondary) 45%, transparent);
            background:
                linear-gradient(180deg, rgba(2, 6, 23, 0.88), rgba(15, 23, 42, 0.76)),
                repeating-linear-gradient(0deg, rgba(255,255,255,0.025) 0, rgba(255,255,255,0.025) 1px, transparent 1px, transparent 6px);
            box-shadow: 0 0 38px color-mix(in srgb, var(--nexus-primary) 20%, transparent), inset 0 0 28px rgba(14,165,233,0.08);
        }}

        .ai-line {{
            font-family: "Cascadia Mono", "SFMono-Regular", Consolas, monospace;
            color: #bae6fd;
            margin: 0.55rem 0;
            overflow: hidden;
        }}

        .alert-critical {{
            border-left: 4px solid var(--nexus-danger);
            animation: pulseGlow 2.6s ease-in-out infinite;
        }}

        .nexus-table [data-testid="stDataFrame"] {{
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, 0.22);
        }}

        div[data-testid="stMetric"] {{
            border-radius: 20px;
            padding: 1rem;
            background: rgba(15, 23, 42, 0.52);
            border: 1px solid rgba(148, 163, 184, 0.16);
        }}

        .stButton > button, .stDownloadButton > button {{
            border-radius: 999px;
            border: 1px solid color-mix(in srgb, var(--nexus-secondary) 48%, transparent);
            background: linear-gradient(135deg, color-mix(in srgb, var(--nexus-primary) 38%, #020617), color-mix(in srgb, var(--nexus-secondary) 34%, #020617));
            color: #f8fafc;
            box-shadow: 0 0 18px color-mix(in srgb, var(--nexus-primary) 18%, transparent);
            transition: all 180ms ease;
        }}

        .stButton > button:hover, .stDownloadButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 0 30px color-mix(in srgb, var(--nexus-secondary) 32%, transparent);
        }}

        hr {{
            border-color: rgba(148, 163, 184, 0.18);
        }}
        </style>
        <div class="nexus-orbit"></div>
        """,
        unsafe_allow_html=True,
    )
