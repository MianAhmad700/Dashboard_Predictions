from __future__ import annotations

import pandas as pd
import streamlit as st

from charts import factory as cf
from components.ui import configure_page, format_number, page_header, render_sidebar, section_title
from utils.data_loader import load_fraud_data, load_hotel_data
from utils.ml import monthly_revenue_forecast, predict_probability, train_cancellation_models, train_fraud_models


configure_page("Predictive Analytics")
controls = render_sidebar()
fraud_df = load_fraud_data(controls["fraud_sample"])
hotel_df = load_hotel_data(controls["hotel_sample"])

page_header(
    "Predictive Analytics",
    "machine learning lab",
    "Train Random Forest, XGBoost, and Logistic Regression models for fraud prediction, cancellation prediction, and revenue forecasting.",
    ["Random Forest", "XGBoost", "Logistic Regression", "Forecasting"],
)

tab_fraud, tab_cancel, tab_revenue = st.tabs(["Fraud Prediction", "Cancellation Prediction", "Revenue Forecasting"])

with tab_fraud:
    fraud_pack = train_fraud_models(fraud_df)
    fraud_results = fraud_pack["results"]
    section_title("Fraud Model Performance")
    perf = pd.DataFrame(
        [
            {
                "Model": name,
                "Accuracy": result["accuracy"],
                "ROC AUC": result["roc_auc"],
                "Average Precision": result["average_precision"],
            }
            for name, result in fraud_results.items()
        ]
    ).sort_values("ROC AUC", ascending=False)
    st.dataframe(perf.style.format({"Accuracy": "{:.3f}", "ROC AUC": "{:.3f}", "Average Precision": "{:.3f}"}), use_container_width=True)
    curves = {name: {"fpr": r["fpr"], "tpr": r["tpr"], "auc": r["roc_auc"]} for name, r in fraud_results.items()}
    st.plotly_chart(cf.roc_curve_plot(curves, "Fraud ROC Curves"), use_container_width=True)

    best = fraud_pack["best_name"]
    st.markdown(f"#### Best Fraud Model: `{best}`")
    imp = fraud_results[best]["importance"]
    st.plotly_chart(cf.bar(imp.sort_values("importance"), "importance", "feature", title="Fraud Feature Importance", orientation="h"), use_container_width=True)

    section_title("Interactive Fraud Prediction Form")
    with st.form("fraud_predict_form"):
        c1, c2, c3, c4 = st.columns(4)
        amount = c1.number_input("Transaction amount", min_value=0.0, value=250.0)
        frequency = c2.number_input("24h frequency", min_value=0, value=5)
        avg_7d = c3.number_input("Avg amount 7d", min_value=0.0, value=120.0)
        failed = c4.number_input("Failed count 24h", min_value=0, value=1)
        c5, c6, c7, c8 = st.columns(4)
        account_age = c5.number_input("Account age days", min_value=0, value=320)
        payment_method = c6.selectbox("Payment method", sorted(fraud_df["payment_method"].unique()))
        device_type = c7.selectbox("Device type", sorted(fraud_df["device_type"].unique()))
        location = c8.selectbox("Location", sorted(fraud_df["location"].unique()))
        c9, c10, c11, c12 = st.columns(4)
        merchant = c9.selectbox("Merchant category", sorted(fraud_df["merchant_category"].unique()))
        is_international = c10.toggle("International", value=False)
        previous = c11.toggle("Previous fraud", value=False)
        unusual = c12.toggle("Unusual amount", value=True)
        c13, c14, c15 = st.columns(3)
        unusual_location = c13.toggle("Unusual location", value=False)
        multiple = c14.toggle("Multiple short-time transactions", value=True)
        velocity = c15.toggle("Velocity flag", value=True)
        model_name = st.selectbox("Model", list(fraud_results.keys()), index=list(fraud_results.keys()).index(best))
        submitted = st.form_submit_button("Predict Fraud Probability", use_container_width=True)
    if submitted:
        row = pd.DataFrame(
            [
                {
                    "transaction_amount": amount,
                    "transaction_frequency_24h": frequency,
                    "avg_transaction_amount_7d": avg_7d,
                    "failed_transaction_count_24h": failed,
                    "account_age_days": account_age,
                    "previous_fraud_flag": int(previous),
                    "unusual_amount_flag": int(unusual),
                    "unusual_location_flag": int(unusual_location),
                    "multiple_transactions_short_time": int(multiple),
                    "high_risk_device_flag": int(device_type in ["Mobile", "Tablet"]),
                    "velocity_flag": int(velocity),
                    "is_international": int(is_international),
                    "payment_method": payment_method,
                    "device_type": device_type,
                    "location": location,
                    "merchant_category": merchant,
                }
            ]
        )
        proba = predict_probability(fraud_pack, model_name, row) * 100
        st.plotly_chart(cf.gauge(proba, "Predicted Fraud Probability"), use_container_width=True)

with tab_cancel:
    cancel_pack = train_cancellation_models(hotel_df)
    cancel_results = cancel_pack["results"]
    section_title("Cancellation Model Performance")
    perf = pd.DataFrame(
        [
            {
                "Model": name,
                "Accuracy": result["accuracy"],
                "ROC AUC": result["roc_auc"],
                "Average Precision": result["average_precision"],
            }
            for name, result in cancel_results.items()
        ]
    ).sort_values("ROC AUC", ascending=False)
    st.dataframe(perf.style.format({"Accuracy": "{:.3f}", "ROC AUC": "{:.3f}", "Average Precision": "{:.3f}"}), use_container_width=True)
    curves = {name: {"fpr": r["fpr"], "tpr": r["tpr"], "auc": r["roc_auc"]} for name, r in cancel_results.items()}
    st.plotly_chart(cf.roc_curve_plot(curves, "Cancellation ROC Curves"), use_container_width=True)

    best = cancel_pack["best_name"]
    st.markdown(f"#### Best Cancellation Model: `{best}`")
    imp = cancel_results[best]["importance"]
    st.plotly_chart(cf.bar(imp.sort_values("importance"), "importance", "feature", title="Cancellation Feature Importance", orientation="h"), use_container_width=True)

    section_title("Interactive Cancellation Prediction Form")
    with st.form("cancel_predict_form"):
        c1, c2, c3, c4 = st.columns(4)
        hotel = c1.selectbox("Hotel", sorted(hotel_df["hotel"].unique()))
        lead_time = c2.number_input("Lead time", min_value=0, value=90)
        adr = c3.number_input("ADR", min_value=0.0, value=125.0)
        total_nights = c4.number_input("Total nights", min_value=0, value=3)
        c5, c6, c7, c8 = st.columns(4)
        adults = c5.number_input("Adults", min_value=0, value=2)
        children = c6.number_input("Children", min_value=0, value=0)
        babies = c7.number_input("Babies", min_value=0, value=0)
        week = c8.number_input("Arrival week", min_value=1, max_value=53, value=30)
        c9, c10, c11, c12 = st.columns(4)
        market_segment = c9.selectbox("Market segment", sorted(hotel_df["market_segment"].unique()))
        channel = c10.selectbox("Distribution channel", sorted(hotel_df["distribution_channel"].unique()))
        deposit = c11.selectbox("Deposit type", sorted(hotel_df["deposit_type"].unique()))
        customer_type = c12.selectbox("Customer type", sorted(hotel_df["customer_type"].unique()))
        c13, c14, c15, c16 = st.columns(4)
        meal = c13.selectbox("Meal", sorted(hotel_df["meal"].unique()))
        country = c14.selectbox("Country", sorted(hotel_df["country"].unique()))
        room = c15.selectbox("Reserved room", sorted(hotel_df["reserved_room_type"].unique()))
        previous_cancellations = c16.number_input("Previous cancellations", min_value=0, value=0)
        model_name = st.selectbox("Cancellation model", list(cancel_results.keys()), index=list(cancel_results.keys()).index(best))
        submitted = st.form_submit_button("Predict Cancellation Probability", use_container_width=True)
    if submitted:
        row = pd.DataFrame(
            [
                {
                    "lead_time": lead_time,
                    "arrival_date_week_number": week,
                    "stays_in_weekend_nights": min(total_nights, 2),
                    "stays_in_week_nights": max(total_nights - 2, 0),
                    "adults": adults,
                    "children": children,
                    "babies": babies,
                    "is_repeated_guest": 0,
                    "previous_cancellations": previous_cancellations,
                    "previous_bookings_not_canceled": 0,
                    "booking_changes": 0,
                    "days_in_waiting_list": 0,
                    "adr": adr,
                    "required_car_parking_spaces": 0,
                    "total_of_special_requests": 1,
                    "total_nights": total_nights,
                    "is_family": int(children + babies > 0),
                    "hotel": hotel,
                    "meal": meal,
                    "country": country,
                    "market_segment": market_segment,
                    "distribution_channel": channel,
                    "deposit_type": deposit,
                    "customer_type": customer_type,
                    "reserved_room_type": room,
                }
            ]
        )
        proba = predict_probability(cancel_pack, model_name, row) * 100
        st.plotly_chart(cf.gauge(proba, "Predicted Cancellation Probability"), use_container_width=True)

with tab_revenue:
    section_title("Revenue Forecasting")
    history, forecast = monthly_revenue_forecast(hotel_df, periods=10)
    if not forecast.empty:
        st.plotly_chart(cf.forecast_chart(history, forecast, "month", "revenue", "forecast", "ML Revenue Forecast"), use_container_width=True)
        st.metric("Next Forecasted Month", format_number(forecast.iloc[0]["forecast"], "$"))
        st.metric("10-Month Forecast Total", format_number(forecast["forecast"].sum(), "$"))
    else:
        st.info("Revenue forecast needs at least three revenue-positive months.")
