# Backend fetching
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import streamlit as st
import pandas as pd
import random, time
from backend.analytics.detection_engine import DarkPoolDetector
from backend.analytics.investigation_engine import InvestigationEngine

st.set_page_config(page_title="Dark Pool Detective", layout="wide")

# ---------------- SESSION STATE ----------------
if "detector" not in st.session_state:
    st.session_state.detector = DarkPoolDetector()

if "trade_log" not in st.session_state:
    st.session_state.trade_log = []

detector = st.session_state.detector
trade_log = st.session_state.trade_log

st.title("Dark Pool Trading Surveillance Dashboard")

run = st.checkbox("▶ Run Live Surveillance", value=True)

# ---------------- DATA STREAM ----------------
if run:
    trade = {
        "symbol": random.choice(["AAPL", "TSLA"]),
        "price": round(random.uniform(149, 157), 2),
        "quantity": random.choice([10, 10, 10, 50, 200, 500]),
        "side": random.choice(["BUY", "SELL"])
    }

    detector.update_trades(trade)
    trade_log.append(trade)

alerts = detector.run_all()
df = pd.DataFrame(trade_log[-200:])

# ---------------- DASHBOARD ----------------
col1, col2 = st.columns(2)

# 1️⃣ LIVE TRADES
col1.subheader("📈 Live Trades")
col1.dataframe(df.tail(15))

# 2️⃣ ALERTS
col2.subheader("🚨 Active Dark Pool Alerts")
if len(alerts) == 0:
    col2.success("No abnormal dark pool activity detected.")
else:
    for a in alerts[-5:]:
        col2.warning(a)

# 3️⃣ INVESTIGATION TOOLS
st.markdown("---")
st.subheader("🔍 Investigation Console")

selected_symbol = st.selectbox(
    "Select Symbol",
    ["AAPL", "TSLA"],
    key="symbol_selector"
)

investigator = InvestigationEngine(trade_log)

timeline = investigator.get_symbol_timeline(selected_symbol)
summary = investigator.trade_summary(selected_symbol)
impact = investigator.price_impact(selected_symbol)

st.write("### Trade Timeline")
st.dataframe(timeline.tail(20))

st.write("### Forensic Summary")
st.write(summary)
st.write(f"Price Impact: {impact}")

# ---------------- AUTO REFRESH ----------------
if run:
    time.sleep(1)
    st.rerun()
