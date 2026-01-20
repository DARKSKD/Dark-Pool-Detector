# Data Pipeline Layer

CONFIDENTIAL – Property of Zetheta Algorithms Private Limited

---

## Purpose

This directory represents the **logical data pipeline architecture** of the Dark Pool Detective Platform.

Although the MVP uses **in-memory simulated trade data**, this module documents a production-ready
separation of concerns aligned with real-world market surveillance systems.

---

## Pipeline Stages

### 1. Ingestion
Responsible for receiving trade data from:
- Market data feeds (future scope)
- Exchange APIs (future scope)
- Simulated trade generator (current MVP)

---

### 2. Processing
Handles:
- Data normalization
- Timestamp standardization
- Feature preparation for detection algorithms

---

### 3. Storage
Planned persistence layers:
- Time-series databases (TimescaleDB)
- Caching (Redis)
- Object storage (S3)

---

## MVP Note

For the current MVP:
- Data ingestion, processing, and storage are handled **in-memory**
- This folder exists to demonstrate **architecture readiness and scalability**
- No external streaming or databases are used

---

## Future Extensions
- Kafka / WebSocket ingestion
- Stream processing (Flink)
- Persistent audit logs
