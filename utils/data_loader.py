from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from config.settings import COUNTRY_NAME_TO_ISO3, FRAUD_DATA_CANDIDATES, HOTEL_DATA_CANDIDATES


def _first_existing(paths: list[Path]) -> Path:
    for path in paths:
        if path.exists():
            return path
    candidates = "\n".join(str(path) for path in paths)
    raise FileNotFoundError(f"Dataset not found. Checked:\n{candidates}")


def _optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include=["int64", "int32"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="integer")
    for col in df.select_dtypes(include=["float64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="float")
    for col in df.select_dtypes(include=["object"]).columns:
        if df[col].nunique(dropna=True) / max(len(df), 1) < 0.45:
            df[col] = df[col].astype("category")
    return df


@st.cache_data(show_spinner="Loading fraud intelligence dataset...")
def load_fraud_data(sample_size: int | None = None) -> pd.DataFrame:
    path = _first_existing(FRAUD_DATA_CANDIDATES)
    df = pd.read_csv(path)
    df.columns = [col.strip() for col in df.columns]

    df["transaction_timestamp"] = pd.to_datetime(df["transaction_timestamp"], errors="coerce")
    df["transaction_amount"] = pd.to_numeric(df["transaction_amount"], errors="coerce").fillna(0)
    df["avg_transaction_amount_7d"] = pd.to_numeric(df["avg_transaction_amount_7d"], errors="coerce").fillna(0)

    numeric_defaults = {
        "transaction_frequency_24h": 0,
        "failed_transaction_count_24h": 0,
        "account_age_days": 0,
        "is_international": 0,
        "previous_fraud_flag": 0,
        "unusual_amount_flag": 0,
        "unusual_location_flag": 0,
        "multiple_transactions_short_time": 0,
        "high_risk_device_flag": 0,
        "velocity_flag": 0,
        "fraud_flag": 0,
    }
    for col, default in numeric_defaults.items():
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default).astype(int)

    for col in ["payment_method", "device_type", "location", "merchant_category", "fraud_risk"]:
        if col in df:
            df[col] = df[col].fillna("Unknown").astype(str)

    df["date"] = df["transaction_timestamp"].dt.date
    df["hour"] = df["transaction_timestamp"].dt.hour.fillna(0).astype(int)
    df["weekday"] = df["transaction_timestamp"].dt.day_name().fillna("Unknown")
    df["month"] = df["transaction_timestamp"].dt.to_period("M").astype(str)
    df["iso3"] = df["location"].map(COUNTRY_NAME_TO_ISO3).fillna(df["location"])
    df["amount_ratio"] = df["transaction_amount"] / df["avg_transaction_amount_7d"].replace(0, np.nan)
    df["amount_ratio"] = df["amount_ratio"].replace([np.inf, -np.inf], np.nan).fillna(1)
    df["risk_score"] = (
        df["fraud_flag"] * 45
        + df["previous_fraud_flag"] * 18
        + df["unusual_amount_flag"] * 10
        + df["unusual_location_flag"] * 10
        + df["velocity_flag"] * 8
        + df["high_risk_device_flag"] * 7
        + np.clip(df["amount_ratio"], 0, 5) * 2
    ).clip(0, 100)
    df["risk_level"] = pd.cut(
        df["risk_score"],
        bins=[-1, 24, 49, 74, 100],
        labels=["Low", "Medium", "High", "Critical"],
    ).astype(str)

    if sample_size and sample_size < len(df):
        df = df.sample(sample_size, random_state=42).sort_values("transaction_timestamp")
    return _optimize_dataframe(df.reset_index(drop=True))


@st.cache_data(show_spinner="Loading hotel intelligence dataset...")
def load_hotel_data(sample_size: int | None = None) -> pd.DataFrame:
    path = _first_existing(HOTEL_DATA_CANDIDATES)
    df = pd.read_csv(path)
    df.columns = [col.strip() for col in df.columns]

    numeric_cols = [
        "is_canceled",
        "lead_time",
        "arrival_date_year",
        "arrival_date_week_number",
        "arrival_date_day_of_month",
        "stays_in_weekend_nights",
        "stays_in_week_nights",
        "adults",
        "children",
        "babies",
        "is_repeated_guest",
        "previous_cancellations",
        "previous_bookings_not_canceled",
        "booking_changes",
        "days_in_waiting_list",
        "adr",
        "required_car_parking_spaces",
        "total_of_special_requests",
        "total_nights",
        "is_family",
    ]
    for col in numeric_cols:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].fillna("Unknown").astype(str)

    month_lookup = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }
    df["arrival_month_num"] = df["arrival_date_month"].map(month_lookup).fillna(1).astype(int)
    df["arrival_date"] = pd.to_datetime(
        {
            "year": df["arrival_date_year"].astype(int),
            "month": df["arrival_month_num"],
            "day": df["arrival_date_day_of_month"].astype(int).clip(1, 28),
        },
        errors="coerce",
    )
    df["reservation_status_date"] = pd.to_datetime(df["reservation_status_date"], errors="coerce")
    df["booking_month"] = df["arrival_date"].dt.to_period("M").astype(str)
    df["guests"] = df["adults"] + df["children"] + df["babies"]
    computed_nights = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
    df["total_nights"] = np.where(computed_nights.gt(0), computed_nights, df["total_nights"])
    df["total_revenue"] = (df["adr"].clip(lower=0) * df["total_nights"].clip(lower=0)).fillna(0)
    df["traveler_type"] = np.select(
        [
            df["is_family"].astype(int).eq(1),
            df["guests"].le(1),
            df["guests"].ge(3),
        ],
        ["Family", "Solo", "Group"],
        default="Couple",
    )
    df["lead_time_bucket"] = pd.cut(
        df["lead_time"],
        bins=[-1, 7, 30, 90, 180, 365, 10000],
        labels=["0-7d", "8-30d", "31-90d", "91-180d", "181-365d", "365d+"],
    ).astype(str)
    df["cancellation_risk_score"] = (
        df["is_canceled"] * 45
        + np.clip(df["lead_time"] / 365, 0, 1) * 24
        + df["previous_cancellations"] * 8
        + (df["deposit_type"].ne("No Deposit")).astype(int) * 12
        + df["booking_changes"].clip(0, 5) * 2
    ).clip(0, 100)

    if sample_size and sample_size < len(df):
        df = df.sample(sample_size, random_state=7).sort_values("arrival_date")
    return _optimize_dataframe(df.reset_index(drop=True))


def filter_fraud(
    df: pd.DataFrame,
    risk_levels: list[str] | None = None,
    merchant_categories: list[str] | None = None,
    locations: list[str] | None = None,
    amount_range: tuple[float, float] | None = None,
) -> pd.DataFrame:
    filtered = df.copy()
    if risk_levels:
        filtered = filtered[filtered["risk_level"].isin(risk_levels) | filtered["fraud_risk"].isin(risk_levels)]
    if merchant_categories:
        filtered = filtered[filtered["merchant_category"].isin(merchant_categories)]
    if locations:
        filtered = filtered[filtered["location"].isin(locations)]
    if amount_range:
        filtered = filtered[filtered["transaction_amount"].between(amount_range[0], amount_range[1])]
    return filtered


def filter_hotel(
    df: pd.DataFrame,
    hotels: list[str] | None = None,
    segments: list[str] | None = None,
    traveler_types: list[str] | None = None,
) -> pd.DataFrame:
    filtered = df.copy()
    if hotels:
        filtered = filtered[filtered["hotel"].isin(hotels)]
    if segments:
        filtered = filtered[filtered["market_segment"].isin(segments)]
    if traveler_types:
        filtered = filtered[filtered["traveler_type"].isin(traveler_types)]
    return filtered
