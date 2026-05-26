from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


try:
    from xgboost import XGBClassifier
except Exception:
    XGBClassifier = None


def _encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def _classifier_models(random_state: int = 42) -> dict:
    models = {
        "Logistic Regression": LogisticRegression(max_iter=800, class_weight="balanced", n_jobs=None),
        "Random Forest": RandomForestClassifier(
            n_estimators=160,
            max_depth=12,
            min_samples_leaf=8,
            class_weight="balanced_subsample",
            random_state=random_state,
            n_jobs=-1,
        ),
    }
    if XGBClassifier is not None:
        models["XGBoost"] = XGBClassifier(
            n_estimators=160,
            max_depth=4,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=random_state,
            n_jobs=2,
        )
    else:
        models["XGBoost-style Gradient Model"] = RandomForestClassifier(
            n_estimators=220,
            max_depth=8,
            random_state=random_state,
            class_weight="balanced_subsample",
            n_jobs=-1,
        )
    return models


def _build_pipeline(model, numeric_features: list[str], categorical_features: list[str]) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric_features),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", _encoder())]), categorical_features),
        ]
    )
    return Pipeline([("preprocessor", preprocessor), ("model", model)])


def _feature_names(pipeline: Pipeline, numeric_features: list[str], categorical_features: list[str]) -> list[str]:
    names = list(numeric_features)
    try:
        encoder = pipeline.named_steps["preprocessor"].named_transformers_["cat"].named_steps["onehot"]
        names += encoder.get_feature_names_out(categorical_features).tolist()
    except Exception:
        names += categorical_features
    return names


def _importance_frame(pipeline: Pipeline, numeric_features: list[str], categorical_features: list[str]) -> pd.DataFrame:
    model = pipeline.named_steps["model"]
    feature_names = _feature_names(pipeline, numeric_features, categorical_features)
    if hasattr(model, "feature_importances_"):
        values = model.feature_importances_
    elif hasattr(model, "coef_"):
        values = np.abs(model.coef_[0])
    else:
        values = np.zeros(len(feature_names))
    values = np.asarray(values)[: len(feature_names)]
    return (
        pd.DataFrame({"feature": feature_names[: len(values)], "importance": values})
        .sort_values("importance", ascending=False)
        .head(18)
    )


def _evaluate_pipeline(name: str, pipeline: Pipeline, x_train, x_test, y_train, y_test, numeric_features, categorical_features) -> dict:
    pipeline.fit(x_train, y_train)
    proba = pipeline.predict_proba(x_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    fpr, tpr, _ = roc_curve(y_test, proba)
    return {
        "name": name,
        "pipeline": pipeline,
        "accuracy": accuracy_score(y_test, pred),
        "roc_auc": roc_auc_score(y_test, proba),
        "average_precision": average_precision_score(y_test, proba),
        "fpr": fpr,
        "tpr": tpr,
        "importance": _importance_frame(pipeline, numeric_features, categorical_features),
    }


@st.cache_resource(show_spinner="Training fraud prediction models...")
def train_fraud_models(df: pd.DataFrame, max_rows: int = 25000) -> dict:
    features_num = [
        "transaction_amount",
        "transaction_frequency_24h",
        "avg_transaction_amount_7d",
        "failed_transaction_count_24h",
        "account_age_days",
        "previous_fraud_flag",
        "unusual_amount_flag",
        "unusual_location_flag",
        "multiple_transactions_short_time",
        "high_risk_device_flag",
        "velocity_flag",
        "is_international",
    ]
    features_cat = ["payment_method", "device_type", "location", "merchant_category"]
    data = df[features_num + features_cat + ["fraud_flag"]].dropna().copy()
    if len(data) > max_rows:
        data = data.sample(max_rows, random_state=42)
    x = data[features_num + features_cat]
    y = data["fraud_flag"].astype(int)
    stratify = y if y.nunique() > 1 else None
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.24, random_state=42, stratify=stratify)

    results = {}
    for name, model in _classifier_models(42).items():
        pipeline = _build_pipeline(model, features_num, features_cat)
        results[name] = _evaluate_pipeline(name, pipeline, x_train, x_test, y_train, y_test, features_num, features_cat)
    best_name = max(results, key=lambda key: results[key]["roc_auc"])
    return {"results": results, "best_name": best_name, "features_num": features_num, "features_cat": features_cat}


@st.cache_resource(show_spinner="Training cancellation prediction models...")
def train_cancellation_models(df: pd.DataFrame, max_rows: int = 30000) -> dict:
    features_num = [
        "lead_time",
        "arrival_date_week_number",
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
    features_cat = ["hotel", "meal", "country", "market_segment", "distribution_channel", "deposit_type", "customer_type", "reserved_room_type"]
    data = df[features_num + features_cat + ["is_canceled"]].dropna().copy()
    if len(data) > max_rows:
        data = data.sample(max_rows, random_state=7)
    x = data[features_num + features_cat]
    y = data["is_canceled"].astype(int)
    stratify = y if y.nunique() > 1 else None
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.24, random_state=7, stratify=stratify)

    results = {}
    for name, model in _classifier_models(7).items():
        pipeline = _build_pipeline(model, features_num, features_cat)
        results[name] = _evaluate_pipeline(name, pipeline, x_train, x_test, y_train, y_test, features_num, features_cat)
    best_name = max(results, key=lambda key: results[key]["roc_auc"])
    return {"results": results, "best_name": best_name, "features_num": features_num, "features_cat": features_cat}


def predict_probability(model_pack: dict, model_name: str, row: pd.DataFrame) -> float:
    pipeline = model_pack["results"][model_name]["pipeline"]
    return float(pipeline.predict_proba(row)[0, 1])


def monthly_revenue_forecast(hotel_df: pd.DataFrame, periods: int = 8) -> tuple[pd.DataFrame, pd.DataFrame]:
    monthly = (
        hotel_df.dropna(subset=["arrival_date"])
        .groupby(pd.Grouper(key="arrival_date", freq="MS"))["total_revenue"]
        .sum()
        .reset_index()
        .rename(columns={"arrival_date": "month", "total_revenue": "revenue"})
    )
    monthly = monthly[monthly["revenue"].gt(0)].reset_index(drop=True)
    if len(monthly) < 3:
        return monthly, pd.DataFrame(columns=["month", "forecast", "lower", "upper"])

    monthly["t"] = np.arange(len(monthly))
    monthly["sin"] = np.sin(2 * np.pi * monthly["t"] / 12)
    monthly["cos"] = np.cos(2 * np.pi * monthly["t"] / 12)
    model = LinearRegression()
    model.fit(monthly[["t", "sin", "cos"]], monthly["revenue"])

    future_t = np.arange(len(monthly), len(monthly) + periods)
    future_months = pd.date_range(monthly["month"].max() + pd.offsets.MonthBegin(1), periods=periods, freq="MS")
    future = pd.DataFrame({"month": future_months, "t": future_t})
    future["sin"] = np.sin(2 * np.pi * future["t"] / 12)
    future["cos"] = np.cos(2 * np.pi * future["t"] / 12)
    forecast = model.predict(future[["t", "sin", "cos"]])
    residual = monthly["revenue"] - model.predict(monthly[["t", "sin", "cos"]])
    band = max(float(residual.std()), float(monthly["revenue"].mean() * 0.08))
    future["forecast"] = np.maximum(forecast, 0)
    future["lower"] = np.maximum(future["forecast"] - band, 0)
    future["upper"] = future["forecast"] + band
    return monthly[["month", "revenue"]], future[["month", "forecast", "lower", "upper"]]
