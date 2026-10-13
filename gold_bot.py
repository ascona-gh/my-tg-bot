import time
from datetime import datetime
import telebot
import yfinance as yf

# =====================================================================
# НАСТРОЙКИ (Вставьте свои данные вместо текста ниже)
TOKEN = "8638169235:AAH9gGEvhGbsrpUzN96wrDAlfx6KNPqoBGQ"
CHANNEL_ID = "-1003918814475"
# =====================================================================

bot = telebot.TeleBot(TOKEN)

# Хранилище для прошлых цен
last_prices = {
    "gold": None,
    "usd_uah": None,
    "eur_uah": None,
    "btc": None,
    "brent": None
}

# Словарь тикеров Yahoo Finance, адаптированный для Украины
TICKERS = {
    "gold": "GC=F",  # Фьючерс на золото ($)
    "usd_uah": "UAH=X",  # Доллар к гривне (Межбанк) [1 доллар = Х гривен]
    "eur_uah": "EURUAH=X",  # Евро к гривне (Межбанк) [1 евро = Х гривен]
    "btc": "BTC-USD",  # Биткоин к доллару ($)
    "brent": "BZ=F"  # Нефть марки Brent ($)
}


def get_market_data():
    """Функция скачивает актуальные цены"""
    prices = {}
    for key, ticker in TICKERS.items():
        try:
            asset = yf.Ticker(ticker)
            data = asset.history(period="1d")
            if not data.empty:
                prices[key] = round(data['Close'].iloc[-1], 2)
            else:
                prices[key] = None
        except Exception as e:
            print(f"Ошибка при получении {key}: {e}")
            prices[key] = None
    return prices


def format_line(name, emoji, current, last, valuta_sign):
    """Функция красиво оформляет строку с изменением цены"""
    if current is None:
        return f"{emoji} {name}: *Данные недоступны*"

    if last is None:
        return f"{emoji} {name}: **{current}** {valuta_sign}"

    if current != last:
        diff = round(current - last, 2)
        if diff > 0:
            return f"{emoji} {name}: **{current}** {valuta_sign} 📈 (+{diff})"
        else:
            return f"{emoji} {name}: **{current}** {valuta_sign} 📉 ({diff})"

    return f"{emoji} {name}: **{current}** {valuta_sign} ➖"


print("ИИ-мониторинг рынков Украины успешно запущен...")

while True:
    current_prices = get_market_data()

    is_first_run = all(v is None for v in last_prices.values())
    has_changes = any(
        current_prices[key] != last_prices[key]
        for key in TICKERS if current_prices[key] is not None
    )

    if is_first_run or has_changes:
        current_time = datetime.now().strftime("%H:%M:%S")

        text = f"⚡️ **Фінансовий моніторинг на {current_time}**\n\n"

        text += "💵 **Курс валют (Міжбанк):**\n"
        text += format_line("USD / UAH", "🇺🇸", current_prices["usd_uah"], last_prices["usd_uah"], "грн") + "\n"
        text += format_line("EUR / UAH", "🇪🇺", current_prices["eur_uah"], last_prices["eur_uah"], "грн") + "\n\n"

        text += "🪙 **Криптовалюта:**\n"
        text += format_line("Bitcoin (BTC/USD)", "⚡️", current_prices["btc"], last_prices["btc"], "$") + "\n\n"

        text += "🛢 **Сировина та метали:**\n"
        text += format_line("Золото (XAU/USD)", "🟡", current_prices["gold"], last_prices["gold"], "$") + "\n"
        text += format_line("Нафта Brent", "🛢", current_prices["brent"], last_prices["brent"], "$") + "\n"

        try:
            bot.send_message(CHANNEL_ID, text, parse_mode="Markdown")

            for key in TICKERS:
                if current_prices[key] is not None:
                    last_prices[key] = current_prices[key]
        except Exception as e:
            print(f"Ошибка отправки в Telegram: {e}")

    time.sleep(900)
