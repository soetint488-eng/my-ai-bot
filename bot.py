import os
import asyncio
import logging
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# --- CONFIG ---
# သင့်ရဲ့ Telegram Bot Token
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
# သင့်ရဲ့ Gemini API Key (OpenAI မဟုတ်ပါ)
GEMINI_API_KEY = "AIzaSyBCxCKjKQhxg0rpXO5471LvS54XCI1QGdw"

# Gemini AI Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- RENDER WEB SERVER ---
async def handle(request): 
    return web.Response(text="Gemini Bot is Live!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()

# --- HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🤖 **ɢᴇᴍɪɴɪ ᴀɪ ᴀssɪsᴛᴀɴᴛ**\nမင်္ဂလာပါဗျ! ကျွန်တော်က Gemini AI ဖြစ်ပါတယ်။ သိလိုသမျှ မေးမြန်းနိုင်ပါပြီ။")

@dp.message(F.text)
async def ai_chat(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        # AI ဆီက အဖြေတောင်းခြင်း
        response = await asyncio.to_thread(model.generate_content, message.text)
        
        if response.text:
            await message.reply(response.text)
        else:
            await message.reply("⚠️ အဖြေမထုတ်ပေးနိုင်ပါဘူးဗျ။")
            
    except Exception as e:
        logging.error(f"Gemini Error: {e}")
        await message.reply("❌ AI Server မှာ အခက်အခဲရှိနေပါတယ်ဗျ။")

async def main():
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
