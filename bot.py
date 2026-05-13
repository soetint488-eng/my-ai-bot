import os
import asyncio
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
is_collecting = False

@app.route('/')
def home(): return "Collector Active!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Enhanced Diamond Collector Logic ---
async def collect_process(chat_id):
    global is_collecting
    session_total = 0
    await bot.send_message(chat_id, "🚀 Diamond Collector စတင်ပါပြီ ကိုကို!")
    
    while is_collecting:
        try:
            # Hot Rooms ယူခြင်း (အချက်အလက် ပိုစုံအောင် limit တိုးထားပါတယ်)
            r = requests.get(f"{BASE_URL}/rooms?limit=15&sort=hot", headers={"Authorization": f"Bearer {LIT_TOKEN}"})
            rooms = r.json().get('entities', [])
            
            for room in rooms:
                if not is_collecting: break
                
                room_id = room.get('id')
                room_name = room.get('name', 'အမည်မရှိအခန်း')
                user_count = room.get('user_count', 0) # အခန်းထဲရှိ လူဦးရေ
                
                # စိန်အိတ် လှမ်းကောက်ခြင်း
                res = requests.post(f"{BASE_URL}/rooms/{room_id}/diamonds/grab", headers={"Authorization": f"Bearer {LIT_TOKEN}"}, timeout=5)
                
                if res.status_code == 200:
                    amt = res.json().get('amount', 0)
                    if amt > 0:
                        session_total += amt
                        await bot.send_message(
                            chat_id, 
                            f"💎 **စိန်ရရှိပါပြီ!**\n"
                            f"━━━━━━━━━━━━━━\n"
                            f"🏠 အခန်းအမည်: {room_name}\n"
                            f"🆔 Room ID: `{room_id}`\n"
                            f"👥 လူဦးရေ: {user_count} ယောက်\n"
                            f"➕ ရရှိစိန်: +{amt}\n"
                            f"💰 စုစုပေါင်း: {session_total}", 
                            parse_mode="Markdown"
                        )
                # API သက်သာအောင် ခဏနားမယ်
                await asyncio.sleep(1) 
        except:
            pass
        await asyncio.sleep(5)

# --- Commands ---
@dp.message_handler(commands=['collect'])
async def start_collect(message: types.Message):
    global is_collecting
    if not is_collecting:
        is_collecting = True
        asyncio.create_task(collect_process(message.chat.id))
    else:
        await message.answer("⚠️ Bot က အလုပ်လုပ်နေတုန်းပါ ကိုကို။")

@dp.message_handler(commands=['stop'])
async def stop_collect(message: types.Message):
    global is_collecting
    is_collecting = False
    await message.answer("🛑 Diamond Collector ကို ရပ်လိုက်ပါပြီ။")

if __name__ == '__main__':
    Thread(target=run_flask).start()
    executor.start_polling(dp, skip_updates=True)
