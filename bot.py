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
def home(): return "200 OK - Power Bot is Active!"

def run_web(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run_web).start()

# --- 2. API Setup ---
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
REMOVE_BG_API_KEY = 'NJqyHZ2Du9oAhnNiiTazFPpo'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- 3. Premium UI Keyboards ---

def get_main_menu(f_id):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✂️ Remove BG", callback_data=f"opt_trans|{f_id}"),
        InlineKeyboardButton("🎨 Solid Colors", callback_data=f"nav_colors|{f_id}"),
        InlineKeyboardButton("🖼 BG Patterns", callback_data=f"nav_patterns|{f_id}"),
        InlineKeyboardButton("🌑 Add Shadow", callback_data=f"opt_shadow|{f_id}"),
        InlineKeyboardButton("💎 Full HD Mode", callback_data=f"opt_hd|{f_id}"),
        InlineKeyboardButton("❌ Close", callback_data="cancel")
    )
    return kb

def get_color_menu(f_id):
    kb = InlineKeyboardMarkup(row_width=3)
    colors = {"🔵 Blue": "blue", "⚪ White": "white", "🔴 Red": "red", 
              "🟢 Green": "green", "🟡 Yellow": "yellow", "🟣 Pink": "pink"}
    for label, val in colors.items():
        kb.insert(InlineKeyboardButton(label, callback_data=f"clr_{val}|{f_id}"))
    kb.row(InlineKeyboardButton("🔙 Back", callback_data=f"back|{f_id}"))
    return kb

# --- 4. Handlers ---

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    await m.reply("🔥 **Dominic Power BG Remover**\n\nပြုပြင်လိုသည့် ဓာတ်ပုံကို ပို့ပေးလိုက်ပါ ကိုကို!")

@dp.message_handler(content_types=['photo'])
async def photo_in(m: types.Message):
    f_id = m.photo[-1].file_id
    await m.reply("✨ **Image Received!**\nအသုံးပြုလိုသည့် Professional Tool ကို ရွေးပါ-", 
                   reply_markup=get_main_menu(f_id))

@dp.callback_query_handler(lambda c: True)
async def callbacks(cb: types.CallbackQuery):
    d = cb.data.split("|")
    cmd = d[0]
    f_id = d[1] if len(d) > 1 else None
    cid, mid = cb.message.chat.id, cb.message.message_id

    # UI Navigation
    if cmd == "nav_colors":
        await bot.edit_message_text("🌈 **Select Background Color**", cid, mid, reply_markup=get_color_menu(f_id))
        return
    elif cmd == "back":
        await bot.edit_message_text("✨ **Main Menu**", cid, mid, reply_markup=get_main_menu(f_id))
        return
    elif cmd == "cancel":
        await bot.delete_message(cid, mid)
        return

    # Processing Logic
    if f_id:
        await bot.edit_message_text("⚙️ **Dominic AI အလုပ်လုပ်နေပါပြီ...**", cid, mid)
        try:
            file = await bot.get_file(f_id)
            p_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}"
            headers = {'X-API-Key': REMOVE_BG_API_KEY}
            params = {'image_url': p_url, 'size': 'auto'}

            # Feature logic based on command
            if cmd == "opt_trans": cap = "✅ Background Removed"
            elif cmd == "opt_shadow": 
                params['add_shadow'] = 'true'
                cap = "✅ Shadow Added"
            elif cmd == "opt_hd":
                params['size'] = 'full'
                cap = "💎 Full HD Quality"
            elif cmd.startswith("clr_"):
                color = cmd.split("_")[1]
                params['bg_color'] = color
                cap = f"✅ {color.capitalize()} Background"

            res = requests.post('https://api.remove.bg/v1.0/removebg', data=params, headers=headers)
            
            if res.status_code == 200:
                out = io.BytesIO(res.content)
                out.name = "dominic_power_edit.png"
                await bot.send_document(cid, document=out, caption=f"{cap}\n_Dominic AI Studio_")
                await bot.delete_message(cid, mid)
            else:
                await bot.send_message(cid, "❌ API Credit မလုံလောက်ပါ သို့မဟုတ် Key မှားနေပါတယ်။")
        except:
            await bot.send_message(cid, "❌ Error ဖြစ်သွားပါတယ်။ ပုံကို အသစ်ပြန်ပို့ပေးပါ။")

    await bot.answer_callback_query(cb.id)

if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
