import os
import asyncio
import logging
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiohttp import web

# --- CONFIG ---
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
GEMINI_KEY = "AIzaSyBCxCKjKQhxg0rpXO5471LvS54XCI1QGdw"

# Gemini Setup
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- RENDER PORT ---
async def handle(request): return web.Response(text="Gemini AI is Live!")
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
    await message.answer(f"🤖 **ɢᴇᴍɪɴɪ ᴀɪ (မြန်မာ)**\n\nမင်္ဂလာပါ {message.from_user.first_name}! ကျွန်တော်က ပိုတော်တဲ့ Gemini AI ဖြစ်ပါတယ်။ သိလိုသမျှကို မြန်မာလို အားမနာတမ်း မေးမြန်းနိုင်ပါတယ်ဗျ။")

@dp.message(Command("getphone"))
async def request_phone(message: types.Message):
    button = KeyboardButton(text="📱 ဖုန်းနံပါတ် ပေးပို့မည်", request_contact=True)
    keyboard = ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True, one_time_keyboard=True)
    await message.answer("သင့်ဖုန်းနံပါတ် သိရှိနိုင်ဖို့ အောက်ကခလုတ်ကို နှိပ်ပေးပါဗျ။", reply_markup=keyboard)

@dp.message(F.contact)
async def get_contact(message: types.Message):
    await message.answer(f"✅ ရရှိပါပြီ!\n📞 ဖုန်း: `{message.contact.phone_number}`", reply_markup=ReplyKeyboardRemove())

@dp.message(F.text)
async def ai_chat(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        # Gemini ကို မြန်မာလို ပိုကောင်းအောင် ခိုင်းထားတာပါ
        prompt = f"Please answer the following question in natural Myanmar language: {message.text}"
        response = await asyncio.to_thread(model.generate_content, prompt)
        await message.reply(response.text)
    except Exception as e:
        await message.reply("❌ ခေတ္တ အခက်အခဲရှိနေပါတယ်ဗျ။")

async def main():
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
