import logging
import os
import requests
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

@app.route('/')
def home(): return "Bot Active!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Logic to Try Multiple Endpoints ---
def fetch_litmatch_users():
    headers = {"Authorization": f"Bearer {LIT_TOKEN}"}
    
    # စမ်းသပ်မယ့် လမ်းကြောင်းများ
    endpoints = [
        f"{BASE_URL}/users/me/contacts/users",
        f"{BASE_URL}/chatmessages",
        f"{BASE_URL}/users/love144883120849408/contacts/users"
    ]
    
    for url in endpoints:
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                # API ပုံစံအမျိုးမျိုးအရ data သို့မဟုတ် entities ထဲမှာ ရှာမယ်
                users = data.get('data') or data.get('entities') or []
                if users: return users
        except:
            continue
    return []

@dp.message_handler(commands=['list'])
async def list_users(message: types.Message):
    await message.answer("🔍 နည်းလမ်းအမျိုးမျိုးနဲ့ ရှာဖွေနေပါတယ် ကိုကို...")
    
    users = fetch_litmatch_users()
    
    if not users:
        await message.answer("⚠️ နည်းလမ်းအားလုံး စမ်းကြည့်ပေမယ့် မတွေ့ပါဘူး ကိုကို။ Token သို့မဟုတ် ID မှားနေတာ ဖြစ်နိုင်ပါတယ်ဗျ။")
        return

    text = "📋 **စကားပြောဖူးသူများ စာရင်း**\n"
    for i, u in enumerate(users[:20], 1): # အယောက် ၂၀ ထိပဲ အရင်ပြမယ်
        name = u if isinstance(u, str) else u.get('nickname') or u.get('from')
        text += f"{i}။ {name}\n"
    
    await message.answer(text, parse_mode="Markdown")

if __name__ == '__main__':
    Thread(target=run_flask).start()
    executor.start_polling(dp, skip_updates=True)
