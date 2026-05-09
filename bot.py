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

# --- 3. UI Keyboards (Premium Look) ---

def get_main_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🖼 Background Color", callback_data="menu_bg"),
        InlineKeyboardButton("🎭 FX Filters", callback_data="menu_pixo"),
        InlineKeyboardButton("⚙️ Photo Adjust", callback_data="menu_adj"),
        InlineKeyboardButton("💎 Transparent PNG", callback_data="bg_transparent")
    )
    kb.row(InlineKeyboardButton("❌ Close Editor", callback_data="cancel"))
    return kb

def get_pixo_filters():
    kb = InlineKeyboardMarkup(row_width=3)
    filters = {
        "🎞 Vintage": "vintage", "🌑 Gray": "grayscale", "🎨 Sepia": "sepia",
        "🌈 Techni": "technicolor", "🎭 Kodach": "kodachrome", "🔄 Invert": "invert"
    }
    for label, code in filters.items():
        kb.insert(InlineKeyboardButton(label, callback_data=f"pixo_{code}"))
    kb.row(InlineKeyboardButton("🔙 Back to Tools", callback_data="back_to_main"))
    return kb

def get_adj_options():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔆 Brighten", callback_data="adj_bright"),
        InlineKeyboardButton("🍭 Vivid Color", callback_data="adj_sat"),
        InlineKeyboardButton("🤖 AI Magic Fix", callback_data="adj_auto"),
        InlineKeyboardButton("🔙 Back to Tools", callback_data="back_to_main")
    )
    return kb

def get_bg_colors():
    kb = InlineKeyboardMarkup(row_width=3)
    colors = {
        "🔵 Blue": "blue", "⚪ White": "white", "🔴 Red": "red",
        "🟢 Green": "green", "🟡 Yellow": "yellow", "🟣 Pink": "pink"
    }
    for label, code in colors.items():
        kb.insert(InlineKeyboardButton(label, callback_data=f"bg_{code}"))
    kb.row(InlineKeyboardButton("🔙 Back to Tools", callback_data="back_to_main"))
    return kb

# --- 4. Handlers ---

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    await m.reply(
        "👋 **Welcome to Dominic Pro Studio!**\n\n"
        "AI စနစ်သုံး Professional Photo Editor ဖြစ်ပါတယ်။\n"
        "စတင်ရန် ဓာတ်ပုံတစ်ပုံ ပို့ပေးပါ ကိုကို။",
        parse_mode="Markdown"
    )

@dp.message_handler(content_types=['photo'])
async def photo_in(m: types.Message):
    # ဒီမှာ reply_to_message_id ထည့်ထားတာက Error မတက်အောင် ကာကွယ်ပေးပါတယ်
    await m.reply(
        "📸 **Image Detected!**\nပြုပြင်လိုသည့် Tool ကို ရွေးချယ်ပါ-",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@dp.callback_query_handler(lambda c: True)
async def callbacks(cb: types.CallbackQuery):
    d = cb.data
    cid = cb.message.chat.id
    mid = cb.message.message_id

    if d == "menu_bg":
        await bot.edit_message_text("🖼 **Choose Background Color**", cid, mid, reply_markup=get_bg_colors(), parse_mode="Markdown")
        return
    elif d == "menu_pixo":
        await bot.edit_message_text("🎨 **Special FX Filters**", cid, mid, reply_markup=get_pixo_filters(), parse_mode="Markdown")
        return
    elif d == "menu_adj":
        await bot.edit_message_text("⚙️ **Professional Adjustments**", cid, mid, reply_markup=get_adj_options(), parse_mode="Markdown")
        return
    elif d == "back_to_main":
        await bot.edit_message_text("✨ **Main Editor Menu**", cid, mid, reply_markup=get_main_keyboard(), parse_mode="Markdown")
        return
    elif d == "cancel":
        await bot.delete_message(cid, mid)
        return
    
    # --- API Processing ---
    await bot.edit_message_text("⚙️ **Dominic AI is processing...**", cid, mid, parse_mode="Markdown")
    
    try:
        # ပုံကို ပြန်ရှာတဲ့အခါ ပိုသေချာအောင် စစ်ဆေးမယ်
        if cb.message.reply_to_message and cb.message.reply_to_message.photo:
            file = await cb.message.reply_to_message.photo[-1].get_file()
            p_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}"
        else:
            await bot.send_message(cid, "❌ **Error:** ပုံကို ပြန်ရှာမတွေ့ပါ။ ကျေးဇူးပြု၍ ပုံကို အသစ်ပြန်ပို့ပေးပါ။")
            return

        # Pixo Tools
        if d.startswith("pixo_") or d.startswith("adj_"):
            action = d.split("_")[1]
            p_base = "https://api.pixoeditor.com/v1/transform"
            p_params = {'apikey': PIXO_API_KEY, 'image': p_url}
            
            # Map Pixo Actions
            if action == "auto": p_params['auto_enhance'] = 'true'
            elif action == "bright": p_params['brightness'] = '30'
            elif action == "sat": p_params['saturation'] = '50'
            else: p_params['filter'] = action
            
            res = requests.get(p_base, params=p_params)
            cap = f"🎨 **Pixo Style:** {action.capitalize()}"

        # Remove.bg Tools
        elif d.startswith("bg_") or d == "bg_transparent":
            color = d.replace("bg_", "")
            rb_params = {'image_url': p_url, 'size': 'auto'}
            if color != "transparent": rb_params['bg_color'] = color
            res = requests.post('https://api.remove.bg/v1.0/removebg', data=rb_params, headers={'X-API-Key': REMOVE_BG_API_KEY})
            cap = f"🖼 **Background:** {color.capitalize()}"

        if res.status_code == 200:
            out = io.BytesIO(res.content)
            out.name = "dominic_pro.png"
            await bot.send_document(cid, document=out, caption=f"{cap}\n_Done by Dominic AI_", parse_mode="Markdown")
            await bot.delete_message(cid, mid)
        else:
            await bot.send_message(cid, f"❌ **API Error:** {res.status_code}\nCredit ကျန်မကျန် ပြန်စစ်ပေးပါ ကိုကို။")

    except Exception as e:
        logging.error(e)
        await bot.send_message(cid, "❌ **Critical Error!**\nပုံကို ပြန်ပို့ပြီး ထပ်မံကြိုးစားကြည့်ပါ ကိုကို။")

    await bot.answer_callback_query(cb.id)

if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
