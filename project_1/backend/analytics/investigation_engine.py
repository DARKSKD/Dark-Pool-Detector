import pandas as pd

class InvestigationEngine:

    def __init__(self, trade_log):
        self.trade_log = pd.DataFrame(trade_log)

    def get_symbol_timeline(self, symbol):
        df = self.trade_log[self.trade_log["symbol"] == symbol]
        return df.tail(50)

    def price_impact(self, symbol):
        df = self.trade_log[self.trade_log["symbol"] == symbol]
        if len(df) < 2:
            return 0
        return round(df.iloc[-1]["price"] - df.iloc[0]["price"], 2)

    def trade_summary(self, symbol):
        df = self.trade_log[self.trade_log["symbol"] == symbol]
        return {
            "Total Trades": len(df),
            "Total Volume": int(df["quantity"].sum()),
            "Buy Volume": int(df[df["side"]=="BUY"]["quantity"].sum()),
            "Sell Volume": int(df[df["side"]=="SELL"]["quantity"].sum())
        }
