# Dark Pool Trading Surveillance System

This project implements a real-time monitoring system for detecting hidden
institutional trading activity in dark pools using rule-based analytics.

## Features
- Real-time trade ingestion (simulated feed)
- 5 detection patterns:
  - Iceberg detection
  - Order flow imbalance
  - VWAP deviation
  - Volume spike detection
  - Price impact analysis
- Live alert dashboard
- Forensic investigation tools

## How to Run

Install dependencies:
pip install streamlit pandas numpy flask scikit-learn plotly

Run dashboard:
streamlit run frontend/dashboard.py
