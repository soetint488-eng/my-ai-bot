import os
import telebot
import google.generativeai as genai
from flask import Flask
from threading import Thread

# --- Configuration ---
API_KEY = os.environ.get('AIzaSyBCxCKjKQhxg0rpXO5471LvS54XCI1QGdw')
BOT_TOKEN = os.environ.get('8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI')

# Gemini AI Setup
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Telegram Bot Setup
bot = telebot.TeleBot(BOT_TOKEN)

# --- Web Server for Render ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- Bot Commands ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ! ကျွန်တော်က Gemini AI Bot ဖြစ်ပါတယ်။ တစ်ခုခု သိချင်တာရှိရင် မေးမြန်းနိုင်ပါတယ်။")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # AI ဆီက အဖြေတောင်းခြင်း
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "စိတ်မရှိပါနဲ့၊ အမှားတစ်ခု ဖြစ်သွားလို့ပါ။ ခဏနေမှ ပြန်ကြိုးစားကြည့်ပေးပါ။")
        print(f"Error: {e}")

# --- Start Bot ---
if __name__ == "__main__":
    print("Bot is starting...")
    keep_alive()  # Render မှာ လိုအပ်တဲ့ Web Server ကို စတင်ခြင်း
    bot.infinity_polling()
