import logging
import requests
import io
from threading import Thread
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- 1. Web Server for Uptime ---
app = Flask('')
@app.route('/')
def home(): return "200 OK - Dominic Studio"

def run_web(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run_web).start()

# --- 2. API Setup ---
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
REMOVE_BG_API_KEY = 'NJqyHZ2Du9oAhnNiiTazFPpo'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- 3. UI Keyboards (Premium Design) ---

def get_main_menu(f_id):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✂️ Remove BG", callback_data=f"opt_trans|{f_id}"),
        InlineKeyboardButton("🎨 Add Color", callback_data=f"nav_colors|{f_id}"),
        InlineKeyboardButton("🌑 Real Shadow", callback_data=f"opt_shadow|{f_id}"),
        InlineKeyboardButton("💎 Ultra HD", callback_data=f"opt_hd|{f_id}")
    )
    kb.row(InlineKeyboardButton("❌ Discard Image", callback_data="cancel"))
    return kb

def get_color_menu(f_id):
    kb = InlineKeyboardMarkup(row_width=3)
    # လိုင်စင်ဓာတ်ပုံအတွက် အသုံးများတာလေးတွေ ဦးစားပေးထားပါတယ်
    colors = {"🔵 Blue": "blue", "⚪ White": "white", "🔴 Red": "red", 
              "🟢 Green": "green", "🟡 Yellow": "yellow", "🟣 Pink": "pink"}
    for label, val in colors.items():
        kb.insert(InlineKeyboardButton(label, callback_data=f"clr_{val}|{f_id}"))
    kb.row(InlineKeyboardButton("🔙 Back to Main Menu", callback_data=f"back|{f_id}"))
    return kb

# --- 4. Handlers ---

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    welcome = (
        "✨ **DOMINIC PRO STUDIO AI** ✨\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "ကိုကို့ရဲ့ ဓာတ်ပုံတွေကို Professional ဆန်ဆန် \n"
        "ပြုပြင်ပေးဖို့ အသင့်ရှိနေပါပြီ။\n\n"
        "🚀 **ပြုပြင်လိုသည့် ဓာတ်ပုံကို ပို့ပေးပါ ကိုကို!**"
    )
    await m.reply(welcome, parse_mode="Markdown")

@dp.message_handler(content_types=['photo'])
async def photo_in(m: types.Message):
    # ပုံကို စစ်ဆေးတဲ့နေရာမှာ ပိုပြီး စိတ်ချရအောင် ပြင်ထားပါတယ်
    if not m.photo:
        return

    try:
        f_id = m.photo[-1].file_id # အကြည်ဆုံးပုံကို ယူမယ်
        
        # UI ကို ပိုလန်းအောင် စာသားတွေ ညှိထားပါတယ်
        menu_text = (
            "📸 **IMAGE DETECTED!**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "အောက်ပါ Tools များထဲမှ ရွေးချယ်ပါ ကိုကို-"
        )
        
        await m.reply(
            menu_text, 
            reply_markup=get_main_menu(f_id),
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Photo Handler Error: {e}")
        await m.reply("❌ **Error:** ပုံကို လက်ခံရရှိဖို့ ခေတ္တ အခက်အခဲရှိနေပါတယ်။ နောက်တစ်ပုံ ထပ်ပို့ပေးပါ ကိုကို။")

@dp.callback_query_handler(lambda c: True)
async def callbacks(cb: types.CallbackQuery):
    d = cb.data.split("|")
    cmd = d[0]
    f_id = d[1] if len(d) > 1 else None
    cid, mid = cb.message.chat.id, cb.message.message_id

    # --- UI Navigations ---
    if cmd == "nav_colors":
        await bot.edit_message_text("🌈 **Select Background Color**", cid, mid, reply_markup=get_color_menu(f_id), parse_mode="Markdown")
        return
    elif cmd == "back":
        await bot.edit_message_text("✨ **Main Editor Menu**", cid, mid, reply_markup=get_main_menu(f_id), parse_mode="Markdown")
        return
    elif cmd == "cancel":
        await bot.delete_message(cid, mid)
        return

    # --- Processing Engine ---
    if f_id:
        # Loading Animation အစား စာသားလှလှလေးနဲ့ ပြမယ်
        await bot.edit_message_text("⚙️ **Dominic AI အလုပ်လုပ်နေပါပြီ... ခဏစောင့်ပါဗျ။**", cid, mid, parse_mode="Markdown")
        
        try:
            # File URL ဆွဲတဲ့အခါ တိုက်ရိုက် မပို့ခင် စစ်မယ်
            file = await bot.get_file(f_id)
            file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}"
            
            headers = {'X-API-Key': REMOVE_BG_API_KEY}
            params = {'image_url': file_url, 'size': 'auto'}

            # Feature logic based on UI button
            if cmd == "opt_trans": cap = "✂️ Background Removed"
            elif cmd == "opt_shadow": 
                params['add_shadow'] = 'true'
                cap = "🌑 Shadow Effect Added"
            elif cmd == "opt_hd":
                params['size'] = 'full'
                cap = "💎 Full HD Quality Result"
            elif cmd.startswith("clr_"):
                color = cmd.split("_")[1]
                params['bg_color'] = color
                cap = f"🎨 {color.capitalize()} Background"

            # API Call
            res = requests.post('https://api.remove.bg/v1.0/removebg', data=params, headers=headers)
            
            if res.status_code == 200:
                out = io.BytesIO(res.content)
                out.name = "dominic_studio.png"
                await bot.send_document(cid, document=out, caption=f"✅ {cap}\n\n_Done by Dominic Pro Studio_")
                await bot.delete_message(cid, mid)
            else:
                await bot.send_message(cid, f"❌ **API Error:** Credit မရှိတော့ပါ သို့မဟုတ် Key သက်တမ်းကုန်နေပါတယ်။")
        except Exception as e:
            logging.error(f"Callback Error: {e}")
            await bot.send_message(cid, "❌ **Critical Error!**\nပုံကို ပြန်ပို့ပြီး ထပ်မံကြိုးစားကြည့်ပါ ကိုကို။")

    await bot.answer_callback_query(cb.id)

if __name__ == '__main__':
    keep_alive()
    print("Bot is ready to work!")
    executor.start_polling(dp, skip_updates=True)
