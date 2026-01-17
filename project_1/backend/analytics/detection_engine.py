import pandas as pd
import numpy as np

class DarkPoolDetector:

    def __init__(self):
        self.trade_window = pd.DataFrame()

    def update_trades(self, new_trade):
        self.trade_window = pd.concat([self.trade_window, pd.DataFrame([new_trade])])
        self.trade_window = self.trade_window.tail(500)

    def iceberg_detector(self):
        grouped = self.trade_window.groupby(['symbol', 'price', 'side'])
        alerts = []
        for (symbol, price, side), grp in grouped:
            if len(grp) > 8 and grp['quantity'].std() < 2:
                alerts.append(f"Iceberg suspected on {symbol} at {price}")
        return alerts

    def volume_spike_detector(self):
        alerts = []
        vol = self.trade_window.groupby('symbol')['quantity'].sum()
        if len(vol) > 10:
            mean = vol.mean()
            std = vol.std()
            spikes = vol[vol > mean + 3 * std]
            for sym in spikes.index:
                alerts.append(f"Volume spike detected on {sym}")
        return alerts

    def order_flow_imbalance(self):
        alerts = []
        grouped = self.trade_window.groupby(['symbol', 'side'])['quantity'].sum().unstack().fillna(0)
        for sym, row in grouped.iterrows():
            if row.get('BUY',0) / (row.get('SELL',1) + 1) > 4:
                alerts.append(f"Order flow imbalance on {sym}")
        return alerts

    def vwap_deviation(self):
        alerts = []
        for sym in self.trade_window['symbol'].unique():
            df = self.trade_window[self.trade_window['symbol']==sym]
            vwap = np.average(df['price'], weights=df['quantity'])
            last_price = df.iloc[-1]['price']
            if abs(last_price - vwap) / vwap > 0.02:
                alerts.append(f"VWAP deviation on {sym}")
        return alerts

    def price_impact(self):
        alerts = []
        for sym in self.trade_window['symbol'].unique():
            df = self.trade_window[self.trade_window['symbol']==sym]
            if len(df) > 5:
                impact = df['price'].iloc[-1] - df['price'].iloc[0]
                if abs(impact) > 1:
                    alerts.append(f"High price impact on {sym}")
        return alerts

    def run_all(self):
        alerts = []
        alerts.extend(self.iceberg_detector())
        alerts.extend(self.volume_spike_detector())
        alerts.extend(self.order_flow_imbalance())
        alerts.extend(self.vwap_deviation())
        alerts.extend(self.price_impact())
        return alerts
