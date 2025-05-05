import os
import json
import requests
import asyncio
import nest_asyncio
import logging
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

nest_asyncio.apply()
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = '7555388402:AAGG28Ut14Eq67EveYGJs6RYxLqVkehYiKs'
YOUR_CHAT_ID = 1249180037
DATA_FILE = "tracked_items.json"
CHECK_INTERVAL = 10800  # Every 3 hours

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
}

def delete_webhook():
    try:
        response = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook")
        print("🧹 Webhook delete response:", response.json())
    except Exception as e:
        print("❌ Error deleting webhook:", e)

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        tracked_items = json.load(f)
else:
    tracked_items = []

def save_tracked_items():
    with open(DATA_FILE, "w") as f:
        json.dump(tracked_items, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("✅ /start command received")
    await update.message.reply_text(
        "👋 Welcome to your Price Tracker Bot, Lukas!\n\n"
        "Commands:\n"
        "`add <url> <price>` – start tracking\n"
        "`show all` – list tracked items\n"
        "`remove <number>` – remove item\n",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.strip()
    print("👀 Message received:", message)

    if message.lower().startswith("add"):
        parts = message.split()
        if len(parts) == 3:
            url = parts[1]
            try:
                target_price = float(parts[2])
                if any(item["url"] == url for item in tracked_items):
                    await update.message.reply_text("⚠️ Already tracking this product.")
                else:
                    tracked_items.append({"url": url, "target_price": target_price})
                    save_tracked_items()
                    await update.message.reply_text(f"✅ Now tracking:\n{url}\nTarget: €{target_price}")
            except ValueError:
                await update.message.reply_text("❗ Invalid price format.")
        else:
            await update.message.reply_text("❗ Usage: `add <url> <price>`")

    elif message.lower() == "show all":
        if not tracked_items:
            await update.message.reply_text("📂 No items tracked yet.")
        else:
            text = "🛒 Tracked items:\n\n"
            for i, item in enumerate(tracked_items, 1):
                text += f"{i}. {item['url']} – €{item['target_price']}\n"
            await update.message.reply_text(text, disable_web_page_preview=True)

    elif message.lower().startswith("remove"):
        parts = message.split()
        if len(parts) == 2 and parts[1].isdigit():
            index = int(parts[1]) - 1
            if 0 <= index < len(tracked_items):
                removed = tracked_items.pop(index)
                save_tracked_items()
                await update.message.reply_text(f"🗑️ Removed: {removed['url']}")
            else:
                await update.message.reply_text("❗ Invalid number.")
        else:
            await update.message.reply_text("❗ Usage: `remove <number>`")

    else:
        await update.message.reply_text(
            "❓ Unknown command.\nTry:\n"
            "`add <url> <price>`\n"
            "`show all`\n"
            "`remove <number>`",
            parse_mode="Markdown"
        )

async def check_prices(app):
    while True:
        print("🔍 Checking prices...")
        for item in tracked_items:
            try:
                response = requests.get(item["url"], headers=HEADERS)
                soup = BeautifulSoup(response.content, "html.parser")
                price_tag = soup.find("span", class_="product-price-amount")
                if price_tag:
                    price_text = price_tag.get_text().strip().replace("€", "").replace(",", "").strip()
                    current_price = float(price_text)
                    print(f"[{item['url']}] Current price: €{current_price}")
                    if current_price <= item["target_price"]:
                        message = (
                            f"🔥 Price dropped!\n{item['url']}\n"
                            f"Now: €{current_price} (Target: €{item['target_price']})"
                        )
                        await app.bot.send_message(chat_id=YOUR_CHAT_ID, text=message, disable_web_page_preview=True)
                else:
                    print(f"⚠️ Price not found for {item['url']}")
            except Exception as e:
                print(f"❌ Error checking {item['url']}: {e}")
        await asyncio.sleep(CHECK_INTERVAL)

async def main():
    delete_webhook()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.create_task(check_prices(app))
    print("✅ Bot is ready.")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
