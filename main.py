import os
import time
from dotenv import load_dotenv
from core.hyperliquid_api import get_rsi, place_order
from strategies.rsi_strategy import RSIStrategy
from analytics.log_trades import log_trade

load_dotenv("config/.env")

ASSETS = ["BTC", "ETH", "SOL"]
INTERVAL = int(os.getenv("FETCH_INTERVAL_SECONDS", 300))
USD_AMOUNT = float(os.getenv("TRADE_AMOUNT", 50))

strategy = RSIStrategy()

while True:
    print(f"[INFO] Nouvelle analyse toutes les {INTERVAL} secondes.")
    for asset in ASSETS:
        rsi = get_rsi(asset)
        signal = strategy.generate_signal(rsi)
        print(f"[{asset}] RSI: {rsi} → Signal: {signal}")

        try:
            if signal == "buy":
                response = place_order(asset, "buy", USD_AMOUNT)
            elif signal == "sell":
                response = place_order(asset, "sell")
            else:
                continue

            status = response.get("status", "unknown")
            if status == "error":
                print(f"[ERROR] {asset} → {response.get('details')}")
            else:
                print(f"[SUCCESS] {asset} → {signal.upper()} order executed.")

            log_trade(asset, signal, rsi, response)
        except Exception as e:
            print(f"[EXCEPTION] {asset} → {str(e)}")
    time.sleep(INTERVAL)
