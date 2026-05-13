import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# --- Config ---
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
LIT_TOKEN = "YWMtzPWP7E6iEfG34Kkt_SyshgC3x2A3exHpkKgjudNTjb0mnqlAcGcR8ItMGWYExFEOAwMAAAGeIGB_fjht7EDhriKvyK2dW2gm-zGLW7s4WZomlUCWd9pPsEcRmZprNw"
ORG_APP = "1102190223222824/lit"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def debug_account_info(chat_id):
    headers = {
        "Authorization": f"Bearer {LIT_TOKEN}",
        "User-Agent": "Easemob-SDK(Android) 4.5.3",
        "Accept": "application/json"
    }
    
    # စစ်ဆေးမည့် URL များ
    urls = [
        f"http://a1-sgp-ga.easemob.com/{ORG_APP}/users/me",
        "https://api.litatom.com/api/v1/users/profile/me"
    ]
    
    debug_text = "🔧 **System Debugging...**\n\n"
    
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            debug_text += f"🌐 **URL:** `{url.split('/')[-1]}`\n"
            debug_text += f"📊 **Status:** `{r.status_code}`\n"
            
            if r.status_code == 200:
                data = r.json()
                # ဒေတာရရင် အနှစ်ချုပ်ပြမယ်
                debug_text += "✅ Data Received!\n\n"
            else:
                # Error ပြရင် ဘာကြောင့်လဲဆိုတာ ပြမယ်
                debug_text += f"❌ Message: `{r.text[:100]}`\n\n"
        except Exception as e:
            debug_text += f"⚠️ Connection Error: `{str(e)[:50]}`\n\n"

    await bot.send_message(chat_id, debug_text, parse_mode="Markdown")

@dp.message_handler(commands=['start'])
async def cmd_start(m: types.Message):
    await debug_account_info(m.chat.id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
