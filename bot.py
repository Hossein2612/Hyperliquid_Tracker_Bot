import os
import json
import time
import logging
import requests
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from utils import load_wallets, save_wallets, format_position, diff_positions

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHECK_INTERVAL = 30  # seconds
WALLET_FILE = "wallets.json"

logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

bot = Bot(token=TELEGRAM_TOKEN)
wallet_data = load_wallets(WALLET_FILE)

def add_wallet(update: Update, context: CallbackContext):
    if context.args:
        wallet = context.args[0]
        chat_id = str(update.effective_chat.id)
        wallet_data.setdefault(chat_id, []).append(wallet)
        save_wallets(WALLET_FILE, wallet_data)
        update.message.reply_text(f"✅ Added wallet: {wallet}")
    else:
        update.message.reply_text("Usage: /add <wallet_address>")

def remove_wallet(update: Update, context: CallbackContext):
    if context.args:
        wallet = context.args[0]
        chat_id = str(update.effective_chat.id)
        if chat_id in wallet_data and wallet in wallet_data[chat_id]:
            wallet_data[chat_id].remove(wallet)
            save_wallets(WALLET_FILE, wallet_data)
            update.message.reply_text(f"🗑️ Removed wallet: {wallet}")
        else:
            update.message.reply_text("Wallet not found.")
    else:
        update.message.reply_text("Usage: /remove <wallet_address>")

def list_wallets(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)
    if chat_id in wallet_data and wallet_data[chat_id]:
        wallets = "\n".join(wallet_data[chat_id])
        update.message.reply_text(f"📜 Watching wallets:\n{wallets}")
    else:
        update.message.reply_text("No wallets being tracked.")

def check_wallets():
    while True:
        for chat_id, wallets in wallet_data.items():
            for wallet in wallets:
                try:
                    url = f"https://api.hyperliquid.xyz/info"
                    payload = {
                        "type": "userState",
                        "user": wallet
                    }
                    r = requests.post(url, json=payload)
                    data = r.json()

                    positions = data.get("assetPositions", [])
                    prev = load_wallets(f"prev_{wallet}.json").get("positions", [])
                    changes = diff_positions(prev, positions)

                    for change in changes:
                        msg = format_position(wallet, change)
                        bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
                        logging.info(f"Change detected: {msg}")

                    save_wallets(f"prev_{wallet}.json", {"positions": positions})

                except Exception as e:
                    logging.error(f"Error checking wallet {wallet}: {e}")

        time.sleep(CHECK_INTERVAL)

def run_bot():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("add", add_wallet))
    dp.add_handler(CommandHandler("remove", remove_wallet))
    dp.add_handler(CommandHandler("list", list_wallets))

    updater.start_polling()
    logging.info("Bot started.")
    check_wallets()

if __name__ == "__main__":
    run_bot()
