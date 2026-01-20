"""
Ingestion Layer

This module defines the ingestion interface for trade data entering the system.

In the current MVP:
- Trade ingestion is simulated inside app.py
- Trades are generated internally for demonstration purposes

Future Scope:
- Connect to live exchange feeds
- Integrate broker or ATS data
- Consume Kafka / WebSocket streams
"""

from datetime import datetime


def ingest_trade(trade: dict) -> dict:
    """
    Standardizes incoming trade data.

    Parameters:
    trade (dict): Raw trade event

    Returns:
    dict: Normalized trade event
    """

    return {
        "symbol": trade.get("symbol"),
        "price": float(trade.get("price")),
        "quantity": int(trade.get("quantity")),
        "side": trade.get("side"),
        "timestamp": trade.get("timestamp", datetime.now().isoformat())
    }
