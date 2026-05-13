import os
import asyncio
import requests
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from flask import Flask
from threading import Thread

# --- Configuration ---
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
LIT_TOKEN = "YWMtOs1AxE6JEfGMQK35LXPHlwC3x2A3exHpkKgjudNTjb0ZQwwAzFsR8JWtDRpn0gquAwMAAAGeH7jqmTht7EDd_nns6iTySRbBrvMZueFVp-UzTJHDDF30mKnSJN8Oug"
ORG_APP = "1102190223222824/lit"
BASE_URL = f"http://a1-sgp-ga.easemob.com/{ORG_APP}"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)
is_collecting = False

@app.route('/')
def home(): return "Collector, Spy & Balance Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Balance Check Logic ---
def get_my_balance():
    headers = {"Authorization": f"Bearer {LIT_TOKEN}"}
    try:
        # Litmatch ရဲ့ Wallet API (Version အလိုက် URL ပြောင်းနိုင်သည်)
        r = requests.get(f"{BASE_URL}/users/me/wallet", headers=headers, timeout=5)
        if r.status_code == 200:
            return r.json().get('data', {}).get('diamond', 0)
    except: pass
    return "N/A"

# --- Diamond Collector Logic ---
async def collect_process(chat_id):
    global is_collecting
    session_total = 0 # ဒီတစ်ခေါက်ကောက်လို့ရတဲ့စိန်
    await bot.send_message(chat_id, "🚀 Diamond Collector စတင်ပါပြီ ကိုကို!")
    
    while is_collecting:
        try:
            r = requests.get(f"{BASE_URL}/rooms?limit=10&sort=hot", headers={"Authorization": f"Bearer {LIT_TOKEN}"})
            rooms = r.json().get('entities', [])
            
            for room in rooms:
                if not is_collecting: break
                room_id = room.get('id')
                res = requests.post(f"{BASE_URL}/rooms/{room_id}/diamonds/grab", headers={"Authorization": f"Bearer {LIT_TOKEN}"}, timeout=5)
                
                if res.status_code == 200:
                    amt = res.json().get('amount', 0)
                    if amt > 0:
                        session_total += amt
                        current_bal = get_my_balance()
                        await bot.send_message(chat_id, f"💎 **SUCCESS!**\n━━━━━━━━━━━━━━\n➕ ရရှိစိန်: +{amt}\n📥 ဒီတစ်ခေါက်စုစုပေါင်း: {session_total}\n💰 အကောင့်ထဲရှိစိန်: {current_bal}", parse_mode="Markdown")
                await asyncio.sleep(0.5)
        except: pass
        await asyncio.sleep(5)

# --- Bot Commands ---
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("မင်္ဂလာပါ ကိုကို Dominic!\n\n💰 လက်ရှိစိန်စစ်ရန်: /balance\n💎 စိန်ကောက်ရန်: /collect\n🛑 ရပ်ရန်: /stop\n👤 Profile Spy: User ID ကို ရိုက်ပို့ပါ")

@dp.message_handler(commands=['balance'])
async def balance_cmd(message: types.Message):
    bal = get_my_balance()
    await message.answer(f"💰 **ကိုကို့ရဲ့ လက်ရှိစိန်လက်ကျန်**\n━━━━━━━━━━━━━━\n💎 {bal} Diamonds", parse_mode="Markdown")

@dp.message_handler(commands=['collect'])
async def start_collect(message: types.Message):
    global is_collecting
    if not is_collecting:
        is_collecting = True
        asyncio.create_task(collect_process(message.chat.id))
    else:
        await message.answer("⚠️ Bot က ကောက်နေတုန်းပါ ကိုကို။")

@dp.message_handler(commands=['stop'])
async def stop_collect(message: types.Message):
    global is_collecting
    is_collecting = False
    await message.answer("🛑 Diamond Collector ကို ရပ်လိုက်ပါပြီ။")

@dp.message_handler()
async def handle_spy(message: types.Message):
    if message.text.isdigit():
        headers = {"Authorization": f"Bearer {LIT_TOKEN}"}
        r = requests.get(f"{BASE_URL}/users/{message.text}", headers=headers)
        if r.status_code == 200:
            user_data = r.json().get('entities', [{}])[0]
            nickname = user_data.get('nickname', 'Unknown')
            reg_date = datetime.fromtimestamp(user_data.get('created', 0)/1000).strftime('%Y-%m-%d')
            avatar = user_data.get('avatar', '')
            
            info = f"👤 **User Info**\n📛 Name: {nickname}\n🆔 ID: {message.text}\n📅 Joined: {reg_date}"
            if avatar: await bot.send_photo(message.chat.id, avatar, caption=info)
            else: await message.answer(info)

if __name__ == '__main__':
    Thread(target=run_flask).start()
    executor.start_polling(dp, skip_updates=True)
