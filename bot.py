import os
import asyncio
import logging
import sys

# Error တက်ရင် ဘာကြောင့်လဲဆိုတာ အသေးစိတ်ပြဖို့
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

try:
    import google.generativeai as genai
    from aiogram import Bot, Dispatcher, types, F
    from aiogram.filters import Command
    from aiohttp import web
    from PIL import Image
    logging.info("Libraries imported successfully!")
except ImportError as e:
    logging.error(f"Import Error: {e}")
    sys.exit(1)

# --- CONFIG ---
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
GEMINI_KEY = "AIzaSyBCxCKjKQhxg0rpXO5471LvS54XCI1QGdw"

try:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
except Exception as e:
    logging.error(f"Setup Error: {e}")
    sys.exit(1)

async def handle(request): return web.Response(text="Bot is Debugging...")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🤖 Vision AI is online!")

async def main():
    try:
        logging.info("Starting Web Server and Polling...")
        await asyncio.gather(start_web_server(), dp.start_polling(bot))
    except Exception as e:
        logging.error(f"Runtime Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
