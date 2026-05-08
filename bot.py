import os
import io
import logging
from flask import Flask, Response
from threading import Thread
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from PIL import Image, ImageOps, ImageFilter
from rembg import remove

# ၁။ Web Server (Render Port Binding & Cron-job.org Support)
app = Flask('')

@app.route('/')
def home():
    # Cron-job.org အတွက် HTTP 200 OK ပြန်ပေးခြင်း
    return Response("Bot is active and running!", status=200)

def run():
    # Render ရဲ့ Dynamic Port ကို ဖတ်ခိုင်းခြင်း (Error မတက်စေရန် အရေးကြီးဆုံးအချက်)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True # Main thread ပိတ်ရင် တစ်ခါတည်း ပိတ်အောင် လုပ်ခြင်း
    t.start()

# ၂။ Telegram Bot Logic
logging.basicConfig(level=logging.INFO)

# ကိုကို့ Token
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def get_filter_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("⚪ B&W", callback_data="filter_bw"),
        types.InlineKeyboardButton("📜 Sepia", callback_data="filter_sepia"),
        types.InlineKeyboardButton("🌫 Blur", callback_data="filter_blur"),
        types.InlineKeyboardButton("✂️ Remove BG", callback_data="filter_rembg"),
        types.InlineKeyboardButton("🖼 Sticker", callback_data="filter_sticker")
    ]
    keyboard.add(*buttons)
    return keyboard

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("မင်္ဂလာပါ ကိုကို! ပြင်ချင်တဲ့ ဓာတ်ပုံကို ပို့ပေးပါ။")

@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    await message.reply("ဒီပုံကို ဘာလုပ်မလဲ ကိုကို?", reply_markup=get_filter_keyboard())

@dp.callback_query_handler(lambda c: c.data.startswith('filter_'))
async def process_filter(callback_query: types.CallbackQuery):
    action = callback_query.data.split('_')[1]
    
    try:
        # Original Photo ကို ပြန်ယူခြင်း
        photo = callback_query.message.reply_to_message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        photo_bytes = await bot.download_file(file_info.file_path)
        
        img = Image.open(photo_bytes)
        output_io = io.BytesIO()

        if action == "bw":
            img = ImageOps.grayscale(img)
        elif action == "sepia":
            # Better Sepia implementation
            img = ImageOps.colorize(ImageOps.grayscale(img), "#704214", "#C0A080")
        elif action == "blur":
            img = img.filter(ImageFilter.GaussianBlur(5))
        elif action == "rembg":
            img = remove(img)
        elif action == "sticker":
            img.thumbnail((512, 512))
            img.save(output_io, format="WEBP")
            output_io.seek(0)
            await bot.send_sticker(callback_query.from_user.id, output_io)
            return

        img.save(output_io, format="PNG")
        output_io.seek(0)
        await bot.send_photo(callback_query.from_user.id, output_io, caption=f"Done! ({action})")
        
    except Exception as e:
        await bot.send_message(callback_query.from_user.id, f"Error: {str(e)}")

if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
