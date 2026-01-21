# Inline detection engine used for MVP demo simplicity.
# Canonical engine design is defined in detection_engine.py

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import random
import threading
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global state
class TradingState:
    def __init__(self):
        self.trade_log = []
        self.detector = None
        self.alert_history = []
        self.is_running = False
        self.lock = threading.Lock()
        self.total_trades_generated = 0


state = TradingState()

# Import detection engine classes (simplified inline version)
class DarkPoolDetector:
    def __init__(self):
        self.trade_window = pd.DataFrame()

    def update_trades(self, new_trade):
        self.trade_window = pd.concat([self.trade_window, pd.DataFrame([new_trade])])
        self.trade_window = self.trade_window.tail(3000)

    def iceberg_detector(self):
        grouped = self.trade_window.groupby(['symbol', 'price', 'side'])
        alerts = []
        for (symbol, price, side), grp in grouped:
            if len(grp) > 5 and grp['quantity'].std() < 10:
                total_qty = grp['quantity'].sum()
                avg_qty = grp['quantity'].mean()
                alerts.append({
                    'type': 'Iceberg Order',
                    'severity': 'HIGH',
                    'symbol': symbol,
                    'price': float(price),
                    'side': side,
                    'details': f"{len(grp)} trades, Total: {total_qty}, Avg: {avg_qty:.1f}",
                    'message': f"Iceberg detected: {len(grp)} similar-sized {side} orders at ${price}",
                    'timestamp': datetime.now().isoformat(),
                    'count': len(grp)
                })
        return alerts

    def volume_spike_detector(self):
        alerts = []
        vol = self.trade_window.groupby('symbol')['quantity'].sum()
        if len(vol) > 2:
            mean = vol.mean()
            std = vol.std()
            if std > 0:
                spikes = vol[vol > mean + 3 * std]
                for sym in spikes.index:
                    spike_trades = self.trade_window[self.trade_window['symbol'] == sym]
                    recent_vol = spike_trades.tail(10)['quantity'].sum()
                    alerts.append({
                        'type': 'Volume Spike',
                        'severity': 'MEDIUM',
                        'symbol': sym,
                        'price': float(spike_trades.iloc[-1]['price']),
                        'side': 'BOTH',
                        'details': f"Total: {vol[sym]}, Recent 10: {recent_vol}, Mean: {mean:.0f}",
                        'message': f"Volume spike on {sym}: {vol[sym]} vs avg {mean:.0f}",
                        'timestamp': datetime.now().isoformat(),
                        'count': int(vol[sym])
                    })
        return alerts

    def order_flow_imbalance(self):
        alerts = []
        grouped = self.trade_window.groupby(['symbol', 'side'])['quantity'].sum().unstack().fillna(0)
        for sym, row in grouped.iterrows():
            buy_vol = row.get('BUY', 0)
            sell_vol = row.get('SELL', 1)
            ratio = buy_vol / (sell_vol + 1)
            
            if ratio > 2:
                direction = 'BUY'
                imbalance_pct = ((buy_vol - sell_vol) / (buy_vol + sell_vol)) * 100
            elif ratio < 0.5:
                direction = 'SELL'
                imbalance_pct = ((sell_vol - buy_vol) / (buy_vol + sell_vol)) * 100
            else:
                continue
                
            sym_trades = self.trade_window[self.trade_window['symbol'] == sym]
            alerts.append({
                'type': 'Order Flow Imbalance',
                'severity': 'HIGH',
                'symbol': sym,
                'price': float(sym_trades.iloc[-1]['price']),
                'side': direction,
                'details': f"Buy: {buy_vol:.0f}, Sell: {sell_vol:.0f}, Imbalance: {imbalance_pct:.1f}%",
                'message': f"Strong {direction} pressure on {sym}: {imbalance_pct:.1f}% imbalance",
                'timestamp': datetime.now().isoformat(),
                'count': int(imbalance_pct)
            })
        return alerts

    def run_all(self):
        alerts = []
        alerts.extend(self.iceberg_detector())
        alerts.extend(self.volume_spike_detector())
        alerts.extend(self.order_flow_imbalance())
        
        severity_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 3), reverse=False)
        
        return alerts

state.detector = DarkPoolDetector()

# Background trade generator with varied patterns
# def generate_trades():
#     base_prices = {"AAPL": 150.0, "TSLA": 152.0, "NVDA": 154.0, "GOOGL": 156.0}
    
#     while True:
#         if state.is_running:
#             with state.lock:
#                 symbol = random.choice(["AAPL", "TSLA", "NVDA", "GOOGL"])
                
#                 # Create different trading patterns randomly
#                 pattern = random.choice(['normal', 'iceberg', 'spike', 'imbalance', 'layering'])
                
#                 if pattern == 'iceberg':
#                     # Iceberg: multiple similar-sized orders at same price
#                     price = round(base_prices[symbol], 2)
#                     quantity = random.choice([10, 10, 11, 12, 10])  # Very similar sizes
#                     side = random.choice(["BUY", "SELL"])
                    
#                 elif pattern == 'spike':
#                     # Volume spike: occasional large trade
#                     price = round(base_prices[symbol] + random.uniform(-0.5, 0.5), 2)
#                     quantity = random.choice([10, 10, 15, 50, 800, 1200])  # Occasional spike
#                     side = random.choice(["BUY", "SELL"])
                    
#                 elif pattern == 'imbalance':
#                     # Order flow imbalance: more buys or sells
#                     price = round(base_prices[symbol] + random.uniform(-0.3, 0.3), 2)
#                     quantity = random.choice([10, 20, 50, 100])
#                     side = random.choice(["BUY", "BUY", "BUY", "SELL"])  # 75% buys
                    
#                 elif pattern == 'layering':
#                     # Layering: frequent side switching at similar prices
#                     price = round(base_prices[symbol], 2)
#                     quantity = random.choice([10, 15, 20])
#                     # Alternate sides frequently
#                     side = "BUY" if random.random() > 0.5 else "SELL"
                    
#                 else:  # normal
#                     price = round(base_prices[symbol] + random.uniform(-1, 1), 2)
#                     quantity = random.choice([10, 15, 20, 50, 100, 200])
#                     side = random.choice(["BUY", "SELL"])
                
#                 # Update base price with some drift
#                 base_prices[symbol] += random.uniform(-0.1, 0.1)
                
#                 trade = {
#                     "symbol": symbol,
#                     "price": price,
#                     "quantity": quantity,
#                     "side": side,
#                     "timestamp": datetime.now().isoformat()
#                 }
                
#                 state.trade_log.append(trade)
#                 state.detector.update_trades(trade)
                
#                 # Keep only last 1000 trades
#                 if len(state.trade_log) > 1000:
#                     state.trade_log = state.trade_log[-1000:]
        
#         time.sleep(0.5)
def generate_trades():
    base_prices = {"AAPL": 150.0, "TSLA": 152.0, "NVDA": 154.0, "GOOGL": 156.0}

    min_tps = 1000
    max_tps = 1500   # random bursts above 1000

    while True:
        if state.is_running:
            batch = []
            now = datetime.now().isoformat()

            trades_per_second = random.randint(min_tps, max_tps)
            state.total_trades_generated += trades_per_second


            # ---- FIX 2: dominant pattern per batch ----
            pattern = random.choice(["iceberg", "imbalance", "spike", "normal"])
            dominant_symbol = random.choice(["AAPL", "TSLA", "NVDA", "GOOGL"])
            dominant_price = round(base_prices[dominant_symbol], 2)


            with state.lock:
                for _ in range(trades_per_second):
                    if pattern == "iceberg":
                        symbol = dominant_symbol
                        price = dominant_price
                        quantity = random.choice([10, 10, 11, 12, 10])
                        side = random.choice(["BUY", "SELL"])

                    elif pattern == "imbalance":
                        symbol = dominant_symbol
                        price = round(base_prices[symbol] + random.uniform(-0.1, 0.1), 2)
                        quantity = random.choice([50, 100, 200])
                        side = random.choice(["BUY", "BUY", "BUY", "SELL"])

                    elif pattern == "spike":
                        symbol = dominant_symbol
                        price = round(base_prices[symbol] + random.uniform(-0.5, 0.5), 2)
                        quantity = random.choice([500, 1000, 2000, 5000])
                        side = random.choice(["BUY", "SELL"])

                    else:  # normal
                        symbol = random.choice(["AAPL", "TSLA", "NVDA", "GOOGL"])
                        price = round(base_prices[symbol] + random.uniform(-1, 1), 2)
                        quantity = random.choice([10, 50, 100])
                        side = random.choice(["BUY", "SELL"])

                    trade = {
                        "symbol": symbol,
                        "price": price,
                        "quantity": quantity,
                        "side": side,
                        "timestamp": datetime.now().isoformat()
                    }

                    batch.append(trade)
                    base_prices[symbol] += random.uniform(-0.05, 0.05)


                state.trade_log.extend(batch)

                for trade in batch:
                    state.detector.update_trades(trade)

                if len(state.trade_log) > 10000:
                    state.trade_log = state.trade_log[-10000:]

            # Optional visibility (remove after testing)
            print(f"Generated {trades_per_second} trades in 1 second")

        time.sleep(1)


# Start background thread
trade_thread = threading.Thread(target=generate_trades, daemon=True)
trade_thread.start()

# ==================== API ENDPOINTS ====================

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    with state.lock:
        return jsonify({
            'is_running': state.is_running,
            'total_trades': state.total_trades_generated,
            'total_alerts': len(state.alert_history)
        })

@app.route('/api/start', methods=['POST'])
def start_surveillance():
    """Start live surveillance"""
    state.is_running = True
    return jsonify({'message': 'Surveillance started', 'is_running': True})

@app.route('/api/stop', methods=['POST'])
def stop_surveillance():
    """Stop live surveillance"""
    state.is_running = False
    return jsonify({'message': 'Surveillance stopped', 'is_running': False})

@app.route('/api/clear', methods=['POST'])
def clear_data():
    """Clear all data"""
    with state.lock:
        state.trade_log = []
        state.alert_history = []
        state.detector = DarkPoolDetector()
    return jsonify({'message': 'Data cleared'})

@app.route('/api/trades', methods=['GET'])
def get_trades():
    """Get recent trades"""
    limit = request.args.get('limit', 100, type=int)
    with state.lock:
        trades = state.trade_log[-limit:]
    return jsonify(trades)

@app.route('/api/trades/symbol/<symbol>', methods=['GET'])
def get_trades_by_symbol(symbol):
    """Get trades for a specific symbol"""
    limit = request.args.get('limit', 50, type=int)
    with state.lock:
        symbol_trades = [t for t in state.trade_log if t['symbol'] == symbol]
        trades = symbol_trades[-limit:]
    return jsonify(trades)

# @app.route('/api/alerts', methods=['GET'])
# def get_alerts():
#     """Get current alerts"""
#     with state.lock:
#         alerts = state.detector.run_all()
        
#         # Update alert history
#         for alert in alerts:
#             if alert not in state.alert_history[-10:]:
#                 state.alert_history.append(alert)
        
#         # Keep only last 100 alerts
#         state.alert_history = state.alert_history[-100:]
    
#     return jsonify(alerts)

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """
    Get current active alerts (real-time).
    No deduplication is applied here to ensure
    continuous visibility during live surveillance.
    """
    with state.lock:
        alerts = state.detector.run_all()

        # Store alerts in history (for audit / review only)
        for alert in alerts:
            state.alert_history.append(alert)

        # Keep history bounded
        state.alert_history = state.alert_history[-100:]

    return jsonify(alerts)


@app.route('/api/alerts/history', methods=['GET'])
def get_alert_history():
    """Get alert history"""
    limit = request.args.get('limit', 50, type=int)
    severity = request.args.get('severity', None)
    
    with state.lock:
        alerts = state.alert_history[-limit:]
        
        if severity:
            severities = severity.split(',')
            alerts = [a for a in alerts if a['severity'] in severities]
    
    return jsonify(alerts)

@app.route('/api/analytics/summary', methods=['GET'])
def get_summary():
    """Get overall market summary"""
    with state.lock:
        if len(state.trade_log) == 0:
            return jsonify({})
        
        df = pd.DataFrame(state.trade_log)
        
        summary = {
            'total_trades': state.total_trades_generated,
            'total_volume': int(df['quantity'].sum()),
            'unique_symbols': int(df['symbol'].nunique()),
            'buy_volume': int(df[df['side'] == 'BUY']['quantity'].sum()),
            'sell_volume': int(df[df['side'] == 'SELL']['quantity'].sum()),
            'symbols': df['symbol'].unique().tolist()
        }
    
    return jsonify(summary)

@app.route('/api/analytics/symbol/<symbol>', methods=['GET'])
def get_symbol_analytics(symbol):
    """Get detailed analytics for a symbol"""
    with state.lock:
        df = pd.DataFrame(state.trade_log)
        symbol_df = df[df['symbol'] == symbol]
        
        if len(symbol_df) == 0:
            return jsonify({})
        
        analytics = {
            'symbol': symbol,
            'total_trades': len(symbol_df),
            'total_volume': int(symbol_df['quantity'].sum()),
            'buy_volume': int(symbol_df[symbol_df['side'] == 'BUY']['quantity'].sum()),
            'sell_volume': int(symbol_df[symbol_df['side'] == 'SELL']['quantity'].sum()),
            'current_price': float(symbol_df.iloc[-1]['price']),
            'high': float(symbol_df['price'].max()),
            'low': float(symbol_df['price'].min()),
            'avg_trade_size': float(symbol_df['quantity'].mean()),
            'vwap': float(np.average(symbol_df['price'], weights=symbol_df['quantity']))
        }
        
        if len(symbol_df) > 1:
            analytics['price_change'] = float(symbol_df.iloc[-1]['price'] - symbol_df.iloc[0]['price'])
            analytics['price_change_pct'] = round((analytics['price_change'] / symbol_df.iloc[0]['price']) * 100, 2)
            analytics['volatility'] = float(symbol_df['price'].std())
        
    return jsonify(analytics)

@app.route('/api/analytics/volume-distribution', methods=['GET'])
def get_volume_distribution():
    """Get volume distribution by symbol"""
    with state.lock:
        if len(state.trade_log) == 0:
            return jsonify([])
        
        df = pd.DataFrame(state.trade_log)
        vol_dist = df.groupby('symbol')['quantity'].sum().reset_index()
        vol_dist.columns = ['symbol', 'volume']
        
    return jsonify(vol_dist.to_dict('records'))

@app.route('/api/analytics/buysell-distribution', methods=['GET'])
def get_buysell_distribution():
    """Get buy/sell distribution by symbol"""
    with state.lock:
        if len(state.trade_log) == 0:
            return jsonify([])
        
        df = pd.DataFrame(state.trade_log)
        buysell = df.groupby(['symbol', 'side'])['quantity'].sum().unstack(fill_value=0).reset_index()
        
    return jsonify(buysell.to_dict('records'))

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# if __name__ == '__main__':
#     app.run(debug=True, port=5000, threaded=True)

if __name__ == '__main__':
    print("Run this app using Waitress, not Flask dev server.")
