import requests
import time
import datetime

# ===== CONFIG =====
BOT_TOKEN = "8840298233:AAFaSzKGKlwkQPgIN9jujcGYk-nUPHSUs38"
CHAT_ID = "@PROFIT_ZONE_947"
API_KEY = "aa164586e0b24b348f49fd3b534ce8cc"

PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]
INTERVAL = "1min"

# ===== TELEGRAM =====
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ===== GET DATA =====
def get_data(pair):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": pair,
        "interval": INTERVAL,
        "outputsize": 50,
        "apikey": API_KEY
    }

    res = requests.get(url, params=params).json()

    if "values" not in res:
        print("API error:", pair, res)
        return None

    return res["values"]

# ===== WAIT FOR CANDLE CLOSE =====
def wait_for_candle_close():
    while True:
        now = datetime.datetime.now()
        if now.second >= 58:
            break
        time.sleep(0.5)

# ===== SIGNAL ANALYSIS (PRO LOGIC) =====
def analyze_pair(data):
    closes = [float(c["close"]) for c in reversed(data)]

    current = closes[-1]
    prev = closes[-2]

    score = 0
    signal = None

    # ===== TREND =====
    up_trend = closes[-1] > closes[-2] > closes[-3] > closes[-4]
    down_trend = closes[-1] < closes[-2] < closes[-3] < closes[-4]

    # ===== VOLATILITY FILTER =====
    volatility = max(closes[-5:]) - min(closes[-5:])
    if volatility < 0.0004:
        return None  # sideways

    # ===== MOMENTUM =====
    momentum = abs(current - prev)
    if momentum > 0.0002:
        score += 2

    # ===== PULLBACK ENTRY =====
    if up_trend and current < prev:
        score += 3
        signal = "CALL 📈"

    elif down_trend and current > prev:
        score += 3
        signal = "PUT 📉"

    # ===== TREND BONUS =====
    if up_trend or down_trend:
        score += 2

    if signal is None:
        return None

    return {
        "signal": signal,
        "score": score,
        "price": current
    }

# ===== SEND SIGNAL =====
def send_signal(pair, signal, price):
    now = datetime.datetime.now()

    entry_time = now.strftime("%H:%M:%S")
    expiry_time = (now + datetime.timedelta(minutes=2)).strftime("%H:%M:%S")

    msg = f"""
📊 BINARY SIGNAL (PRO)

Pair: {pair}
Signal: {signal}

⏰ Entry: {entry_time}
⌛ Expiry: {expiry_time}

💰 Price: {price}

🔥 High Probability Setup
"""

    send(msg)

# ===== MAIN LOOP =====
print("🔥 PRO BOT RUNNING...")

while True:
    wait_for_candle_close()
    time.sleep(1)  # ensure candle closed

    best_trade = None

    for pair in PAIRS:
        data = get_data(pair)

        if not data:
            continue

        result = analyze_pair(data)

        if not result:
            continue

        if (best_trade is None) or (result["score"] > best_trade["score"]):
            best_trade = {
                "pair": pair,
                "signal": result["signal"],
                "score": result["score"],
                "price": result["price"]
            }

        time.sleep(2)  # avoid API limit

    # ===== SEND ONLY BEST TRADE =====
    if best_trade and best_trade["score"] >= 5:
        send_signal(
            best_trade["pair"],
            best_trade["signal"],
            best_trade["price"]
        )
    else:
        print("No strong trade (sideways market)")

    time.sleep(60)
