from __future__ import annotations

import pandas as pd


def fraud_kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    fraud_cases = int(df["fraud_flag"].sum()) if "fraud_flag" in df else 0
    high_risk = int(df["risk_level"].isin(["High", "Critical"]).sum()) if "risk_level" in df else 0
    international = int(df["is_international"].sum()) if "is_international" in df else 0
    revenue = float(df["transaction_amount"].sum()) if "transaction_amount" in df else 0
    avg_amount = float(df["transaction_amount"].mean()) if total else 0
    fraud_rate = (fraud_cases / total * 100) if total else 0
    return {
        "total_transactions": total,
        "fraud_cases": fraud_cases,
        "fraud_rate": fraud_rate,
        "transaction_revenue": revenue,
        "high_risk_transactions": high_risk,
        "international_transactions": international,
        "average_transaction_amount": avg_amount,
    }


def hotel_kpis(df: pd.DataFrame) -> dict:
    bookings = len(df)
    cancellations = int(df["is_canceled"].sum()) if "is_canceled" in df else 0
    cancellation_rate = (cancellations / bookings * 100) if bookings else 0
    adr = float(df["adr"].mean()) if bookings else 0
    revenue = float(df["total_revenue"].sum()) if "total_revenue" in df else 0
    avg_stay = float(df["total_nights"].mean()) if bookings else 0
    family_rate = float(df["is_family"].mean() * 100) if "is_family" in df and bookings else 0
    return {
        "hotel_bookings": bookings,
        "cancellations": cancellations,
        "cancellation_rate": cancellation_rate,
        "average_daily_rate": adr,
        "hotel_revenue": revenue,
        "average_stay_duration": avg_stay,
        "family_rate": family_rate,
    }


def executive_kpis(fraud_df: pd.DataFrame, hotel_df: pd.DataFrame) -> dict:
    fraud = fraud_kpis(fraud_df)
    hotel = hotel_kpis(hotel_df)
    return {
        **fraud,
        **hotel,
        "total_revenue": fraud["transaction_revenue"] + hotel["hotel_revenue"],
    }
