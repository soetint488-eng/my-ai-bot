import os
import asyncio
import logging
import base64
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

# --- RENDER PORT ---
async def handle(request): return web.Response(text="Stable Vision AI is Live!")
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
    await message.answer("🤖 **ʟʟᴀᴍᴀ 3.3 ᴠɪsɪᴏɴ** ✨\n\nစာတွေရော၊ ဓာတ်ပုံတွေရော ပို့ပြီး မေးမြန်းနိုင်ပါပြီဗျ!")

# 📸 ဓာတ်ပုံကြည့်တဲ့နေရာ
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        photo_bytes = await bot.download_file(file_info.file_path)
        
        # ပုံကို Base64 ပြောင်းခြင်း
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
            model="llama-3.2-11b-vision-preview", # Vision Model
        )
        await message.reply(chat_completion.choices[0].message.content)
    except Exception as e:
        logging.error(f"Vision Error: {e}")
        await message.reply("❌ ပုံကို ဖတ်လို့မရပါဘူးဗျ။")

# 💬 စာသားဖြေတဲ့နေရာ
@dp.message(F.text)
async def ai_chat(message: types.Message):
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
        await message.reply("❌ ခေတ္တ အဆင်မပြေဖြစ်နေပါတယ်ဗျ။")

async def main():
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
