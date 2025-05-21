# Hyperliquid Wallet Tracker Bot

A Telegram bot that tracks Hyperliquid wallet position changes and sends notifications.

## Features

- Add/remove wallets via Telegram
- Monitor position opens, closes, and modifications
- Sends position details, margin size, PnL, liquidation price
- Logs to `bot.log`
- Deployable to Railway or Render

## Deployment

1. Clone the repo.
2. Set your `TELEGRAM_TOKEN` in Railway or `.env`.
3. `pip install -r requirements.txt`
4. `python bot.py` to run locally.

Use `/add <wallet>` and `/remove <wallet>` in Telegram to track wallets.
