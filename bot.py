import logging
import requests
import io
from threading import Thread
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- 1. Web Server for Cron-job ---
app = Flask('')
@app.route('/')
def home(): return "200 OK - Bot is Active!"

def run_web(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run_web).start()

# --- 2. API Setup ---
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
REMOVE_BG_API_KEY = 'NJqyHZ2Du9oAhnNiiTazFPpo'
PIXO_API_KEY = '3kgr1xywr5y0'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- 3. UI Keyboards ---
def get_main_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✂️ BG Remover", callback_data="menu_bg"),
        InlineKeyboardButton("🎨 Pixo Filters", callback_data="menu_pixo"),
        InlineKeyboardButton("☀️ Adjustments", callback_data="menu_adj"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    )
    return kb

def get_pixo_filters():
    kb = InlineKeyboardMarkup(row_width=3)
    filters = ["Sepia", "Grayscale", "Invert", "Vintage", "Kodachrome", "Technicolor"]
    for f in filters:
        kb.insert(InlineKeyboardButton(f, callback_data=f"pixo_{f.lower()}"))
    kb.add(InlineKeyboardButton("🔙 Back", callback_data="back_to_main"))
    return kb

def get_adj_options():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔆 Brighten", callback_data="adj_bright"),
        InlineKeyboardButton("🌈 High Sat", callback_data="adj_sat"),
        InlineKeyboardButton("🎭 Auto Enhance", callback_data="adj_auto"),
        InlineKeyboardButton("🔙 Back", callback_data="back_to_main")
    )
    return kb

def get_bg_colors():
    kb = InlineKeyboardMarkup(row_width=3)
    colors = ["Blue", "White", "Red", "Green", "Yellow", "Transparent"]
    for c in colors:
        kb.insert(InlineKeyboardButton(c, callback_data=f"bg_{c.lower()}"))
    kb.add(InlineKeyboardButton("🔙 Back", callback_data="back_to_main"))
    return kb

# --- 4. Logic Functions ---

async def call_pixo_api(photo_url, action):
    # Pixo Image Processing API URL
    base_url = "https://api.pixoeditor.com/v1/transform"
    params = {
        'apikey': PIXO_API_KEY,
        'image': photo_url,
    }
    
    # Action အလိုက် Parameter ပြောင်းလဲခြင်း
    if action == "sepia": params['filter'] = 'sepia'
    elif action == "grayscale": params['filter'] = 'grayscale'
    elif action == "invert": params['filter'] = 'invert'
    elif action == "bright": params['brightness'] = '30'
    elif action == "sat": params['saturation'] = '50'
    elif action == "auto": params['auto_enhance'] = 'true'
    
    res = requests.get(base_url, params=params)
    return res

# --- 5. Handlers ---

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    await m.reply("📸 **Dominic Pixo Editor AI**\n\nပုံပို့ပြီး Editor စတင်အသုံးပြုပါဗျ။", parse_mode="Markdown")

@dp.message_handler(content_types=['photo'])
async def photo_in(m: types.Message):
    await m.reply("✨ **ဓာတ်ပုံရရှိပါပြီ**\nအောက်ပါ Tools များကို အသုံးပြုနိုင်ပါပြီ-", reply_markup=get_main_keyboard())

@dp.callback_query_handler(lambda c: True)
async def callbacks(cb: types.CallbackQuery):
    d = cb.data
    cid = cb.message.chat.id
    mid = cb.message.message_id

    if d == "menu_bg": await bot.edit_message_text("✂️ **Background Colors**", cid, mid, reply_markup=get_bg_colors())
    elif d == "menu_pixo": await bot.edit_message_text("🎨 **Pixo Special Filters**", cid, mid, reply_markup=get_pixo_filters())
    elif d == "menu_adj": await bot.edit_message_text("☀️ **Image Adjustments**", cid, mid, reply_markup=get_adj_options())
    elif d == "back_to_main": await bot.edit_message_text("✨ Tools များကို ပြန်လည်ရွေးချယ်ပါ-", cid, mid, reply_markup=get_main_keyboard())
    elif d == "cancel": await bot.delete_message(cid, mid)
    
    # API Processing Logic
    else:
        await bot.edit_message_text("🚀 AI Processing... ခဏစောင့်ပါဗျ။", cid, mid)
        try:
            file = await cb.message.reply_to_message.photo[-1].get_file()
            p_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}"
            
            # Pixo Tools
            if d.startswith("pixo_") or d.startswith("adj_"):
                action = d.split("_")[1]
                res = await call_pixo_api(p_url, action)
                caption = f"✅ Pixo {action.capitalize()} Effect အောင်မြင်ပါတယ်!"
            
            # Remove.bg Tools
            elif d.startswith("bg_"):
                color = d.split("_")[1]
                params = {'image_url': p_url, 'size': 'auto'}
                if color != "transparent": params['bg_color'] = color
                res = requests.post('https://api.remove.bg/v1.0/removebg', data=params, headers={'X-API-Key': REMOVE_BG_API_KEY})
                caption = f"✅ {color.capitalize()} Background ပြောင်းလဲပြီးပါပြီ!"

            if res.status_code == 200:
                out = io.BytesIO(res.content)
                out.name = "dominic_edit.png"
                await bot.send_document(cid, document=out, caption=caption)
                await bot.delete_message(cid, mid)
            else:
                await bot.send_message(cid, "❌ API Error ဖြစ်သွားပါတယ်။ Key သို့မဟုတ် Credit စစ်ဆေးပေးပါ။")
        except:
            await bot.send_message(cid, "❌ ပုံကို ပြန်လည်ပို့ပေးပါဗျ။")

    await bot.answer_callback_query(cb.id)

if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
