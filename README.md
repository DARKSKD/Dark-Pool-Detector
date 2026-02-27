# Dark Pool Detective Platform

## Overview

The **Dark Pool Detective Platform** is a real-time market surveillance and forensic analytics system designed to detect hidden liquidity patterns, large block trades, and manipulative trading behaviors commonly associated with dark pool activity.

The platform implements multiple **order-flow detection algorithms**, a **real-time visualization dashboard**, and a **forensic investigation suite** to reconstruct suspicious trading behavior.


https://github.com/user-attachments/assets/c8b34209-f872-4e79-ae57-49f620805737








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
```
Frontend (React + D3.js)
|
| REST API (JSON)
|
Backend (Flask)
├── Detection Engine
├── Investigation Engine
├── Trade Simulator (High-TPS Batch Engine)
└── Alert Manager
```

---

## Technology Stack

### Backend
- Python 3.9+
- Flask + Flask-CORS
- Pandas, NumPy
- Multithreading (real-time simulation)
- **Waitress (Production WSGI Server)**

### Frontend
- React 18
- D3.js
- Tailwind CSS
- Vite (Production Build)

---

## Project Structure
```
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
├── data-pipeline/
│ ├── ingestion.py
│ ├── processing.py
│ └── storage.py
│
├── README.md
└── .gitignore

```
---

## Running the Project (Local – PRIVATE)

### Backend
> ⚠️ Flask development server is **not** used for deployment.  
> Backend runs on a **production WSGI server (Waitress)**.

cd backend
python -m venv myenv
source myenv/bin/activate  # Windows: myenv\Scripts\activate
pip install -r requirements.txt
pip install waitress
python app.py

Run backend using Waitress:

``` waitress-serve --host=127.0.0.1 --port=5000 app:app  ```

Backend available at: http://localhost:5000

### Frontend 

cd frontend
npm install
npm run build
npm run preview

Frontend runs at: http://localhost:4173

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


### Future Work:
- Unsupervised anomaly detection using Isolation Forest
- LSTM-based sequence modeling for order flow
- Persistent storage and historical replay
- Integration with real market data feeds
