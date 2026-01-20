# Dark Pool Detective Platform

CONFIDENTIAL – Property of Zetheta Algorithms Private Limited  
Unauthorized access, use, or distribution is strictly prohibited.

---

## Overview

The **Dark Pool Detective Platform** is a real-time market surveillance and forensic analytics system designed to detect hidden liquidity patterns, large block trades, and manipulative trading behaviors commonly associated with dark pool activity.

The platform implements multiple **order-flow detection algorithms**, a **real-time visualization dashboard**, and a **forensic investigation suite** to reconstruct suspicious trading behavior.

This repository is strictly **PRIVATE** and governed under Zetheta Algorithms IP policies.

---

## Key Capabilities

### Detection Engine
- Iceberg Order Detection
- Volume Spike Detection
- Order Flow Imbalance
- VWAP Deviation
- Price Impact Analysis
- Layering Pattern Detection

### Real-Time Monitoring
- Live trade feed simulation
- Real-time alerts with severity classification
- Market-wide and symbol-level analytics

### Investigation Suite
- Symbol-wise trade timeline reconstruction
- VWAP, volatility, and price impact analysis
- Pattern detection for forensic review
- Trade concentration and correlation analysis

---

## System Architecture

Frontend (React + D3.js)
|
| REST API (JSON)
|
Backend (Flask)
├── Detection Engine
├── Investigation Engine
├── Trade Simulator
└── Alert Manager


---

## Technology Stack

### Backend
- Python 3.9+
- Flask + Flask-CORS
- Pandas, NumPy
- Multithreading (real-time simulation)

### Frontend
- React 18
- D3.js
- Tailwind CSS
- Vite

---

## Project Structure

dark-pool-detective/
│
├── backend/
│ ├── analytics/
│ │ ├── detection_engine.py
│ │ └── investigation_engine.py
│ ├── app.py
│ └── requirements.txt
│
├── frontend/
│ ├── src/
│ │ └── app.jsx
│ ├── package.json
│ └── vite.config.js
│
├── README.md
└── .gitignore


---

## Running the Project (Local – PRIVATE)

### Backend

cd backend
python -m venv myenv
source myenv/bin/activate  # Windows: myenv\Scripts\activate
pip install -r requirements.txt
python app.py

Backend runs at: http://localhost:5000

### Frontend 

cd frontend
npm install
npm run dev

Frontend runs at: http://localhost:5173

### Confidentiality & IP Notice

All code and concepts are the exclusive property of Zetheta Algorithms Private Limited

No public deployment, forks, or sharing permitted

Repository ownership must be transferred to @ZethetaIntern

All local copies must be deleted post handover

### Status

✔ MVP Complete
✔ Detection Engine Functional
✔ Real-Time Dashboard Operational
✔ Investigation Suite Implemented
✔ Ready for Final Demo & IP Transfer

