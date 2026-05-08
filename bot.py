import os
import io
import logging
import asyncio
import requests
from flask import Flask, Response
from threading import Thread
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from PIL import Image, ImageOps, ImageFilter
from rembg import remove
import replicate

# ၁။ Web Server ပိုင်း (Render Port Binding)
app = Flask('')

@app.route('/')
def home():
    return Response("Bot is active and running!", status=200)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ၂။ Telegram Bot ပိုင်း
logging.basicConfig(level=logging.INFO)
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# State Management for Cropping
class CropState(StatesGroup):
    waiting_for_area = State()

def get_filter_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("⚪ B&W", callback_data="filter_bw"),
        types.InlineKeyboardButton("📜 Sepia", callback_data="filter_sepia"),
        types.InlineKeyboardButton("🌫 Blur", callback_data="filter_blur"),
        types.InlineKeyboardButton("✂️ Remove BG", callback_data="filter_rembg"),
        types.InlineKeyboardButton("✨ AI Enhance (ပုံကြည်)", callback_data="filter_enhance"),
        types.InlineKeyboardButton("📐 Crop (ပုံဖြတ်)", callback_data="filter_crop"),
        types.InlineKeyboardButton("🖼 Sticker", callback_data="filter_sticker")
    ]
    keyboard.add(*buttons)
    return keyboard

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("မင်္ဂလာပါ ကိုကို! ပြင်ချင်တဲ့ ဓာတ်ပုံကို ပို့ပေးပါ။ ✨")

@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    await message.reply("ဒီပုံကို ဘာလုပ်မလဲ ကိုကို?", reply_markup=get_filter_keyboard())

# --- AI Enhancement Function ---
async def ai_enhance_photo(photo_url):
    replicate_token = os.getenv('REPLICATE_API_TOKEN')
    if not replicate_token:
        return None, "Error: Replicate Token မရှိသေးပါ။ Render မှာ ထည့်ပေးပါ။"
    
    client = replicate.Client(api_token=replicate_token)
    try:
        # GFPGAN Model သုံးပြီး ပုံကြည်အောင်လုပ်ခြင်း
        output = client.run(
            "tencentarc/gfpgan:9283608cc6b7be6b65a8e44983db01e11100227496c4c9c40213b1026456f081",
            input={"img": photo_url, "scale": 2}
        )
        return output, None
    except Exception as e:
        return None, str(e)

# --- Callback Queries ---
@dp.callback_query_handler(lambda c: c.data.startswith('filter_'))
async def process_filter(callback_query: types.CallbackQuery, state: FSMContext):
    action = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    
    try:
        photo_id = callback_query.message.reply_to_message.photo[-1].file_id
        file_info = await bot.get_file(photo_id)
        photo_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}"
        photo_bytes = await bot.download_file(file_info.file_path)
        img = Image.open(photo_bytes)
    except:
        await bot.answer_callback_query(callback_query.id, "Error: ပုံရှာမတွေ့ပါ။")
        return

    await bot.answer_callback_query(callback_query.id, "ခဏစောင့်ပါ ကိုကို...")
    output_io = io.BytesIO()

    if action == "bw":
        img = ImageOps.grayscale(img)
    elif action == "sepia":
        img = ImageOps.colorize(ImageOps.grayscale(img), "#704214", "#C0A080")
    elif action == "blur":
        img = img.filter(ImageFilter.GaussianBlur(5))
    elif action == "rembg":
        img = remove(img)
    elif action == "enhance":
        enhanced_url, err = await ai_enhance_photo(photo_url)
        if err:
            await bot.send_message(user_id, f"AI Error: {err}")
            return
        img = Image.open(io.BytesIO(requests.get(enhanced_url).content))
    elif action == "crop":
        await state.update_data(photo_id=photo_id)
        await bot.send_message(user_id, "ဖြတ်မည့် % ကို ပို့ပေးပါ (ဥပမာ: 10 10 90 90)")
        await CropState.waiting_for_area.set()
        return
    elif action == "sticker":
        img.thumbnail((512, 512))
        img.save(output_io, format="WEBP")
        output_io.seek(0)
        await bot.send_sticker(user_id, output_io)
        return

    img.save(output_io, format="PNG")
    output_io.seek(0)
    await bot.send_photo(user_id, output_io, caption=f"Done! ({action})")

# --- Crop Message Handler ---
@dp.message_handler(state=CropState.waiting_for_area)
async def do_crop(message: types.Message, state: FSMContext):
    try:
        l, t, r, b = [float(x) for x in message.text.split()]
        data = await state.get_data()
        file_info = await bot.get_file(data['photo_id'])
        img = Image.open(await bot.download_file(file_info.file_path))
        
        w, h = img.size
        img = img.crop(((l/100)*w, (t/100)*h, (r/100)*w, (b/100)*h))
        
        out = io.BytesIO()
        img.save(out, format="PNG")
        out.seek(0)
        await bot.send_photo(message.from_user.id, out, caption="Cropped Done!")
    except:
        await message.reply("မှားယွင်းနေပါသည်။ ဥပမာ- 10 10 90 90")
    await state.finish()

# ၃။ Main Runner
async def main():
    Thread(target=run_flask, daemon=True).start()
    try:
        await dp.start_polling()
    finally:
        await bot.close()

if __name__ == '__main__':
    asyncio.run(main())
