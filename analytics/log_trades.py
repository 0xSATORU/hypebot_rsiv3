import csv
from datetime import datetime

def log_trade(symbol, signal, rsi, response):
    with open("logs/trade_log.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
<<<<<<< HEAD
            datetime.utcnow().isoformat(), symbol, signal, rsi,
            response.get("status"), response.get("details", str(response))
=======
            datetime.utcnow().isoformat(), symbol, signal, rsi, response.get("status"), response.get("details")
>>>>>>> 78efec8b1ea762142e6cb0b25bfea53bd9964f55
        ])
