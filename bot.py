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

async def handle(request): return web.Response(text="Llama 3.3 is Online!")
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
        "model": "llama-3.3-70b-specdec", # အသစ်ဆုံးနဲ့ အမြန်ဆုံး Model ပါ
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Answer in Myanmar language. Be very polite."},
            {"role": "user", "content": user_text}
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status != 200:
                err_data = await resp.json()
                return f"❌ API Error: {err_data['error']['message']}"
            
            data = await resp.json()
            return data['choices'][0]['message']['content']

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🤖 **ʟʟᴀᴍᴀ 3.3 ᴀɪ** ✨\nမင်္ဂလာပါ! အခု Model အသစ်နဲ့ အဆင်သင့်ဖြစ်ပါပြီဗျ။ သိလိုသမျှ မေးမြန်းနိုင်ပါပြီ။")

@dp.message(F.text)
async def ai_chat(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        reply = await get_groq_response(message.text)
        await message.reply(reply)
    except Exception as e:
        await message.reply("❌ တစ်ခုခု မှားယွင်းနေပါတယ်ဗျ။")

async def main():
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
