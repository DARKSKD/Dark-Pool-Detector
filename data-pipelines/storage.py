"""
Storage Layer

Defines storage interfaces for trade and alert data.

MVP Implementation:
- In-memory storage (Python lists, DataFrames)

Future Scope:
- Time-series databases
- Persistent alert logs
- Audit trails for compliance
"""


class InMemoryStore:
    """
    Simple in-memory store used in MVP.
    """

    def __init__(self):
        self.trades = []
        self.alerts = []

    def store_trade(self, trade: dict):
        self.trades.append(trade)

        # Keep last N trades only
        if len(self.trades) > 1000:
            self.trades = self.trades[-1000:]

    def store_alert(self, alert: dict):
        self.alerts.append(alert)

        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

    def get_trades(self):
        return self.trades

    def get_alerts(self):
        return self.alerts
