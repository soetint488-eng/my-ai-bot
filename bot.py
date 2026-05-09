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
def home(): return "200 OK - Dominic Pro Studio is Active!"

def run_web(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run_web).start()

# --- 2. API Setup ---
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
REMOVE_BG_API_KEY = 'NJqyHZ2Du9oAhnNiiTazFPpo'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- 3. UI Keyboards (Premium Glassmorphism Style) ---

def get_main_menu(f_id):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✂️ Remove Background", callback_data=f"opt_trans|{f_id}"),
        InlineKeyboardButton("🌈 Change Color", callback_data=f"nav_colors|{f_id}"),
        InlineKeyboardButton("🌑 Add Real Shadow", callback_data=f"opt_shadow|{f_id}"),
        InlineKeyboardButton("💎 Ultra HD Mode", callback_data=f"opt_hd|{f_id}")
    )
    kb.row(InlineKeyboardButton("❌ Discard Image", callback_data="cancel"))
    return kb

def get_color_menu(f_id):
    kb = InlineKeyboardMarkup(row_width=3)
    colors = {
        "🔵 Blue": "blue", "⚪ White": "white", "🔴 Red": "red", 
        "🟢 Green": "green", "🟡 Yellow": "yellow", "🟣 Pink": "pink"
    }
    for label, val in colors.items():
        kb.insert(InlineKeyboardButton(label, callback_data=f"clr_{val}|{f_id}"))
    kb.row(InlineKeyboardButton("🔙 Back to Main Menu", callback_data=f"back|{f_id}"))
    return kb

# --- 4. Handlers ---

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    # Start UI ကို ပိုပြီး Professional ဖြစ်အောင် စာသားနဲ့ Emoji ကို သေချာစီထားပါတယ်
    welcome_msg = (
        "✨ **WELCOME TO DOMINIC STUDIO AI** ✨\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 **Professional Background Remover**\n\n"
        "ကိုကို့ရဲ့ ဓာတ်ပုံတွေကို တစ်ချက်နှိပ်ရုံနဲ့ \n"
        "Professional ဆန်ဆန် ပြုပြင်ပေးမယ့် AI Bot ပါ။\n\n"
        "🚀 **စတင်ရန် ဓာတ်ပုံတစ်ပုံ ပို့ပေးပါ ကိုကို!**"
    )
    await m.reply(welcome_msg, parse_mode="Markdown")

@dp.message_handler(content_types=['photo'])
async def photo_in(m: types.Message):
    # ပုံကို လက်ခံရရှိကြောင်း ချက်ချင်း သိသာအောင် Loading အရင်ပြမယ်
    status = await m.reply("📸 **Processing Image...**", parse_mode="Markdown")
    
    try:
        f_id = m.photo[-1].file_id # အကြည်ဆုံးပုံရဲ့ ID ကိုယူမယ်
        
        menu_text = (
            "✅ **Image Loaded Successfully!**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "အောက်ပါ Professional Tools များထဲမှ ရွေးချယ်ပါ ကိုကို-"
        )
        
        # Loading message ကို ဖျက်ပြီး Menu UI ကို ပြောင်းမယ်
        await bot.edit_message_text(
            menu_text, 
            status.chat.id, 
            status.message_id, 
            reply_markup=get_main_menu(f_id),
            parse_mode="Markdown"
        )
    except Exception as e:
        await status.edit_text("❌ ပုံဖတ်တာ မှားယွင်းနေပါတယ်။ ကျေးဇူးပြု၍ ပြန်ပို့ပေးပါ။")

@dp.callback_query_handler(lambda c: True)
async def callbacks(cb: types.CallbackQuery):
    d = cb.data.split("|")
    cmd = d[0]
    f_id = d[1] if len(d) > 1 else None
    cid, mid = cb.message.chat.id, cb.message.message_id

    # UI Navigation
    if cmd == "nav_colors":
        await bot.edit_message_text("🌈 **Select Background Color**", cid, mid, reply_markup=get_color_menu(f_id), parse_mode="Markdown")
        return
    elif cmd == "back":
        await bot.edit_message_text("✨ **Main Editor Menu**", cid, mid, reply_markup=get_main_menu(f_id), parse_mode="Markdown")
        return
    elif cmd == "cancel":
        await bot.delete_message(cid, mid)
        return

    # Processing Logic
    if f_id:
        await bot.edit_message_text("⚙️ **AI စနစ်က ပြုပြင်နေပါပြီ... ခဏစောင့်ပါဗျ။**", cid, mid, parse_mode="Markdown")
        try:
            file = await bot.get_file(f_id)
            p_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}"
            headers = {'X-API-Key': REMOVE_BG_API_KEY}
            params = {'image_url': p_url, 'size': 'auto'}

            # Feature logic
            if cmd == "opt_trans": cap = "✂️ **Background Removed Successfully!**"
            elif cmd == "opt_shadow": 
                params['add_shadow'] = 'true'
                cap = "🌑 **Shadow Added Successfully!**"
            elif cmd == "opt_hd":
                params['size'] = 'full'
                cap = "💎 **Full HD Result Delivered!**"
            elif cmd.startswith("clr_"):
                color = cmd.split("_")[1]
                params['bg_color'] = color
                cap = f"🎨 **{color.capitalize()} Background Applied!**"

            res = requests.post('https://api.remove.bg/v1.0/removebg', data=params, headers=headers)
            
            if res.status_code == 200:
                out = io.BytesIO(res.content)
                out.name = "dominic_pro_studio.png"
                await bot.send_document(cid, document=out, caption=f"{cap}\n\n_Powered by Dominic AI Pro Studio_")
                await bot.delete_message(cid, mid)
            else:
                await bot.send_message(cid, "❌ **API Error:** Credit မလုံလောက်တော့ပါဘူး ကိုကို။")
        except:
            await bot.send_message(cid, "❌ **Error:** လုပ်ဆောင်ချက် မအောင်မြင်ပါ။")

    await bot.answer_callback_query(cb.id)

if __name__ == '__main__':
    keep_alive() # Cron-job keep alive
    print("Dominic Pro Studio Bot is Online!")
    executor.start_polling(dp, skip_updates=True)
