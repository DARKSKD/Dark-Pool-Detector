
---

# 2️⃣ `docs/TECHNICAL_DOCUMENTATION.md`

```md
# Technical Documentation – Dark Pool Detective Platform

## Backend Design

### app.py
Acts as the core orchestration layer:
- Trade simulation engine
- Detection engine execution
- REST API exposure
- Thread-safe state management

Key responsibilities:
- Generate simulated market trades
- Maintain rolling trade window
- Trigger detection algorithms
- Serve analytics and alerts

---

## Detection Engine (`detection_engine.py`)

### Implemented Algorithms

#### 1. Iceberg Order Detection
Detects repeated trades with:
- Same symbol
- Same price
- Low quantity variance
- High frequency

Purpose:
> Identify large hidden parent orders split into smaller executions.

---

#### 2. Volume Spike Detection
Detects abnormal volume using:
- Mean + N × Std deviation
- Symbol-level aggregation

Purpose:
> Identify sudden institutional participation.

---

#### 3. Order Flow Imbalance
Analyzes BUY vs SELL dominance:
- BUY/SELL ratio
- Directional pressure

Purpose:
> Detect aggressive accumulation or distribution.

---

#### 4. VWAP Deviation
Compares last trade price to VWAP.

Purpose:
> Identify abnormal execution away from fair price.

---

#### 5. Price Impact
Measures net price movement over trade window.

Purpose:
> Quantify market impact caused by large orders.

---

#### 6. Layering Pattern
Detects:
- Frequent side switching
- Minimal price variation

Purpose:
> Identify spoofing or layering behavior.

---

## Investigation Engine (`investigation_engine.py`)

Provides forensic reconstruction tools:

- Trade timelines
- VWAP, volatility, concentration
- Pattern detection (large trades, clustering)
- Correlation analysis between symbols
- Buy/Sell dominance metrics

Designed for **post-alert investigation workflows**.

---

## Frontend Architecture

### app.jsx

Core modules:
- Live Trade Feed
- Active Alerts Panel
- Symbol Forensics View
- Volume Distribution Charts

Visualization:
- D3.js line charts (price)
- Bar charts (volume)
- Severity-based alert highlighting

---

## API Overview

| Endpoint | Purpose |
|--------|--------|
| `/api/start` | Start surveillance |
| `/api/stop` | Stop surveillance |
| `/api/trades` | Fetch recent trades |
| `/api/alerts` | Get active alerts |
| `/api/analytics/summary` | Market summary |
| `/api/analytics/symbol/{symbol}` | Symbol analytics |

---

## Performance Characteristics

- Trade processing: ~1000 trades/min
- Detection latency: < 1 second
- Rolling window size: 500 trades
- Alert deduplication enabled

---

## Security

- Private deployment only
- No external data feeds
- No real market data used
- CORS restricted to frontend

