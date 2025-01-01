import os
import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
from flask import Flask, request
import chardet
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
PORT = int(os.getenv('PORT', 5000))  # Default to port 5000 if PORT is not set
WEBHOOK_URL = f"https://onesyntootg.onrender.com/{TOKEN}"

# Initialize Flask app
app = Flask(__name__)

# Initialize Telegram bot and application
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# Define the start command handler
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Welcome 🙏 to Syntoo's NEPSE💹bot!\n"
        "के को डाटा चाहियो भन्नुस ?\n"
        "म फ्याट्टै खोजिहाल्छु 😂😅\n"
        "Symbol दिनुस जस्तै:- NMB, SHINE, SHPC, SWBBL"
    )

# Define the function to fetch stock data
async def fetch_stock_data(symbol):
    url = f"https://nepse.ct.ws/{symbol}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = chardet.detect(response.content)
            encoding = result['encoding'] if result['encoding'] else 'utf-8'
            soup = BeautifulSoup(response.content.decode(encoding), 'html.parser')

            data = {
                "Symbol": symbol,
                "LTP": soup.find('span', {'id': 'last_price'}).text,
                "Change Percent": soup.find('span', {'id': 'change_percent'}).text,
                "Day High": soup.find('span', {'id': 'day_high'}).text,
                "Day Low": soup.find('span', {'id': 'day_low'}).text,
                "Volume": soup.find('span', {'id': 'volume'}).text,
                "Turn Over": soup.find('span', {'id': 'turn_over'}).text,
                "52 Week High": soup.find('span', {'id': '52_week_high'}).text,
                "52 Week Low": soup.find('span', {'id': '52_week_low'}).text,
                "Down From High%": soup.find('span', {'id': 'down_from_high'}).text,
                "Up From Low%": soup.find('span', {'id': 'up_from_low'}).text,
            }
            return data
        else:
            logger.error(f"Failed to fetch data for {symbol}. HTTP Status Code: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {e}")
        return None

# Define the stock command handler
async def stock(update: Update, context: CallbackContext) -> None:
    symbol = update.message.text.upper()
    data = await fetch_stock_data(symbol)
    if data:
        response = (
            f"Symbol: {data['Symbol']}\n"
            f"LTP: {data['LTP']}\n"
            f"Change Percent: {data['Change Percent']}\n"
            f"Day High: {data['Day High']}\n"
            f"Day Low: {data['Day Low']}\n"
            f"Volume: {data['Volume']}\n"
            f"Turn Over: {data['Turn Over']}\n"
            f"52 Week High: {data['52 Week High']}\n"
            f"52 Week Low: {data['52 Week Low']}\n"
            f"Down From High%: {data['Down From High%']}\n"
            f"Up From Low%: {data['Up From Low%']}"
        )
    else:
        response = (
            f"Symbol ..... 'ल्या, फेला परेन त 🤗🤗।\n"
            f"नआत्तिनु Symbol राम्रो सङ्ग फेरि दिनुस।\n"
            f"म फेरि खोज्छु।"
        )
    await update.message.reply_text(response)

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, stock))

# Flask route for webhook
@app.route(f"/{TOKEN}", methods=['POST'])
def telegram_webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        application.process_update(update)
        return "OK", 200

# Run Flask app
if __name__ == '__main__':
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host='0.0.0.0', port=PORT, debug=True)  # Ensure Flask app runs on the correct port
