import os
import requests
import pandas as pd
import ta

BASE_URL = "https://api.hyperliquid.xyz"
WALLET = os.getenv("WALLET_ADDRESS")

def get_ohlcv(symbol, interval="5m"):
    payload = {"type": "candleSnapshot", "coin": symbol, "interval": interval}
    res = requests.post(BASE_URL + "/info", json=payload)
    candles = res.json().get("data", [])
    if not candles or len(candles[0]) < 6:
        return None
    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["close"] = pd.to_numeric(df["close"])
    return df

def get_rsi(symbol, period=14):
    df = get_ohlcv(symbol)
    if df is None or df.empty:
        return None
    rsi = ta.momentum.RSIIndicator(close=df["close"], window=period).rsi()
    return round(rsi.iloc[-1], 2)

def get_price(symbol):
    df = get_ohlcv(symbol)
    if df is not None and not df.empty:
        return float(df["close"].iloc[-1])
    return 0

def get_position_size(symbol):
    payload = {"type": "allMidsAndPositions", "user": WALLET}
    res = requests.post(BASE_URL + "/info", json=payload)
    if res.status_code == 200:
        positions = res.json().get("positions", [])
        for p in positions:
            if p["coin"] == symbol:
                return float(p["position"]["szi"])
    return 0

def place_order(symbol, side, usd_amount=None):
    px = get_price(symbol)
    if px == 0:
        return {"status": "error", "details": "Price unavailable"}

    if side == "buy" and usd_amount:
        size = round(usd_amount / px, 6)
    elif side == "sell":
        size = get_position_size(symbol)
        if size == 0:
            return {"status": "error", "details": "No position to close"}
    else:
        return {"status": "error", "details": "Invalid side or amount"}

    payload = {
        "type": "order",
        "coin": symbol,
        "isBuy": side == "buy",
        "sz": str(size),
        "limitPx": None,
        "orderType": "market",
        "clientOrderId": "auto-rsi"
    }

    res = requests.post(BASE_URL + "/order", json=payload)
    return res.json()
