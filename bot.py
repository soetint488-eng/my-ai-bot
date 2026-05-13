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
def home(): return "Party Monitor Active!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Monitoring & Collecting Logic ---
async def collect_process(chat_id):
    global is_collecting
    session_total = 0
    await bot.send_message(chat_id, "🚀 Party Room တွေကို စတင်စောင့်ကြည့်နေပါပြီ ကိုကို!")
    
    while is_collecting:
        try:
            # Hot Rooms စာရင်းယူမယ်
            r = requests.get(f"{BASE_URL}/rooms?limit=10&sort=hot", headers={"Authorization": f"Bearer {LIT_TOKEN}"})
            rooms = r.json().get('entities', [])
            
            for room in rooms:
                if not is_collecting: break
                
                room_id = room.get('id')
                room_name = room.get('name', 'အမည်မရှိအခန်း')
                user_count = room.get('user_count', 0)
                
                # အခန်းထဲဝင်တိုင်း Info ကို အရင်ပြမယ်
                info_msg = (
                    f"📺 **Party Monitoring**\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"🏠 အခန်း: {room_name}\n"
                    f"🆔 ID: `{room_id}`\n"
                    f"👥 လူဦးရေ: {user_count} ယောက်"
                )
                status_sent = await bot.send_message(chat_id, info_msg, parse_mode="Markdown")
                
                # စိန်အိတ် (Lucky Bag) ရှိမရှိ စစ်မယ်
                bag_res = requests.get(f"{BASE_URL}/rooms/{room_id}/luckybags", headers={"Authorization": f"Bearer {LIT_TOKEN}"})
                bags = bag_res.json().get('entities', [])
                
                for bag in bags:
                    bag_id = bag.get('id')
                    # စိန်လှမ်းကောက်မယ်
                    grab_res = requests.post(f"{BASE_URL}/rooms/{room_id}/luckybags/{bag_id}/grab", headers={"Authorization": f"Bearer {LIT_TOKEN}"})
                    
                    if grab_res.status_code == 200:
                        amt = grab_res.json().get('amount', 0)
                        if amt > 0:
                            session_total += amt
                            await bot.send_message(chat_id, f"🎊 **စိန်ရပါပြီ ကိုကို!**\n➕ ရရှိစိန်: +{amt}\n💰 စုစုပေါင်း: {session_total}")

                # စာမျက်နှာ မရှုပ်အောင် ၅ စက္ကန့်နေရင် လက်ရှိ Room Info စာကို ပြန်ဖျက်ပေးမယ်
                await asyncio.sleep(5)
                try:
                    await bot.delete_message(chat_id, status_sent.message_id)
                except: pass
                
        except: pass
        await asyncio.sleep(2)

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
    await message.answer("🛑 စောင့်ကြည့်တာကို ရပ်လိုက်ပါပြီ။")

if __name__ == '__main__':
    Thread(target=run_flask).start()
    executor.start_polling(dp, skip_updates=True)
