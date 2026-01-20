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

state = TradingState()

# Import detection engine classes (simplified inline version)
class DarkPoolDetector:
    def __init__(self):
        self.trade_window = pd.DataFrame()

    def update_trades(self, new_trade):
        if 'timestamp' not in new_trade:
            new_trade['timestamp'] = datetime.now().isoformat()
        new_df = pd.DataFrame([new_trade])
        self.trade_window = pd.concat([self.trade_window, new_df], ignore_index=True)
        self.trade_window = self.trade_window.tail(500)

    def iceberg_detector(self):
        if len(self.trade_window) < 5:
            return []
        grouped = self.trade_window.groupby(['symbol', 'price', 'side'])
        alerts = []
        for (symbol, price, side), grp in grouped:
            if len(grp) >= 5 and grp['quantity'].std() < 5:
                total_qty = int(grp['quantity'].sum())
                avg_qty = float(grp['quantity'].mean())
                alerts.append({
                    'type': 'Iceberg Order',
                    'severity': 'HIGH',
                    'symbol': symbol,
                    'price': float(price),
                    'side': side,
                    'details': f"{len(grp)} trades, Total: {total_qty}, Avg: {avg_qty:.1f}, Std: {grp['quantity'].std():.2f}",
                    'message': f"Iceberg detected: {len(grp)} similar-sized {side} orders at ${price}",
                    'timestamp': datetime.now().isoformat(),
                    'count': len(grp)
                })
        return alerts

    def volume_spike_detector(self):
        if len(self.trade_window) < 5:
            return []
        alerts = []
        vol = self.trade_window.groupby('symbol')['quantity'].sum()
        if len(vol) > 1:
            mean = vol.mean()
            std = vol.std()
            if std > 0:
                spikes = vol[vol > mean + 2 * std]
                for sym in spikes.index:
                    spike_trades = self.trade_window[self.trade_window['symbol'] == sym]
                    recent_vol = int(spike_trades.tail(10)['quantity'].sum())
                    alerts.append({
                        'type': 'Volume Spike',
                        'severity': 'MEDIUM',
                        'symbol': sym,
                        'price': float(spike_trades.iloc[-1]['price']),
                        'side': 'BOTH',
                        'details': f"Total: {int(vol[sym])}, Recent 10: {recent_vol}, Mean: {mean:.0f}, Std: {std:.0f}",
                        'message': f"Volume spike on {sym}: {int(vol[sym])} vs avg {mean:.0f}",
                        'timestamp': datetime.now().isoformat(),
                        'count': int(vol[sym])
                    })
        return alerts

    def order_flow_imbalance(self):
        if len(self.trade_window) < 5:
            return []
        alerts = []
        grouped = self.trade_window.groupby(['symbol', 'side'])['quantity'].sum().unstack().fillna(0)
        for sym, row in grouped.iterrows():
            buy_vol = float(row.get('BUY', 0))
            sell_vol = float(row.get('SELL', 0))
            if buy_vol == 0 and sell_vol == 0:
                continue
            ratio = buy_vol / (sell_vol + 1)
            if ratio > 2.5:
                direction = 'BUY'
                imbalance_pct = ((buy_vol - sell_vol) / (buy_vol + sell_vol)) * 100 if (buy_vol + sell_vol) > 0 else 0
            elif ratio < 0.4:
                direction = 'SELL'
                imbalance_pct = ((sell_vol - buy_vol) / (buy_vol + sell_vol)) * 100 if (buy_vol + sell_vol) > 0 else 0
            else:
                continue
            sym_trades = self.trade_window[self.trade_window['symbol'] == sym]
            alerts.append({
                'type': 'Order Flow Imbalance',
                'severity': 'HIGH',
                'symbol': sym,
                'price': float(sym_trades.iloc[-1]['price']),
                'side': direction,
                'details': f"Buy: {buy_vol:.0f}, Sell: {sell_vol:.0f}, Ratio: {ratio:.2f}, Imbalance: {imbalance_pct:.1f}%",
                'message': f"Strong {direction} pressure on {sym}: {imbalance_pct:.1f}% imbalance",
                'timestamp': datetime.now().isoformat(),
                'count': int(imbalance_pct)
            })
        return alerts

    def vwap_deviation(self):
        if len(self.trade_window) < 3:
            return []
        alerts = []
        for sym in self.trade_window['symbol'].unique():
            df = self.trade_window[self.trade_window['symbol'] == sym]
            if len(df) < 3:
                continue
            vwap = np.average(df['price'], weights=df['quantity'])
            last_price = float(df.iloc[-1]['price'])
            deviation = ((last_price - vwap) / vwap) * 100
            if abs(deviation) > 1.0:
                severity = 'HIGH' if abs(deviation) > 2 else 'MEDIUM'
                alerts.append({
                    'type': 'VWAP Deviation',
                    'severity': severity,
                    'symbol': sym,
                    'price': last_price,
                    'side': 'BUY' if deviation > 0 else 'SELL',
                    'details': f"Current: ${last_price:.2f}, VWAP: ${vwap:.2f}, Deviation: {deviation:.2f}%",
                    'message': f"Price deviation on {sym}: {abs(deviation):.2f}% from VWAP",
                    'timestamp': datetime.now().isoformat(),
                    'count': int(abs(deviation))
                })
        return alerts

    def price_impact(self):
        if len(self.trade_window) < 3:
            return []
        alerts = []
        for sym in self.trade_window['symbol'].unique():
            df = self.trade_window[self.trade_window['symbol'] == sym]
            if len(df) > 2:
                impact = float(df['price'].iloc[-1] - df['price'].iloc[0])
                impact_pct = (impact / df['price'].iloc[0]) * 100 if df['price'].iloc[0] != 0 else 0
                if abs(impact) > 0.5:
                    severity = 'HIGH' if abs(impact) > 1.5 else 'MEDIUM'
                    alerts.append({
                        'type': 'Price Impact',
                        'severity': severity,
                        'symbol': sym,
                        'price': float(df['price'].iloc[-1]),
                        'side': 'BUY' if impact > 0 else 'SELL',
                        'details': f"Start: ${df['price'].iloc[0]:.2f}, End: ${df['price'].iloc[-1]:.2f}, Change: ${impact:.2f}",
                        'message': f"Price moved ${abs(impact):.2f} ({abs(impact_pct):.2f}%) on {sym}",
                        'timestamp': datetime.now().isoformat(),
                        'count': int(abs(impact) * 100)
                    })
        return alerts

    def layering_detector(self):
        if len(self.trade_window) < 8:
            return []
        alerts = []
        for sym in self.trade_window['symbol'].unique():
            df = self.trade_window[self.trade_window['symbol'] == sym].tail(15)
            if len(df) < 8:
                continue
            price_changes = df['price'].diff().abs()
            similar_price_count = (price_changes < 0.1).sum()
            if similar_price_count > len(df) * 0.6:
                side_changes = df['side'].ne(df['side'].shift()).sum()
                if side_changes > len(df) * 0.4:
                    alerts.append({
                        'type': 'Layering Pattern',
                        'severity': 'HIGH',
                        'symbol': sym,
                        'price': float(df['price'].iloc[-1]),
                        'side': 'BOTH',
                        'details': f"Price stability: {similar_price_count}/{len(df)} trades, Side changes: {side_changes}",
                        'message': f"Potential layering detected on {sym}: {side_changes} side switches",
                        'timestamp': datetime.now().isoformat(),
                        'count': side_changes
                    })
        return alerts

    def run_all(self):
        alerts = []
        alerts.extend(self.iceberg_detector())
        alerts.extend(self.volume_spike_detector())
        alerts.extend(self.order_flow_imbalance())
        alerts.extend(self.vwap_deviation())
        alerts.extend(self.price_impact())
        alerts.extend(self.layering_detector())
        
        # Remove duplicates
        unique_alerts = []
        seen = set()
        for alert in alerts:
            key = (alert['type'], alert['symbol'])
            if key not in seen:
                unique_alerts.append(alert)
                seen.add(key)
        
        severity_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        unique_alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))
        return unique_alerts

state.detector = DarkPoolDetector()

# Background trade generator with varied patterns
def generate_trades():
    base_prices = {"AAPL": 150.0, "TSLA": 152.0, "NVDA": 154.0, "GOOGL": 156.0}
    
    while True:
        if state.is_running:
            try:
                with state.lock:
                    symbol = random.choice(["AAPL", "TSLA", "NVDA", "GOOGL"])
                    
                    # Create different trading patterns randomly
                    pattern = random.choice(['normal', 'iceberg', 'spike', 'imbalance', 'layering'])
                    
                    if pattern == 'iceberg':
                        price = round(base_prices[symbol], 2)
                        quantity = random.choice([10, 10, 11, 12, 10])
                        side = random.choice(["BUY", "SELL"])
                    elif pattern == 'spike':
                        price = round(base_prices[symbol] + random.uniform(-0.5, 0.5), 2)
                        quantity = random.choice([10, 10, 15, 50, 800, 1200])
                        side = random.choice(["BUY", "SELL"])
                    elif pattern == 'imbalance':
                        price = round(base_prices[symbol] + random.uniform(-0.3, 0.3), 2)
                        quantity = random.choice([10, 20, 50, 100])
                        side = random.choice(["BUY", "BUY", "BUY", "SELL"])
                    elif pattern == 'layering':
                        price = round(base_prices[symbol], 2)
                        quantity = random.choice([10, 15, 20])
                        side = "BUY" if random.random() > 0.5 else "SELL"
                    else:  # normal
                        price = round(base_prices[symbol] + random.uniform(-1, 1), 2)
                        quantity = random.choice([10, 15, 20, 50, 100, 200])
                        side = random.choice(["BUY", "SELL"])
                    
                    # Update base price with drift
                    base_prices[symbol] += random.uniform(-0.1, 0.1)
                    
                    trade = {
                        "symbol": symbol,
                        "price": price,
                        "quantity": quantity,
                        "side": side,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    state.trade_log.append(trade)
                    state.detector.update_trades(trade)
                    
                    if len(state.trade_log) > 1000:
                        state.trade_log = state.trade_log[-1000:]
            except Exception as e:
                print(f"Error generating trade: {e}")
        
        time.sleep(0.5)

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
            'total_trades': len(state.trade_log),
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
        symbol_trades = [t for t in state.trade_log if t.get('symbol') == symbol]
        trades = symbol_trades[-limit:]
    return jsonify(trades)

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get current alerts"""
    with state.lock:
        alerts = state.detector.run_all()
        
        # Update alert history
        for alert in alerts:
            if alert not in state.alert_history[-10:]:
                state.alert_history.append(alert)
        
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
            alerts = [a for a in alerts if a.get('severity') in severities]
    
    return jsonify(alerts)

@app.route('/api/analytics/summary', methods=['GET'])
def get_summary():
    """Get overall market summary"""
    with state.lock:
        if len(state.trade_log) == 0:
            return jsonify({
                'total_trades': 0,
                'total_volume': 0,
                'unique_symbols': 0,
                'buy_volume': 0,
                'sell_volume': 0,
                'symbols': []
            })
        
        df = pd.DataFrame(state.trade_log)
        
        summary = {
            'total_trades': len(df),
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
        if len(state.trade_log) == 0:
            return jsonify({})
        
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

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5000")
    print("API endpoints available at http://localhost:5000/api/")
    app.run(debug=True, port=5000, threaded=True)