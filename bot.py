import logging
import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from flask import Flask
from threading import Thread

# --- Configuration ---
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk' # ကိုကို့ Bot Token
LIT_TOKEN = "YWMtOs1AxE6JEfGMQK35LXPHlwC3x2A3exHpkKgjudNTjb0ZQwwAzFsR8JWtDRpn0gquAwMAAAGeH7jqmTht7EDd_nns6iTySRbBrvMZueFVp-UzTJHDDF30mKnSJN8Oug"
BASE_URL = "http://a1-sgp-ga.easemob.com/1102190223222824/lit"

# Initialize Bot and Flask
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)

# --- Flask for Render (Port Listening) ---
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Telegram Bot Commands ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("မင်္ဂလာပါ ကိုကို Dominic! စကားပြောဖူးသူစာရင်း ကြည့်ချင်ရင် /list လို့ ပို့ပေးပါဗျ။")

@dp.message_handler(commands=['list'])
async def list_users(message: types.Message):
    await message.answer("🔍 စာရင်းကို ရှာဖွေနေပါတယ်၊ ခဏစောင့်ပါ...")
    
    url = f"{BASE_URL}/users/love144883120849408/contacts/users"
    headers = {"Authorization": f"Bearer {LIT_TOKEN}"}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        users = r.json().get('data', [])
        
        if not users:
            await message.answer("⚠️ စကားပြောဖူးသူ မတွေ့ပါဘူး ကိုကို။")
            return

        text = "📋 **စကားပြောဖူးသူများ စာရင်း**\n━━━━━━━━━━━━━━\n"
        for i, name in enumerate(users, 1):
            text += f"{i}။ {name}\n"
        
        await message.answer(text, parse_mode="Markdown")
    except:
        await message.answer("❌ Litmatch Server နဲ့ ချိတ်ဆက်လို့မရပါဘူး ကိုကို။")

# --- Start ---
if __name__ == '__main__':
    # Flask ကို Background မှာ Run မယ်
    Thread(target=run_flask).start()
    # Telegram Bot ကို Run မယ်
    executor.start_polling(dp, skip_updates=True)
