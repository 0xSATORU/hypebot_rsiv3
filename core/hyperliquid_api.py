import os
import requests

API_KEY = os.getenv("HYPE_API_KEY")
WALLET = os.getenv("WALLET_ADDRESS")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def get_rsi(symbol):
    url = f"https://api.hype.co/v1/indicators/rsi?symbol={symbol}&interval=5m"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json()["rsi"]
    return None

def get_price(symbol):
    url = f"https://api.hype.co/v1/price?symbol={symbol}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return float(res.json().get("price", 0))
    return 0

def place_order(symbol, side, usd_amount):
    price = get_price(symbol)
    if price == 0:
        return {"status": "error", "details": "Price unavailable"}
    size = round(usd_amount / price, 6)
    url = "https://api.hype.co/v1/order"
    payload = {
        "wallet": WALLET,
        "symbol": symbol,
        "side": side,
        "size": size,
        "type": "market"
    }
    res = requests.post(url, headers=HEADERS, json=payload)
    return res.json()

def get_clean_name(symbol):
    return symbol.replace(":USDC", "")
