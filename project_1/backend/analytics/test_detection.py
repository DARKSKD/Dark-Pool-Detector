from detection_engine import DarkPoolDetector
import random

detector = DarkPoolDetector()

# 1. ICEBERG pattern
for _ in range(12):
    detector.update_trades({
        "symbol": "AAPL",
        "price": 150.00,
        "quantity": 10,
        "side": "BUY"
    })

# 2. FLOW IMBALANCE
for _ in range(30):
    detector.update_trades({
        "symbol": "AAPL",
        "price": 150 + random.uniform(-0.2,0.2),
        "quantity": 50,
        "side": "BUY"
    })

for _ in range(5):
    detector.update_trades({
        "symbol": "AAPL",
        "price": 150 + random.uniform(-0.2,0.2),
        "quantity": 10,
        "side": "SELL"
    })

# 3. VOLUME SPIKE
for _ in range(40):
    detector.update_trades({
        "symbol": "TSLA",
        "price": 720,
        "quantity": 500,
        "side": "BUY"
    })

# 4. VWAP DEVIATION + PRICE IMPACT
prices = [150,150,150,150,155,156,157]
for p in prices:
    detector.update_trades({
        "symbol": "AAPL",
        "price": p,
        "quantity": 100,
        "side": "BUY"
    })

alerts = detector.run_all()
print("\nDETECTED ALERTS:\n")
for a in alerts:
    print(a)
