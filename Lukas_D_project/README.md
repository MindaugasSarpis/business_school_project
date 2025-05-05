# 🛍️ Telegram Price Tracker Bot

Track prices of products and services (like ASOS, Wizzair or Booking.com) and get alerts directly via Telegram when prices drop.

---

## 🤖 Try the Bot

You can try the Telegram bot here 👉 [@DeeptechprojctBot](https://t.me/DeeptechprojctBot)

---

## 📦 Requirements

To run this bot on another PC, install the following Python packages:

- `python-telegram-bot`
- `beautifulsoup4`
- `requests`
- `schedule`
- `nest_asyncio`

```bash
pip install -r requirements.txt
```

---

## 🛠️ Setup Instructions

1. **Clone or Download** this repo and the `price_tracker.py` script  
2. **Create a Telegram Bot** using [@BotFather](https://t.me/BotFather)  
3. Paste your `TELEGRAM_TOKEN` and `YOUR_CHAT_ID` into the script  
4. **Run it** with:

```bash
python3 price_tracker.py
```

---

## 💬 Telegram Commands

```text
add <url> <price>   → Track an item
show all            → List tracked items
remove <number>     → Stop tracking
```

---

## 📸 Screenshot

![image alt](https://github.com/dzisevic19/business_school_project/blob/main/Lukas_D_project/python_app/lukas_d_final/Screenshot%202025-05-04%20at%2018.23.25.png?raw=true)

---

## 🗒️ Notes

- Currently optimized for ASOS, WizzAir product pages.
- More websites can be added by adjusting the HTML parsing logic in `check_prices()`.
- To support sites like Zalando use Selenium or APIs.

---
  
## 🚀 Future Ideas
- Add a web dashboard (Flask)
- Graph price history
- Multi-user support via chat IDs
