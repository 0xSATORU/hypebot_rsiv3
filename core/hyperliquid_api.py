import os
import requests
import pandas as pd
import ta

BASE_URL = "https://api.hyperliquid.xyz"
WALLET = os.getenv("WALLET_ADDRESS")
HYPE_API_KEY = os.getenv("HYPE_API_KEY")
HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {HYPE_API_KEY}"}

def get_ohlc(symbol, interval="5m"):
    payload = {
        "type": "candleSnapshot",
        "coin": symbol,
        "interval": interval
    }
    try:
        res = requests.post(BASE_URL + "/info", json=payload, headers=HEADERS)
        candles = res.json().get("data", [])
        if not candles:
            print(f"[WARN] No OHLC data for {symbol}")
            return None
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["close"] = pd.to_numeric(df["close"])
        return df
    except Exception as e:
        print(f"[ERROR] get_ohlc() failed for {symbol} — {e}")
        return None

def get_rsi(symbol, window=14):
    df = get_ohlc(symbol)
    if df is None or df.empty:
        print(f"[WARN] No data to compute RSI for {symbol}")
        return None
    try:
        rsi = ta.momentum.RSIIndicator(close=df["close"], window=window).rsi()
        return round(rsi.iloc[-1], 2)
    except Exception as e:
        print(f"[ERROR] RSI calculation failed for {symbol} — {e}")
        return None

def get_price(symbol):
    df = get_ohlc(symbol)
    if df is not None and not df.empty:
        return float(df["close"].iloc[-1])
    print(f"[WARN] Could not retrieve price for {symbol}")
    return 0

def get_position_size(symbol):
    payload = {"type": "allMidsAndPositions", "user": WALLET}
    try:
        res = requests.post(BASE_URL + "/info", json=payload, headers=HEADERS)
        if res.status_code == 200:
            positions = res.json().get("positions", [])
            for p in positions:
                if p["coin"] == symbol:
                    return float(p["position"]["szi"])
        print(f"[INFO] No open position for {symbol}")
        return 0
    except Exception as e:
        print(f"[ERROR] get_position_size() failed for {symbol} — {e}")
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

    try:
        res = requests.post(BASE_URL + "/order", json=payload, headers=HEADERS)
        return res.json()
    except Exception as e:
        print(f"[ERROR] Failed to place {side.upper()} order on {symbol} — {e}")
        return {"status": "error", "details": str(e)}
