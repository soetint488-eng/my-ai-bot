import os
import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# --- CONFIG ---
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
GROQ_API_KEY = "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"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- RENDER PORT ALIVE ---
async def handle(request):
    return web.Response(text="Bot is running smoothly!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server started on port {port}")

# --- AI RESPONSE FUNCTION ---
async def get_groq_response(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Answer in Myanmar language."},
            {"role": "user", "content": user_text}
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers, timeout=20) as resp:
            data = await resp.json()
            if resp.status != 200:
                return f"❌ API Error: {data['error']['message']}"
            return data['choices'][0]['message']['content']

# --- HANDLERS ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🤖 **ʟʟᴀᴍᴀ 3.3 ᴀɪ** ✨\nအားလုံးအဆင်သင့်ဖြစ်ပါပြီ! မေးခွန်းတွေ မေးနိုင်ပါပြီဗျ။")

@dp.message(F.text)
async def ai_chat(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        reply = await get_groq_response(message.text)
        await message.reply(reply)
    except Exception as e:
        logging.error(f"Chat Error: {e}")
        await message.reply("❌ ခဏနေမှ ပြန်မေးပေးပါဗျ။")

async def main():
    # Web server နဲ့ Polling ကို ယှဉ် run ပါမယ်
    server_task = asyncio.create_task(start_web_server())
    poll_task = asyncio.create_task(dp.start_polling(bot))
    await asyncio.gather(server_task, poll_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot Stopped")
