import requests
import pandas as pd
import time
import schedule
from ta.trend import EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator

# ================= CONFIG =================
BOT_TOKEN = "8840298233:AAG0jITQkx_pO2ySn3u44TdHacC5WsKwfhE"
CHAT_ID = "@PROFIT_ZONE_947"

API_KEY = "aa164586e0b24b348f49fd3b534ce8cc"

PAIRS = ["EUR/USD", "GBP/JPY", "USD/JPY"]
INTERVAL = "5min"

# ================= TELEGRAM =================
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Telegram Error:", e)

# ================= SAFE DATA FETCH =================
def get_data(pair):
    try:
        url = "https://api.twelvedata.com/time_series"

        params = {
            "symbol": pair,
            "interval": INTERVAL,
            "outputsize": 100,
            "apikey": API_KEY
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        # ❌ API error check
        if "status" in data and data["status"] == "error":
            print("API Error:", data.get("message"))
            return None

        if "values" not in data:
            print("No data for:", pair)
            return None

        df = pd.DataFrame(data["values"])
        df = df.iloc[::-1]

        df["close"] = df["close"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)

        return df

    except Exception as e:
        print("Data fetch error:", e)
        return None

# ================= STRATEGY =================
def signal(df):
    try:
        df["ema"] = EMAIndicator(df["close"], window=20).ema_indicator()
        df["rsi"] = RSIIndicator(df["close"], window=14).rsi()
        df["adx"] = ADXIndicator(df["high"], df["low"], df["close"], window=14).adx()

        last = df.iloc[-1]
        prev = df.iloc[-2]

        price = last["close"]

        # SIDEWAYS FILTER
        if last["adx"] < 20:
            return None

        # BUY
        if price > last["ema"] and last["rsi"] < 40 and price > prev["close"]:
            return "BUY"

        # SELL
        if price < last["ema"] and last["rsi"] > 60 and price < prev["close"]:
            return "SELL"

        return None

    except Exception as e:
        print("Signal error:", e)
        return None

# ================= SIGNAL SEND =================
def send_signal(pair, sig, price):
    msg = f"""
📊 FOREX SIGNAL

Pair: {pair}
Timeframe: {INTERVAL}

Signal: {sig}
Entry: {price}

📈 Strategy: EMA + RSI + ADX
"""
    send(msg)

# ================= MAIN BOT =================
def run_bot():
    print("Running cycle...")

    for pair in PAIRS:
        df = get_data(pair)

        if df is None or len(df) < 50:
            continue

        sig = signal(df)
        price = df["close"].iloc[-1]

        if sig:
            send_signal(pair, sig, price)

    print("Cycle completed")

# ================= LOOP =================
schedule.every(5).minutes.do(run_bot)

print("Bot Started Successfully...")

import time

while True:
    schedule.run_pending()
    time.sleep(1)
