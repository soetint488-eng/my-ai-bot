import os
import asyncio
import logging
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# --- CONFIG ---
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
GEMINI_API_KEY = "AIzaSyBCxCKjKQhxg0rpXO5471LvS54XCI1QGdw"

# Gemini AI Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') # ပိုမြန်တဲ့ Flash model ကို သုံးထားပါတယ်

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- RENDER PORT KEEP-ALIVE ---
async def handle(request): 
    return web.Response(text="Gemini AI Bot is Running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome = (
        f"🤖 **ɢᴇᴍɪɴɪ ᴀɪ ᴀssɪsᴛᴀɴᴛ**\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"မင်္ဂလာပါ **{message.from_user.first_name}**! 👋\n\n"
        f"ကျွန်တော်က Gemini AI ဖြစ်ပါတယ်။ သိလိုသမျှ မေးခွန်းတွေကို "
        f"စာရိုက်ပြီး မေးမြန်းနိုင်ပါတယ်ဗျ။"
    )
    await message.answer(welcome, parse_mode="Markdown")

@dp.message(F.text)
async def ai_chat(message: types.Message):
    # User စာရိုက်လိုက်ရင် Bot က 'typing...' ပြပေးမယ်
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Gemini AI ဆီက အဖြေတောင်းခြင်း
        response = model.generate_content(message.text)
        
        # အဖြေကို ပြန်ပို့ခြင်း
        if response.text:
            await message.reply(response.text, parse_mode="Markdown")
        else:
            await message.reply("⚠️ စိတ်မရှိပါနဲ့ဗျ၊ ဒီမေးခွန်းကို ကျွန်တော် မဖြေနိုင်သေးပါဘူး။")
            
    except Exception as e:
        logging.error(f"Gemini Error: {e}")
        await message.reply("❌ AI Server နဲ့ ချိတ်ဆက်ရာမှာ အခက်အခဲရှိနေပါတယ်ဗျ။ ခဏနေမှ ပြန်စမ်းကြည့်ပေးပါ။")

async def main():
    # Web server နဲ့ Bot ကို တစ်ပြိုင်တည်း run မယ်
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
