from flask import Flask, request
import requests
import pytz
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

# Telegram bot bilgileri
TELEGRAM_BOT_TOKEN = '7789798585:AAEv3QL9S2DZUTVYelRTaMXYLLuZrdz-kt0'
CHAT_ID = '6744699088'

# Günlük satış sayacı
sales_data = {
    'date': datetime.now().strftime('%Y-%m-%d'),
    'total_sales': 0,
    'total_revenue': 0.0,
    'products': defaultdict(lambda: {
        'count': 0,
        'revenue': 0.0
    })
}


# Telegram mesajı göndermek için fonksiyon
def send_telegram_message(text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': text}
    requests.post(url, data=payload)


# Ana sayfa
@app.route('/')
def home():
    return 'Hoş Geldiniz! Webhook, /gumroad-webhook ile aktif.'


# Webhook
@app.route('/gumroad-webhook', methods=['POST'])
def gumroad_webhook():
    global sales_data

    data = request.form.to_dict()
    product = data.get('product_name', 'Bilinmiyor')
    email = data.get('email', 'Bilinmiyor')
    price_cents = int(data.get('price', '0'))
    price_dollars = price_cents / 100

    tz = pytz.timezone('Europe/Istanbul')
    now = datetime.now(tz)
    now_date = now.strftime('%Y-%m-%d')
    now_time = now.strftime('%H:%M:%S')

    # Gün değiştiyse sayaçları sıfırla
    if sales_data['date'] != now_date:
        sales_data = {
            'date': now_date,
            'total_sales': 0,
            'total_revenue': 0.0,
            'products': defaultdict(lambda: {
                'count': 0,
                'revenue': 0.0
            })
        }

    # Günlük sayaçları güncelle
    sales_data['total_sales'] += 1
    sales_data['total_revenue'] += price_dollars
    sales_data['products'][product]['count'] += 1
    sales_data['products'][product]['revenue'] += price_dollars

    # Ürün bazlı liste oluştur
    product_lines = ""
    for prod, stats in sales_data['products'].items():
        product_lines += f"- {prod}: {stats['count']} satış, ${stats['revenue']:.2f} gelir\n"

    message = (f"🛒 Yeni satış!\n\n"
               f"📦 Ürün: {product}\n"
               f"👤 Müşteri: {email}\n"
               f"💰 Tutar: ${price_dollars:.2f}\n"
               f"🕒 Zaman: {now_time}\n"
               f"📅 Tarih: {now_date}\n\n"
               f"📊 Günlük Satış Özeti:\n"
               f"Toplam Satış: {sales_data['total_sales']}\n"
               f"Toplam Gelir: ${sales_data['total_revenue']:.2f}\n"
               f"Ürünler:\n{product_lines}")

    send_telegram_message(message)

    return 'OK'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
