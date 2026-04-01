import os
import asyncio
import logging
import base64  # <--- ဒါလေး ကျန်ခဲ့လို့ Error တက်တာပါ
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

# --- RENDER PORT ALIVE ---
async def handle(request):
    return web.Response(text="Vision AI is Running Smoothly!")

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
    await message.answer("🤖 **ʟʟᴀᴍᴀ 3.3 ᴠɪsɪᴏɴ** ✨\n\nစာတွေရော၊ ဓာတ်ပုံတွေရော ပို့ပြီး မေးမြန်းနိုင်ပါပြီဗျ!")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        photo_bytes = await bot.download_file(file_info.file_path)
        
        # ဓာတ်ပုံကို AI ဖတ်နိုင်အောင် ပြောင်းလဲခြင်း
        base64_image = base64.b64encode(photo_bytes.getvalue()).decode('utf-8')
        
        chat_completion = await asyncio.to_thread(
            client.chat.completions.create,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "ဒီပုံထဲမှာ ဘာတွေတွေ့ရလဲ မြန်မာလို ရှင်းပြပေးပါ။"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ],
                }
            ],
            model="llama-3.2-11b-vision-preview",
        )
        await message.reply(chat_completion.choices[0].message.content)
    except Exception as e:
        logging.error(f"Vision Error: {e}")
        await message.reply("❌ ပုံကို ဖတ်လို့မရပါဘူးဗျ။")

@dp.message(F.text)
async def ai_chat(message: types.Message):
    if message.text.startswith('/'): return
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        chat_completion = await asyncio.to_thread(
            client.chat.completions.create,
            messages=[
                {"role": "system", "content": "You are a helpful Myanmar assistant. Answer in natural Myanmar language."},
                {"role": "user", "content": message.text}
            ],
            model="llama-3.3-70b-versatile",
        )
        await message.reply(chat_completion.choices[0].message.content)
    except Exception as e:
        logging.error(f"Chat Error: {e}")
        await message.reply("❌ ခဏနေမှ ပြန်မေးပေးပါဗျ။")

async def main():
    # Web server နဲ့ Polling ကို အတူတူ Run ပါမယ်
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
