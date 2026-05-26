from __future__ import annotations

from io import BytesIO

import numpy as np
import pandas as pd


def _safe_pct(value: float) -> str:
    if pd.isna(value):
        return "0.0%"
    return f"{value:.1f}%"


def generate_fraud_insights(df: pd.DataFrame) -> list[dict]:
    insights: list[dict] = []
    if df.empty:
        return [{"title": "No fraud records loaded", "body": "Upload or connect the fraud dataset to activate the intelligence engine.", "severity": "Medium"}]

    fraud_rate = df["fraud_flag"].mean() * 100
    high_amount = df[df["transaction_amount"] > df["transaction_amount"].quantile(0.90)]
    high_amount_rate = high_amount["fraud_flag"].mean() * 100 if len(high_amount) else 0

    merchant_risk = (
        df.groupby("merchant_category", observed=False)["fraud_flag"]
        .agg(["mean", "count"])
        .query("count >= 20")
        .sort_values("mean", ascending=False)
    )
    top_merchant = merchant_risk.index[0] if not merchant_risk.empty else "Unknown"
    top_merchant_rate = merchant_risk.iloc[0]["mean"] * 100 if not merchant_risk.empty else 0

    device_risk = (
        df.groupby("device_type", observed=False)["fraud_flag"]
        .mean()
        .sort_values(ascending=False)
    )
    top_device = device_risk.index[0] if not device_risk.empty else "Unknown"
    top_device_rate = device_risk.iloc[0] * 100 if not device_risk.empty else 0

    velocity_lift = (
        df[df["velocity_flag"].eq(1)]["fraud_flag"].mean()
        / max(df[df["velocity_flag"].eq(0)]["fraud_flag"].mean(), 0.001)
    )

    insights.extend(
        [
            {
                "title": "Fraud pressure is active",
                "body": f"Current sampled fraud rate is {_safe_pct(fraud_rate)} with {int(df['fraud_flag'].sum()):,} confirmed cases.",
                "severity": "Critical" if fraud_rate >= 10 else "High" if fraud_rate >= 5 else "Medium",
            },
            {
                "title": f"{top_merchant} merchants lead fraud probability",
                "body": f"This category is running at {_safe_pct(top_merchant_rate)}, making it the highest-risk commercial cluster.",
                "severity": "High",
            },
            {
                "title": "High value transactions deserve stepped-up controls",
                "body": f"Transactions above the 90th percentile show {_safe_pct(high_amount_rate)} fraud incidence versus {_safe_pct(fraud_rate)} globally.",
                "severity": "High" if high_amount_rate > fraud_rate * 1.4 else "Medium",
            },
            {
                "title": f"{top_device} devices are the dominant risk surface",
                "body": f"Device-level fraud probability peaks at {_safe_pct(top_device_rate)}. Route this segment to enhanced verification.",
                "severity": "Medium",
            },
            {
                "title": "Velocity flags are a strong behavioral signal",
                "body": f"Velocity-triggered users show approximately {velocity_lift:.1f}x higher fraud probability than normal-flow users.",
                "severity": "Critical" if velocity_lift >= 2.5 else "High",
            },
        ]
    )
    return insights


def generate_hotel_insights(df: pd.DataFrame) -> list[dict]:
    insights: list[dict] = []
    if df.empty:
        return [{"title": "No hotel records loaded", "body": "Upload or connect the hotel dataset to activate hospitality intelligence.", "severity": "Medium"}]

    cancel_rate = df["is_canceled"].mean() * 100
    lead_cancel = (
        df.groupby("lead_time_bucket", observed=False)["is_canceled"]
        .mean()
        .sort_values(ascending=False)
    )
    top_lead_bucket = lead_cancel.index[0] if not lead_cancel.empty else "Unknown"
    top_lead_rate = lead_cancel.iloc[0] * 100 if not lead_cancel.empty else 0

    family_stay = df[df["traveler_type"].eq("Family")]["total_nights"].mean()
    solo_stay = df[df["traveler_type"].eq("Solo")]["total_nights"].mean()
    segment_revenue = (
        df.groupby("market_segment", observed=False)["total_revenue"]
        .sum()
        .sort_values(ascending=False)
    )
    top_segment = segment_revenue.index[0] if not segment_revenue.empty else "Unknown"

    adr_by_month = (
        df.groupby("arrival_date_month", observed=False)["adr"]
        .mean()
        .sort_values(ascending=False)
    )
    top_month = adr_by_month.index[0] if not adr_by_month.empty else "Unknown"

    insights.extend(
        [
            {
                "title": "Cancellation exposure is measurable and controllable",
                "body": f"Current cancellation rate is {_safe_pct(cancel_rate)}. Use tighter deposit strategy on high-risk channels.",
                "severity": "High" if cancel_rate >= 35 else "Medium",
            },
            {
                "title": f"Lead time bucket {top_lead_bucket} carries cancellation risk",
                "body": f"This bucket cancels at {_safe_pct(top_lead_rate)}, indicating forecasting and pre-arrival engagement opportunity.",
                "severity": "High",
            },
            {
                "title": "Family guests stay longer",
                "body": f"Family average stay is {family_stay:.1f} nights versus {solo_stay:.1f} nights for solo guests.",
                "severity": "Medium",
            },
            {
                "title": f"{top_segment} is the revenue engine",
                "body": f"Market segment revenue contribution peaks here. Protect this channel with premium availability and ADR controls.",
                "severity": "Opportunity",
            },
            {
                "title": f"{top_month} commands the highest ADR",
                "body": "Use this seasonal window for premium packaging, minimum stay controls, and room-type upsell campaigns.",
                "severity": "Opportunity",
            },
        ]
    )
    return insights


def generate_combined_insights(fraud_df: pd.DataFrame, hotel_df: pd.DataFrame) -> list[dict]:
    fraud = generate_fraud_insights(fraud_df)
    hotel = generate_hotel_insights(hotel_df)
    combined = fraud[:3] + hotel[:3]
    combined.append(
        {
            "title": "Unified enterprise signal",
            "body": "Fraud prevention and hospitality demand both respond to early behavioral signals: velocity, lead time, channel, country, and customer history.",
            "severity": "AI Strategy",
        }
    )
    return combined


def build_html_report(fraud_df: pd.DataFrame, hotel_df: pd.DataFrame, insights: list[dict]) -> bytes:
    fraud_rate = fraud_df["fraud_flag"].mean() * 100 if len(fraud_df) else 0
    cancel_rate = hotel_df["is_canceled"].mean() * 100 if len(hotel_df) else 0
    insight_html = "".join(
        f"<li><strong>{item['title']}</strong>: {item['body']} <em>({item['severity']})</em></li>"
        for item in insights
    )
    html = f"""
    <html>
    <head><title>NEXUS AI Executive Report</title></head>
    <body style="font-family:Arial;background:#020617;color:#e5e7eb;padding:32px;">
      <h1>NEXUS AI Executive Report</h1>
      <p>Generated from the active fraud and hotel analytics datasets.</p>
      <h2>Command Metrics</h2>
      <ul>
        <li>Total transactions: {len(fraud_df):,}</li>
        <li>Fraud rate: {fraud_rate:.2f}%</li>
        <li>Hotel bookings: {len(hotel_df):,}</li>
        <li>Cancellation rate: {cancel_rate:.2f}%</li>
      </ul>
      <h2>AI Insight Feed</h2>
      <ul>{insight_html}</ul>
    </body>
    </html>
    """
    return html.encode("utf-8")


def build_pdf_report(fraud_df: pd.DataFrame, hotel_df: pd.DataFrame, insights: list[dict]) -> bytes | None:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception:
        return None

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "NEXUS AI Executive Report")
    y -= 34
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Transactions: {len(fraud_df):,} | Hotel bookings: {len(hotel_df):,}")
    y -= 28
    for item in insights[:8]:
        if y < 80:
            c.showPage()
            y = height - 50
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, item["title"][:86])
        y -= 14
        c.setFont("Helvetica", 9)
        text = item["body"][:108]
        c.drawString(60, y, text)
        y -= 24
    c.save()
    buffer.seek(0)
    return buffer.read()


def opportunity_score(df: pd.DataFrame, value_col: str, risk_col: str) -> float:
    if df.empty or value_col not in df or risk_col not in df:
        return 0.0
    value = pd.to_numeric(df[value_col], errors="coerce").fillna(0)
    risk = pd.to_numeric(df[risk_col], errors="coerce").fillna(0)
    return float(np.clip((value.rank(pct=True) * (1 - risk.rank(pct=True))).mean() * 100, 0, 100))
