from flask import Flask, request, jsonify
from telegram import Bot
import os

# =========================
# SETTINGS
# =========================

BOT_TOKEN = "8832991027:AAG1sgsFqZe7cssMSwu5fGxOI5G4cimEsQc"
CHANNEL_ID = "@PROFIT_ZONE_947"

bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

# =========================
# WEBHOOK
# =========================

@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.json

    signal = data.get("signal", "NONE")
    symbol = data.get("symbol", "UNKNOWN")
    price = data.get("price", "0")

    message = f"""
📊 Binary Signal

💱 Pair: {symbol}
📈 Signal: {signal}
💰 Price: {price}

⏰ Expiry: 5-10  Minutes
"""

    bot.send_message(
        chat_id=CHANNEL_ID,
        text=message
    )

    return jsonify({
        "status": "success"
    })

# =========================
# HOME
# =========================

@app.route('/')
def home():
    return "Webhook Bot Running"

# =========================
# START
# =========================

if __name__ == "__main__":
    app.run(port=5000)
