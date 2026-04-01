import os
import asyncio
import logging
import openai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# --- CONFIG ---
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
OPENAI_API_KEY = "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"

openai.api_key = OPENAI_API_KEY

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

async def handle(request): return web.Response(text="Bot is Online!")
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🤖 **ChatGPT AI Assistant**\nမေးခွန်းများ မေးမြန်းနိုင်ပါပြီဗျ!")

@dp.message(F.text)
async def ai_chat(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        # OpenAI v0.28.1 ရဲ့ ရေးထုံး
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}]
        )
        await message.reply(response.choices[0].message.content)
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)[:100]}")

async def main():
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
