from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.ui import active_theme_palette
from styles.neon import get_theme


def _layout(fig: go.Figure, title: str | None = None, height: int = 420) -> go.Figure:
    theme = get_theme()
    fig.update_layout(
        title=title,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=theme["text"], family="Inter, Arial, sans-serif"),
        margin=dict(l=25, r=25, t=55 if title else 20, b=25),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        colorway=active_theme_palette(),
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,0.12)", zerolinecolor="rgba(148,163,184,0.18)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,0.12)", zerolinecolor="rgba(148,163,184,0.18)")
    return fig


def _empty_figure(title: str = "No data available", height: int = 420) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text="No data available for the current filters",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=16, color="#94a3b8"),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _layout(fig, title, height)


def donut(df: pd.DataFrame, names: str, values: str | None = None, title: str = "", hole: float = 0.62) -> go.Figure:
    if df.empty:
        return _empty_figure(title)
    fig = px.pie(df, names=names, values=values, hole=hole, color_discrete_sequence=active_theme_palette())
    fig.update_traces(textposition="inside", textinfo="percent+label", marker=dict(line=dict(color="rgba(255,255,255,0.16)", width=1)))
    fig.add_annotation(text="NEXUS", x=0.5, y=0.5, showarrow=False, font=dict(size=18, color="#e5e7eb"))
    return _layout(fig, title)


def line_area(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str = "", height: int = 430) -> go.Figure:
    if df.empty:
        return _empty_figure(title, height)
    fig = px.area(df, x=x, y=y, color=color, markers=True, color_discrete_sequence=active_theme_palette())
    fig.update_traces(line=dict(width=3), opacity=0.72)
    return _layout(fig, title, height)


def line(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str = "", height: int = 420) -> go.Figure:
    if df.empty:
        return _empty_figure(title, height)
    fig = px.line(df, x=x, y=y, color=color, markers=True, color_discrete_sequence=active_theme_palette())
    fig.update_traces(line=dict(width=3))
    return _layout(fig, title, height)


def bar(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str = "", orientation: str = "v", height: int = 420) -> go.Figure:
    if df.empty:
        return _empty_figure(title, height)
    fig = px.bar(df, x=x, y=y, color=color, orientation=orientation, color_discrete_sequence=active_theme_palette())
    fig.update_traces(marker_line_width=0, opacity=0.9)
    return _layout(fig, title, height)


def histogram(df: pd.DataFrame, x: str, color: str | None = None, title: str = "", nbins: int = 45, height: int = 420) -> go.Figure:
    if df.empty:
        return _empty_figure(title, height)
    fig = px.histogram(df, x=x, color=color, nbins=nbins, marginal="box", opacity=0.78, color_discrete_sequence=active_theme_palette())
    return _layout(fig, title, height)


def box(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str = "", height: int = 420) -> go.Figure:
    if df.empty:
        return _empty_figure(title, height)
    fig = px.box(df, x=x, y=y, color=color, points="outliers", color_discrete_sequence=active_theme_palette())
    return _layout(fig, title, height)


def heatmap(pivot: pd.DataFrame, title: str = "", height: int = 430) -> go.Figure:
    if pivot.empty:
        return _empty_figure(title, height)
    theme = get_theme()
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.astype(str),
            y=pivot.index.astype(str),
            colorscale=[[0, theme["bg"]], [0.45, theme["primary"]], [1, theme["accent"]]],
            hoverongaps=False,
            colorbar=dict(title="Intensity"),
        )
    )
    return _layout(fig, title, height)


def treemap(df: pd.DataFrame, path: list[str], values: str, color: str | None = None, title: str = "", height: int = 450) -> go.Figure:
    if df.empty:
        return _empty_figure(title, height)
    fig = px.treemap(df, path=path, values=values, color=color, color_continuous_scale="Turbo")
    fig.update_traces(root_color="rgba(15,23,42,0.6)")
    return _layout(fig, title, height)


def sunburst(df: pd.DataFrame, path: list[str], values: str | None = None, color: str | None = None, title: str = "", height: int = 450) -> go.Figure:
    if df.empty:
        return _empty_figure(title, height)
    fig = px.sunburst(df, path=path, values=values, color=color, color_continuous_scale="Plasma", color_discrete_sequence=active_theme_palette())
    return _layout(fig, title, height)


def radar(categories: list[str], values: list[float], title: str = "") -> go.Figure:
    theme = get_theme()
    cats = categories + categories[:1]
    vals = values + values[:1]
    fig = go.Figure(
        data=go.Scatterpolar(
            r=vals,
            theta=cats,
            fill="toself",
            line=dict(color=theme["secondary"], width=3),
            fillcolor="rgba(6,182,212,0.24)",
        )
    )
    fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, gridcolor="rgba(148,163,184,0.18)")))
    return _layout(fig, title, 430)


def bubble(df: pd.DataFrame, x: str, y: str, size: str, color: str, title: str = "", height: int = 430) -> go.Figure:
    if df.empty:
        return _empty_figure(title, height)
    fig = px.scatter(df, x=x, y=y, size=size, color=color, hover_name=color, size_max=54, color_discrete_sequence=active_theme_palette())
    fig.update_traces(marker=dict(line=dict(width=1, color="rgba(255,255,255,0.22)")))
    return _layout(fig, title, height)


def scatter(df: pd.DataFrame, x: str, y: str, color: str, size: str | None = None, title: str = "", height: int = 430) -> go.Figure:
    if df.empty:
        return _empty_figure(title, height)
    fig = px.scatter(df, x=x, y=y, color=color, size=size, opacity=0.78, color_discrete_sequence=active_theme_palette())
    fig.update_traces(marker=dict(line=dict(width=0.5, color="rgba(255,255,255,0.18)")))
    return _layout(fig, title, height)


def choropleth(df: pd.DataFrame, locations: str, color: str, hover_name: str, title: str = "", locationmode: str = "ISO-3", height: int = 470) -> go.Figure:
    if df.empty:
        return _empty_figure(title, height)
    fig = px.choropleth(
        df,
        locations=locations,
        color=color,
        hover_name=hover_name,
        locationmode=locationmode,
        color_continuous_scale="Turbo",
        projection="natural earth",
    )
    fig.update_geos(
        bgcolor="rgba(0,0,0,0)",
        showframe=False,
        showcoastlines=True,
        coastlinecolor="rgba(148,163,184,0.22)",
        landcolor="rgba(15,23,42,0.42)",
        oceancolor="rgba(2,6,23,0.7)",
        showocean=True,
    )
    return _layout(fig, title, height)


def violin(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str = "", height: int = 430) -> go.Figure:
    if df.empty:
        return _empty_figure(title, height)
    fig = px.violin(df, x=x, y=y, color=color, box=True, points=False, color_discrete_sequence=active_theme_palette())
    return _layout(fig, title, height)


def roc_curve_plot(curves: dict, title: str = "ROC Performance") -> go.Figure:
    fig = go.Figure()
    for name, curve in curves.items():
        fig.add_trace(go.Scatter(x=curve["fpr"], y=curve["tpr"], mode="lines", name=f"{name} AUC {curve['auc']:.3f}", line=dict(width=3)))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Baseline", line=dict(dash="dash", color="rgba(148,163,184,0.55)")))
    fig.update_xaxes(title="False Positive Rate")
    fig.update_yaxes(title="True Positive Rate")
    return _layout(fig, title, 430)


def gauge(value: float, title: str, suffix: str = "%") -> go.Figure:
    theme = get_theme()
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": suffix, "font": {"color": theme["text"]}},
            title={"text": title, "font": {"color": theme["text"]}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#94a3b8"},
                "bar": {"color": theme["secondary"]},
                "bgcolor": "rgba(15,23,42,0.32)",
                "borderwidth": 1,
                "bordercolor": "rgba(148,163,184,0.24)",
                "steps": [
                    {"range": [0, 35], "color": "rgba(34,197,94,0.22)"},
                    {"range": [35, 70], "color": "rgba(245,158,11,0.24)"},
                    {"range": [70, 100], "color": "rgba(239,68,68,0.26)"},
                ],
            },
        )
    )
    return _layout(fig, None, 280)


def forecast_chart(history: pd.DataFrame, forecast: pd.DataFrame, x: str, y: str, yhat: str, title: str = "") -> go.Figure:
    theme = get_theme()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=history[x], y=history[y], mode="lines+markers", name="Actual", line=dict(color=theme["secondary"], width=3)))
    fig.add_trace(go.Scatter(x=forecast[x], y=forecast[yhat], mode="lines+markers", name="Forecast", line=dict(color=theme["accent"], width=3, dash="dot")))
    if {"lower", "upper"}.issubset(forecast.columns):
        fig.add_trace(
            go.Scatter(
                x=pd.concat([forecast[x], forecast[x][::-1]]),
                y=pd.concat([forecast["upper"], forecast["lower"][::-1]]),
                fill="toself",
                fillcolor="rgba(236,72,153,0.14)",
                line=dict(color="rgba(255,255,255,0)"),
                hoverinfo="skip",
                name="Confidence",
            )
        )
    return _layout(fig, title, 460)


def live_stream(values: list[float], title: str = "Live Pulse") -> go.Figure:
    theme = get_theme()
    x = list(range(len(values)))
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=values,
            mode="lines",
            fill="tozeroy",
            line=dict(color=theme["secondary"], width=3),
            fillcolor="rgba(6,182,212,0.18)",
            name="Signal",
        )
    )
    return _layout(fig, title, 300)
