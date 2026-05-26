from __future__ import annotations

from pathlib import Path


APP_NAME = "NEXUS AI Analytics"
APP_SUBTITLE = "Enterprise Fraud, Revenue, and Hospitality Intelligence"
APP_VERSION = "1.0.0"

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
EXPORT_DIR = ROOT_DIR / "exports"
MODEL_DIR = ROOT_DIR / "models"
ASSET_DIR = ROOT_DIR / "assets"

FRAUD_FILE_NAME = "retail_fraud_detection_100k.csv"
HOTEL_FILE_NAME = "hotel_bookings_cleaned.csv"

FRAUD_DATA_CANDIDATES = [
    ROOT_DIR / FRAUD_FILE_NAME,
    DATA_DIR / FRAUD_FILE_NAME,
    Path(r"c:\Users\GA\Downloads\Billa ref2\retail_fraud_detection_100k.csv"),
]

HOTEL_DATA_CANDIDATES = [
    ROOT_DIR / HOTEL_FILE_NAME,
    DATA_DIR / HOTEL_FILE_NAME,
    Path(r"c:\Users\GA\Downloads\Billa ref1\hotel_bookings_cleaned.csv"),
]

PAGES = [
    ("Executive Overview", "pages/1_Executive_Overview.py"),
    ("Fraud Intelligence", "pages/2_Fraud_Intelligence.py"),
    ("Transaction Analytics", "pages/3_Transaction_Analytics.py"),
    ("Hotel Analytics", "pages/4_Hotel_Analytics.py"),
    ("Revenue Insights", "pages/5_Revenue_Insights.py"),
    ("AI Insights Center", "pages/6_AI_Insights_Center.py"),
    ("Predictive Analytics", "pages/7_Predictive_Analytics.py"),
    ("Real-Time Monitoring", "pages/8_Real_Time_Monitoring.py"),
    ("Settings / Theme", "pages/9_Settings_Theme_Customization.py"),
]

THEMES = {
    "Cyberpunk Violet": {
        "primary": "#8b5cf6",
        "secondary": "#06b6d4",
        "accent": "#f472b6",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "bg": "#030712",
        "panel": "rgba(15, 23, 42, 0.74)",
        "text": "#e5e7eb",
    },
    "Tesla Blue": {
        "primary": "#38bdf8",
        "secondary": "#818cf8",
        "accent": "#2dd4bf",
        "success": "#34d399",
        "warning": "#fbbf24",
        "danger": "#fb7185",
        "bg": "#020617",
        "panel": "rgba(8, 13, 32, 0.78)",
        "text": "#f8fafc",
    },
    "Pink Nebula": {
        "primary": "#ec4899",
        "secondary": "#a855f7",
        "accent": "#22d3ee",
        "success": "#10b981",
        "warning": "#f97316",
        "danger": "#f43f5e",
        "bg": "#090014",
        "panel": "rgba(31, 12, 42, 0.78)",
        "text": "#fdf2f8",
    },
}

DEFAULT_THEME = "Cyberpunk Violet"

RISK_ORDER = ["Low", "Medium", "High", "Critical"]
RISK_COLORS = {
    "Low": "#22c55e",
    "Medium": "#f59e0b",
    "High": "#fb7185",
    "Critical": "#ef4444",
}

COUNTRY_NAME_TO_ISO3 = {
    "United States": "USA",
    "USA": "USA",
    "US": "USA",
    "Canada": "CAN",
    "UK": "GBR",
    "United Kingdom": "GBR",
    "India": "IND",
    "Germany": "DEU",
    "France": "FRA",
    "Spain": "ESP",
    "Italy": "ITA",
    "Brazil": "BRA",
    "Australia": "AUS",
    "China": "CHN",
    "Japan": "JPN",
    "Mexico": "MEX",
    "Netherlands": "NLD",
    "Portugal": "PRT",
}
