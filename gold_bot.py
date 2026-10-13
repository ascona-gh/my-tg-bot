import time
import json
from datetime import datetime
import urllib.request

# =====================================================================
# НАСТРОЙКИ (Вставьте свои данные вместо текста ниже)
TOKEN = "СЮДА_ВСТАВЬТЕ_ТОКЕН_ОТ_BOTFATHER"
CHANNEL_ID = "СЮДА_ВСТАВЬТЕ_ID_КАНАЛА_С_МИНУСОМ"
# =====================================================================

last_prices = {"usd": None, "eur": None, "btc": None, "gold": None}

def send_telegram_message(text):
    """Отправка сообщения через встроенную библиотеку urllib"""
    url = f"https://telegram.org{TOKEN}/sendMessage"
    data = json.dumps({"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown"}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            return response.read()
    except Exception as e:
        print(f"Ошибка отправки в TG: {e}")

def get_prices():
    prices = {"usd": None, "eur": None, "btc": None, "gold": None}
    try:
        # 1. Курс НБУ (Доллар и Евро)
        req_nbu = urllib.request.Request("https://bank.gov.ua", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_nbu) as response:
            res_nbu = json.loads(response.read().decode('utf-8'))
            for item in res_nbu:
                if item['cc'] == 'USD': prices['usd'] = round(item['rate'], 2)
                elif item['cc'] == 'EUR': prices['eur'] = round(item['rate'], 2)
                
        # 2. Биткоин и Золото через CoinGecko
        req_cg = urllib.request.Request("https://coingecko.com", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_cg) as response:
            res_cg = json.loads(response.read().decode('utf-8'))
            prices['btc'] = round(res_cg['bitcoin']['usd'], 2)
            prices['gold'] = round(res_cg['tether-gold']['usd'], 2)
    except Exception as e:
        print(f"Ошибка получения данных: {e}")
    return prices

def format_line(name, emoji, current, last, sign):
    if current is None: return f"{emoji} {name}: *немає даних*"
    if last is None: return f"{emoji} {name}: **{current}** {sign}"
    if current != last:
        diff = round(current - last, 2)
        arrow = "📈 (+)" if diff > 0 else "📉 (-)"
        return f"{emoji} {name}: **{current}** {sign} {arrow}{abs(diff)}"
    return f"{emoji} {name}: **{current}** {sign} ➖"

print("Супер-облегченный автономный бот запущен...")

while True:
    curr = get_prices()
    has_changes = any(curr[k] != last_prices[k] for k in curr if curr[k] is not None)
    
    if has_changes or all(v is None for v in last_prices.values()):
        dt = datetime.now().strftime("%H:%M:%S")
        text = f"⚡️ **Фінансовий моніторинг на {dt}**\n\n"
        text += "💵 **Офіційний курс НБУ:**\n"
        text += format_line("USD / UAH", "🇺🇸", curr["usd"], last_prices["usd"], "грн") + "\n"
        text += format_line("EUR / UAH", "🇪🇺", curr["eur"], last_prices["eur"], "грн") + "\n\n"
        text += "🪙 **Світові активи (USD):**\n"
        text += format_line("Bitcoin", "⚡️", curr["btc"], last_prices["btc"], "$") + "\n"
        text += format_line("Золото (XAU)", "🟡", curr["gold"], last_prices["gold"], "$") + "\n"
        
        send_telegram_message(text)
        for k in curr:
            if curr[k] is not None: last_prices[k] = curr[k]
            
    time.sleep(900)
