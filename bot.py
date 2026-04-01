import os
import asyncio
import logging
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiohttp import web
from io import BytesIO
from PIL import Image

# --- CONFIG ---
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
GEMINI_KEY = "AIzaSyBCxCKjKQhxg0rpXO5471LvS54XCI1QGdw"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') # Vision support ပါပြီးသားပါ

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- RENDER PORT ---
async def handle(request): return web.Response(text="Vision AI is Active!")
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
    await message.answer("🤖 **ᴍᴜʟᴛɪ-ᴍᴏᴅᴀʟ ᴀɪ ʙᴏᴛ** ✨\n\nကျွန်တော့်ဆီကို စာတွေအပြင် **ဓာတ်ပုံတွေ** ပါ ပို့ပြီး မေးမြန်းနိုင်ပါပြီဗျ!")

# 📸 ဓာတ်ပုံ လက်ခံတဲ့နေရာ
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        # ဓာတ်ပုံကို Download ဆွဲခြင်း
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        photo_bytes = await bot.download_file(file_info.file_path)
        
        img = Image.open(photo_bytes)
        
        # Gemini ကို ပုံနဲ့တူတူ ပို့ခြင်း
        response = await asyncio.to_thread(
            model.generate_content, 
            ["ဒီပုံထဲမှာ ဘာတွေတွေ့ရလဲဆိုတာ မြန်မာလို အသေးစိတ် ရှင်းပြပေးပါ။", img]
        )
        await message.reply(response.text)
    except Exception as e:
        await message.reply(f"❌ ပုံကို ဖတ်လို့မရပါဘူးဗျ။")

# 💬 စာသား လက်ခံတဲ့နေရာ
@dp.message(F.text)
async def ai_chat(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        response = await asyncio.to_thread(
            model.generate_content, 
            f"Answer in natural Myanmar language: {message.text}"
        )
        await message.reply(response.text)
    except Exception as e:
        await message.reply("❌ တစ်ခုခု မှားယွင်းနေပါတယ်ဗျ။")

async def main():
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
