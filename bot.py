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

client = Groq(api_key=GROQ_API_KEY)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- RENDER WEB SERVER ---
async def handle(request): 
    return web.Response(text="Llama 3 AI is Running on Groq!")

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
    welcome = (
        f"🤖 **ʟʟᴀᴍᴀ 3 ᴀɪ (ɢʀᴏǫ)**\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"မင်္ဂလာပါ **{message.from_user.first_name}**! 👋\n\n"
        f"ကျွန်တော်က Llama 3 AI ဖြစ်ပါတယ်။ သိလိုသမျှကို "
        f"မြန်မာလို မေးမြန်းနိုင်ပါပြီဗျ။"
    )
    await message.answer(welcome, parse_mode="Markdown")

@dp.message(F.text)
async def ai_chat(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        # Groq (Llama 3) ဆီက အဖြေတောင်းခြင်း
        chat_completion = await asyncio.to_thread(
            client.chat.completions.create,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. You must answer in Myanmar language. Be friendly and polite."},
                {"role": "user", "content": message.text}
            ],
            model="llama3-70b-8192", # အတော်ဆုံး model ပါ
        )
        
        reply = chat_completion.choices[0].message.content
        await message.reply(reply)
            
    except Exception as e:
        logging.error(f"Groq Error: {e}")
        await message.reply("❌ AI Server မှာ ခေတ္တ အခက်အခဲရှိနေပါတယ်ဗျ။")

async def main():
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
