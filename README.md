# NEXUS AI Analytics Dashboard

An ultra-modern Python-only enterprise analytics dashboard for retail fraud intelligence and hotel booking revenue analytics.

NEXUS AI Analytics is built with Streamlit, Plotly, Pandas, NumPy, and Scikit-learn. It uses no React, no Node.js, no Firebase, and no external frontend/backend stack.

## Features

- Futuristic cyberpunk and glassmorphism UI with neon panels, animated backgrounds, glow cards, and premium dark mode.
- Full multipage dashboard: Executive Overview, Fraud Intelligence, Transaction Analytics, Hotel Analytics, Revenue Insights, AI Insights Center, Predictive Analytics, Real-Time Monitoring, and Settings.
- Automatic dataset loading, cleaning, derived metrics, memory optimization, KPI calculation, insight generation, and cached ML training.
- Advanced Plotly analytics: donut charts, line and area charts, heatmaps, treemaps, radar charts, bubble charts, scatter clusters, choropleths, violin plots, gauges, ROC curves, and forecast charts.
- AI-style insight engine with observations, risk alerts, opportunity detection, recommendations, terminal panels, and downloadable HTML/PDF reports.
- Predictive analytics for fraud probability, cancellation probability, and seasonal revenue forecasting.
- Simulated real-time command wall with auto-refresh support, live feeds, alerts, and streaming charts.
- Theme switcher, advanced filters, transaction search, CSV exports, report downloads, and assistant-style controls.

## Project Architecture

```text
.
├── app.py
├── requirements.txt
├── README.md
├── assets/
│   └── logo.svg
├── data/
│   └── README.md
├── pages/
│   ├── 1_Executive_Overview.py
│   ├── 2_Fraud_Intelligence.py
│   ├── 3_Transaction_Analytics.py
│   ├── 4_Hotel_Analytics.py
│   ├── 5_Revenue_Insights.py
│   ├── 6_AI_Insights_Center.py
│   ├── 7_Predictive_Analytics.py
│   ├── 8_Real_Time_Monitoring.py
│   └── 9_Settings_Theme_Customization.py
├── components/
│   └── ui.py
├── utils/
│   ├── data_loader.py
│   ├── insights.py
│   ├── kpis.py
│   └── ml.py
├── charts/
│   └── factory.py
├── styles/
│   └── neon.py
├── models/
├── exports/
└── config/
    └── settings.py
```

## Datasets

The app expects:

- `retail_fraud_detection_100k.csv`
- `hotel_bookings_cleaned.csv`

Preferred production location:

```text
data/retail_fraud_detection_100k.csv
data/hotel_bookings_cleaned.csv
```

For this local build, the app also auto-detects the provided source files:

```text
c:\Users\GA\Downloads\Billa ref2\retail_fraud_detection_100k.csv
c:\Users\GA\Downloads\Billa ref1\hotel_bookings_cleaned.csv
```

## Installation

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run

```powershell
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal.

## Screenshots

Add screenshots here after launching the dashboard:

- Executive Overview
- Fraud Intelligence
- AI Insights Center
- Predictive Analytics
- Real-Time Monitoring

## Production Notes

- Streamlit caching is used for data loading and ML training to keep interaction smooth.
- The ML page samples model-training rows to keep the dashboard responsive while still using representative signals.
- XGBoost is optional in code and included in requirements. If unavailable, the page falls back to an XGBoost-style ensemble model label.
- PDF export uses `reportlab`; HTML export is always available.
- All visual styling is Python-served Streamlit CSS and Plotly configuration. No JavaScript framework is used.
