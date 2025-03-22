import os
import time
from dotenv import load_dotenv
from core.hyperliquid_api import get_rsi, place_order, get_clean_name
from strategies.rsi_strategy import RSIStrategy
from analytics.log_trades import log_trade

load_dotenv("config/.env")

ASSETS = ["BTC:USDC", "ETH:USDC", "SOL:USDC"]
INTERVAL = int(os.getenv("FETCH_INTERVAL_SECONDS", 300))
USD_AMOUNT = float(os.getenv("TRADE_AMOUNT", 50))

strategy = RSIStrategy()

while True:
    for asset in ASSETS:
        rsi = get_rsi(asset)
        signal = strategy.generate_signal(rsi)
        clean_name = get_clean_name(asset)
        print(f"[{clean_name}] RSI: {rsi} → Signal: {signal}")
        if signal in ["buy", "sell"]:
            response = place_order(asset, signal, USD_AMOUNT)
            log_trade(clean_name, signal, rsi, response)
    time.sleep(INTERVAL)
