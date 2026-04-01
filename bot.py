import os
import asyncio
import logging
from groq import Groq
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# --- CONFIG ---
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
GROQ_API_KEY = "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"

# Groq Setup
client = Groq(api_key=GROQ_API_KEY)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- RENDER WEB SERVER ---
async def handle(request): 
    return web.Response(text="Llama 3 AI is Running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- AI CHAT FUNCTION ---
def get_ai_response(user_text):
    # Groq Synchronous ခေါ်ဆိုမှု
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer in Myanmar language."},
            {"role": "user", "content": user_text}
        ],
        model="llama3-70b-8192",
    )
    return chat_completion.choices[0].message.content

# --- HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🤖 **ʟʟᴀᴍᴀ 3 ᴀɪ** ✨\nမေးခွန်းများ စတင်မေးမြန်းနိုင်ပါပြီဗျ!")

@dp.message(F.text)
async def ai_chat(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        # AI ဆီက အဖြေကို Thread ထဲမှာ တောင်းခြင်း (Crash မဖြစ်အောင်)
        loop = asyncio.get_event_loop()
        reply = await loop.run_in_executor(None, get_ai_response, message.text)
        await message.reply(reply)
            
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.reply("❌ ခဏနေမှ ပြန်မေးပေးပါဗျ။")

async def main():
    # Web Server နဲ့ Bot ကို တပြိုင်တည်း run ပါမယ်
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
