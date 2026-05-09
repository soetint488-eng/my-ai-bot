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
def home(): return "200 OK - Dominic Studio is Active!"

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

def get_main_keyboard(f_id):
    kb = InlineKeyboardMarkup(row_width=2)
    # file_id ကို callback ထဲ တန်းထည့်လိုက်တာက Error ကို အပြီးတိုင် ရှင်းပေးပါတယ်
    kb.add(
        InlineKeyboardButton("🖼 Background", callback_data=f"m_bg|{f_id}"),
        InlineKeyboardButton("🎭 FX Filters", callback_data=f"m_fx|{f_id}"),
        InlineKeyboardButton("⚙️ Adjust", callback_data=f"m_ad|{f_id}"),
        InlineKeyboardButton("💎 PNG", callback_data=f"bg_transparent|{f_id}")
    )
    kb.row(InlineKeyboardButton("❌ Close", callback_data="cancel"))
    return kb

# --- 4. Handlers ---

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    await m.reply("👋 **Dominic Pro Studio AI** မှ ကြိုဆိုပါတယ် ကိုကို!\n\nဓာတ်ပုံတစ်ပုံ ပို့ပေးလိုက်ပါဗျ။")

@dp.message_handler(content_types=['photo'])
async def photo_in(m: types.Message):
    f_id = m.photo[-1].file_id # ပုံရဲ့ ID ကို ယူထားမယ်
    await m.reply(
        "📸 **Image Received!**\nပြုပြင်လိုသည့် Tool ကို ရွေးချယ်ပါ ကိုကို-",
        reply_markup=get_main_keyboard(f_id),
        parse_mode="Markdown"
    )

@dp.callback_query_handler(lambda c: True)
async def callbacks(cb: types.CallbackQuery):
    data_parts = cb.data.split("|")
    cmd = data_parts[0]
    f_id = data_parts[1] if len(data_parts) > 1 else None
    
    cid = cb.message.chat.id
    mid = cb.message.message_id

    # UI Navigations
    if cmd == "m_bg":
        kb = InlineKeyboardMarkup(row_width=3)
        colors = ["Blue", "White", "Red", "Green", "Yellow", "Pink"]
        for c in colors: kb.insert(InlineKeyboardButton(c, callback_data=f"bg_{c.lower()}|{f_id}"))
        kb.add(InlineKeyboardButton("🔙 Back", callback_data=f"back|{f_id}"))
        await bot.edit_message_text("🖼 **Choose Background Color**", cid, mid, reply_markup=kb, parse_mode="Markdown")
        return

    elif cmd == "m_fx":
        kb = InlineKeyboardMarkup(row_width=3)
        fxs = {"Vintage": "vintage", "Gray": "grayscale", "Sepia": "sepia", "Techni": "technicolor", "Invert": "invert"}
        for k, v in fxs.items(): kb.insert(InlineKeyboardButton(k, callback_data=f"px_{v}|{f_id}"))
        kb.add(InlineKeyboardButton("🔙 Back", callback_data=f"back|{f_id}"))
        await bot.edit_message_text("🎨 **Special FX Filters**", cid, mid, reply_markup=kb, parse_mode="Markdown")
        return

    elif cmd == "back":
        await bot.edit_message_text("✨ **Main Menu**", cid, mid, reply_markup=get_main_keyboard(f_id))
        return

    elif cmd == "cancel":
        await bot.delete_message(cid, mid)
        return

    # --- API Processing ---
    if f_id:
        await bot.edit_message_text("⚙️ **Dominic AI is working...**", cid, mid, parse_mode="Markdown")
        try:
            file = await bot.get_file(f_id)
            p_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}"
            
            # Pixo (FX Filters)
            if cmd.startswith("px_"):
                action = cmd.split("_")[1]
                res = requests.get("https://api.pixoeditor.com/v1/transform", 
                                   params={'apikey': PIXO_API_KEY, 'image': p_url, 'filter': action})
                cap = f"🎨 FX: {action.capitalize()}"

            # Background (Remove.bg)
            elif cmd.startswith("bg_"):
                color = cmd.split("_")[1]
                rb_params = {'image_url': p_url, 'size': 'auto'}
                if color != "transparent": rb_params['bg_color'] = color
                res = requests.post('https://api.remove.bg/v1.0/removebg', 
                                    data=rb_params, headers={'X-API-Key': REMOVE_BG_API_KEY})
                cap = f"🖼 BG: {color.capitalize()}"

            if res.status_code == 200:
                out = io.BytesIO(res.content)
                out.name = "dominic_studio.png"
                await bot.send_document(cid, document=out, caption=f"✅ {cap}\n_Dominic Pro Studio_", parse_mode="Markdown")
                await bot.delete_message(cid, mid)
            else:
                await bot.send_message(cid, "❌ API Credit ကုန်နေပါပြီ ကိုကို။")
        except Exception as e:
            logging.error(e)
            await bot.send_message(cid, "❌ Error ဖြစ်သွားပါတယ်။ ပုံကို အသစ်ပြန်ပို့ပေးပါ။")

    await bot.answer_callback_query(cb.id)

if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
