import pandas as pd
import numpy as np
from datetime import datetime

class InvestigationEngine:

    def __init__(self, trade_log):
        """Initialize with trade log (list of dicts or DataFrame)"""
        if isinstance(trade_log, list):
            self.trade_log = pd.DataFrame(trade_log)
        else:
            self.trade_log = trade_log

    def get_symbol_timeline(self, symbol):
        """Get recent trade timeline for a symbol"""
        if len(self.trade_log) == 0:
            return pd.DataFrame()
        
        df = self.trade_log[self.trade_log["symbol"] == symbol]
        return df.tail(50)

    def price_impact(self, symbol):
        """Calculate price impact for a symbol"""
        df = self.trade_log[self.trade_log["symbol"] == symbol]
        
        if len(df) < 2:
            return 0
        
        return round(float(df.iloc[-1]["price"] - df.iloc[0]["price"]), 2)

    def trade_summary(self, symbol):
        """Get basic trade summary for a symbol"""
        df = self.trade_log[self.trade_log["symbol"] == symbol]
        
        if len(df) == 0:
            return {
                "Total Trades": 0,
                "Total Volume": 0,
                "Buy Volume": 0,
                "Sell Volume": 0
            }
        
        return {
            "Total Trades": len(df),
            "Total Volume": int(df["quantity"].sum()),
            "Buy Volume": int(df[df["side"] == "BUY"]["quantity"].sum()),
            "Sell Volume": int(df[df["side"] == "SELL"]["quantity"].sum())
        }

    def advanced_metrics(self, symbol):
        """Calculate advanced trading metrics for a symbol"""
        df = self.trade_log[self.trade_log["symbol"] == symbol]
        
        if len(df) < 2:
            return {}
        
        metrics = {}
        
        # VWAP
        if len(df) > 0:
            metrics['VWAP'] = round(float(np.average(df['price'], weights=df['quantity'])), 2)
        
        # Price metrics
        metrics['High'] = round(float(df['price'].max()), 2)
        metrics['Low'] = round(float(df['price'].min()), 2)
        metrics['Current'] = round(float(df.iloc[-1]['price']), 2)
        metrics['Price Change'] = round(float(df.iloc[-1]['price'] - df.iloc[0]['price']), 2)
        
        if df.iloc[0]['price'] != 0:
            metrics['Price Change %'] = round((metrics['Price Change'] / float(df.iloc[0]['price'])) * 100, 2)
        else:
            metrics['Price Change %'] = 0
        
        # Volume metrics
        metrics['Avg Trade Size'] = round(float(df['quantity'].mean()), 2)
        metrics['Max Trade Size'] = int(df['quantity'].max())
        metrics['Min Trade Size'] = int(df['quantity'].min())
        
        # Order flow
        buy_vol = float(df[df['side'] == 'BUY']['quantity'].sum())
        sell_vol = float(df[df['side'] == 'SELL']['quantity'].sum())
        total_vol = buy_vol + sell_vol
        
        if total_vol > 0:
            metrics['Buy/Sell Ratio'] = round(buy_vol / (sell_vol + 1), 2)
            metrics['Buy %'] = round((buy_vol / total_vol) * 100, 1)
            metrics['Sell %'] = round((sell_vol / total_vol) * 100, 1)
        else:
            metrics['Buy/Sell Ratio'] = 0
            metrics['Buy %'] = 0
            metrics['Sell %'] = 0
        
        # Volatility
        if len(df) > 1:
            metrics['Price Volatility'] = round(float(df['price'].std()), 2)
            metrics['Volume Volatility'] = round(float(df['quantity'].std()), 2)
        
        return metrics

    def detect_patterns(self, symbol):
        """Detect trading patterns for forensic analysis"""
        df = self.trade_log[self.trade_log["symbol"] == symbol]
        patterns = []
        
        if len(df) < 5:
            return patterns
        
        # Large trades
        large_threshold = df['quantity'].quantile(0.9)
        large_trades = df[df['quantity'] > large_threshold]
        
        if len(large_trades) > 0:
            patterns.append({
                'pattern': 'Large Trades',
                'count': len(large_trades),
                'description': f"{len(large_trades)} trades above 90th percentile ({large_threshold:.0f} shares)"
            })
        
        # Clustering (trades at same price)
        price_counts = df['price'].value_counts()
        clustered = price_counts[price_counts > 5]
        
        if len(clustered) > 0:
            patterns.append({
                'pattern': 'Price Clustering',
                'count': len(clustered),
                'description': f"{len(clustered)} price levels with 5+ trades"
            })
        
        # Rapid sequence trades (if timestamp available)
        if 'timestamp' in df.columns:
            df_sorted = df.sort_values('timestamp').copy()
            
            # Convert timestamp strings to datetime if needed
            if df_sorted['timestamp'].dtype == 'object':
                try:
                    df_sorted['timestamp'] = pd.to_datetime(df_sorted['timestamp'])
                    time_diffs = df_sorted['timestamp'].diff()
                    rapid = time_diffs[time_diffs < pd.Timedelta(seconds=2)]
                    
                    if len(rapid) > 3:
                        patterns.append({
                            'pattern': 'Rapid Trading',
                            'count': len(rapid),
                            'description': f"{len(rapid)} trades within 2 seconds of previous trade"
                        })
                except:
                    pass  # Skip if timestamp conversion fails
        
        # Repeated quantities
        qty_counts = df['quantity'].value_counts()
        repeated = qty_counts[qty_counts > 5]
        
        if len(repeated) > 0:
            top_repeated = list(repeated.index[:3])
            patterns.append({
                'pattern': 'Repeated Quantities',
                'count': len(repeated),
                'description': f"Same quantities repeated 5+ times: {top_repeated}"
            })
        
        # Side switching patterns
        if len(df) > 10:
            switches = df['side'].ne(df['side'].shift()).sum()
            switch_rate = switches / len(df)
            
            if switch_rate > 0.6:
                patterns.append({
                    'pattern': 'High Side Switching',
                    'count': switches,
                    'description': f"Frequent buy/sell alternation: {switch_rate*100:.1f}% switch rate"
                })
        
        return patterns

    def time_distribution(self, symbol):
        """Analyze trade distribution over time"""
        df = self.trade_log[self.trade_log["symbol"] == symbol]
        
        if len(df) < 2:
            return {}
        
        # Sort by timestamp if available
        if 'timestamp' in df.columns:
            try:
                df_sorted = df.sort_values('timestamp')
            except:
                df_sorted = df
        else:
            df_sorted = df
        
        # Recent activity windows
        if len(df_sorted) > 0:
            last_10 = df_sorted.tail(10)
            last_20 = df_sorted.tail(20)
            last_50 = df_sorted.tail(50)
            
            return {
                'Last 10 trades volume': int(last_10['quantity'].sum()),
                'Last 20 trades volume': int(last_20['quantity'].sum()),
                'Last 50 trades volume': int(last_50['quantity'].sum()),
                'Recent avg size': round(float(last_10['quantity'].mean()), 1),
                'Total trades': len(df_sorted)
            }
        
        return {}

    def correlation_analysis(self, symbol1, symbol2):
        """Analyze correlation between two symbols"""
        df1 = self.trade_log[self.trade_log["symbol"] == symbol1]
        df2 = self.trade_log[self.trade_log["symbol"] == symbol2]
        
        if len(df1) < 5 or len(df2) < 5:
            return None
        
        # Price correlation
        try:
            corr = np.corrcoef(
                df1.tail(min(len(df1), 50))['price'],
                df2.tail(min(len(df2), 50))['price']
            )[0, 1]
            
            return {
                'Price Correlation': round(float(corr), 3),
                'Interpretation': 'Strong' if abs(corr) > 0.7 else 'Moderate' if abs(corr) > 0.4 else 'Weak'
            }
        except:
            return None

    def trade_concentration(self, symbol):
        """Analyze concentration of trades"""
        df = self.trade_log[self.trade_log["symbol"] == symbol]
        
        if len(df) < 5:
            return {}
        
        # Price concentration
        price_range = float(df['price'].max() - df['price'].min())
        price_std = float(df['price'].std())
        
        # Volume concentration
        top_5_trades = df.nlargest(5, 'quantity')['quantity'].sum()
        total_volume = df['quantity'].sum()
        
        concentration_pct = round((float(top_5_trades) / float(total_volume)) * 100, 1) if total_volume > 0 else 0
        
        return {
            'Price Range': round(price_range, 2),
            'Price Std Dev': round(price_std, 2),
            'Top 5 Trades % of Volume': concentration_pct,
            'Unique Price Levels': int(df['price'].nunique())
        }