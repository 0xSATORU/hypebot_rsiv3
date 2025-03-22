import csv
from datetime import datetime

def log_trade(symbol, signal, rsi, response):
    with open("logs/trade_log.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.utcnow().isoformat(), symbol, signal, rsi, response.get("status"), response.get("details")
        ])
