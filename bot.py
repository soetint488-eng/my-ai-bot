import os
import json
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from flask import Flask
from threading import Thread
import websockets

# --- Configuration ---
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
LIT_TOKEN = "YWMtOs1AxE6JEfGMQK35LXPHlwC3x2A3exHpkKgjudNTjb0ZQwwAzFsR8JWtDRpn0gquAwMAAAGeH7jqmTht7EDd_nns6iTySRbBrvMZueFVp-UzTJHDDF30mKnSJN8Oug"
MSYNC_URL = "wss://msync-im1-sgp-aws-ga.easemob.com:6717"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)

@app.route('/')
def home(): return "Bot Active and Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- MSYNC Socket ကနေ Chat List ဆွဲထုတ်ခြင်း ---
async def get_names_from_socket():
    users = []
    try:
        async with websockets.connect(MSYNC_URL, timeout=10) as ws:
            # Login Packet ပို့ခြင်း
            auth = {"op": 1, "token": LIT_TOKEN, "appId": "1102190223222824#lit"}
            await ws.send(json.dumps(auth))
            
            # စာရင်းကို စက္ကန့်အနည်းငယ် စောင့်ဖတ်မယ်
            for _ in range(5): 
                response = await asyncio.wait_for(ws.recv(), timeout=2)
                data = json.loads(response)
                # Chat ပိုင်ရှင် နာမည်ပါလာရင် သိမ်းမယ်
                if "from" in data:
                    users.append(data.get("from"))
    except:
        pass
    return list(set(users)) # နာမည်မထပ်အောင် လုပ်ခြင်း

@dp.message_handler(commands=['list'])
async def list_users(message: types.Message):
    await message.answer("📡 MSYNC Server ကနေ တိုက်ရိုက် ဆွဲထုတ်နေပါတယ် ကိုကို...")
    
    # Async function ကို ပုံမှန်အတိုင်း ခေါ်ယူခြင်း
    loop = asyncio.get_event_loop()
    users = await get_names_from_socket()
    
    if not users:
        await message.answer("⚠️ Socket ကနေလည်း မတွေ့သေးဘူး ကိုကို။ Token က Chat List ကြည့်ဖို့ ခွင့်မပြုတာ ဖြစ်နိုင်ပါတယ်ဗျ။")
        return

    text = "📋 **စကားပြောဖူးသူများ (Socket စနစ်)**\n"
    for i, name in enumerate(users, 1):
        text += f"{i}။ {name}\n"
    
    await message.answer(text, parse_mode="Markdown")

if __name__ == '__main__':
    Thread(target=run_flask).start()
    executor.start_polling(dp, skip_updates=True)
