import requests
import time
import schedule
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import deque
from datetime import datetime

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = "vedomylidr@gmail.com"
APP_PASSWORD = "nqie kbgm amiy drsc"

RECEIVER_EMAIL = "vedomylidr@gmail.com"

COINS = {
    "BTCUSDT": 3,
    "ETHUSDT": 4,
    "SOLUSDT": 5,
}

INTERVAL_MINUTES = 5

price_history = {
    coin: deque(maxlen=INTERVAL_MINUTES)
    for coin in COINS
}

last_alert = {}

def get_price(symbol):

    ids = {
        "BTCUSDT": "bitcoin",
        "ETHUSDT": "ethereum",
        "SOLUSDT": "solana"
    }

    coin_id = ids[symbol]

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"

    response = requests.get(url)

    data = response.json()

    return float(data[coin_id]["usd"])

def send_email(subject, body):

    msg = MIMEMultipart()

    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)

    server.starttls()

    server.login(SENDER_EMAIL, APP_PASSWORD)

    server.send_message(msg)

    server.quit()

def check_market():

    print(f"Kontrola trhu: {datetime.now()}")

    for coin, threshold in COINS.items():

        try:
            current_price = get_price(coin)

            history = price_history[coin]

            history.append(current_price)

            if len(history) < INTERVAL_MINUTES:
                continue

            old_price = history[0]

            percent_change = ((current_price - old_price) / old_price) * 100

            print(f"{coin}: {percent_change:.2f}%")

            now = time.time()

            if coin in last_alert:
                if now - last_alert[coin] < 900:
                    continue

            if abs(percent_change) >= threshold:

                direction = "ROSTE 🚀" if percent_change > 0 else "KLESÁ 📉"

                subject = f"{coin} {direction} {percent_change:.2f}%"

                body = f"""
Coin: {coin}

Směr: {direction}

Změna: {percent_change:.2f}%

Aktuální cena: {current_price:.2f} USD

Čas: {datetime.now()}
"""

                send_email(subject, body)

                print(f"ALERT ODESLÁN: {coin}")

                last_alert[coin] = now

        except Exception as e:
            print(f"Chyba u {coin}: {e}")

schedule.every(1).minutes.do(check_market)

print("BTC/ETH/SOL alert bot spuštěn...")

while True:
    schedule.run_pending()
    time.sleep(1)
