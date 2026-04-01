import os
import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# --- CONFIG ---
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
# Key ကို သေချာပြန်စစ်ပြီး ထည့်ပေးပါ (Space တွေ မပါရပါဘူး)
GROQ_API_KEY = "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"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

async def handle(request): return web.Response(text="Bot is Debugging...")
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()

async def get_groq_response(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Answer in Myanmar language."},
            {"role": "user", "content": user_text}
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            # Error တက်ခဲ့ရင် ဘာကြောင့်လဲဆိုတာ ကြည့်ဖို့
            if resp.status != 200:
                err_text = await resp.text()
                return f"❌ API Error ({resp.status}): {err_text[:100]}"
            
            data = await resp.json()
            return data['choices'][0]['message']['content']

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🤖 **Debug Mode** ✨\nမေးခွန်းတစ်ခုခု မေးကြည့်ပါဗျ။ Error ကို အတိအကျ ပြပေးပါမယ်။")

@dp.message(F.text)
async def ai_chat(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        reply = await get_groq_response(message.text)
        await message.reply(reply)
    except Exception as e:
        await message.reply(f"❌ System Error: {str(e)}")

async def main():
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
