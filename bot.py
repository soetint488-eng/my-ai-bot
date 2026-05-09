import os
import sqlite3
import logging
import asyncio
from flask import Flask, Response
from threading import Thread
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# ၁။ Web Server (Render အတွက်)
app = Flask('')
@app.route('/')
def home(): return Response("Multi-Bot Builder is Online!", status=200)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ၂။ Database Setup
def init_db():
    conn = sqlite3.connect('bot_builder.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute("INSERT OR IGNORE INTO settings VALUES ('status', 'on')")
    c.execute("INSERT OR IGNORE INTO settings VALUES ('admin_id', '5123456789')") # ကိုယ့် ID ပြောင်းပါ
    conn.commit()
    conn.close()

init_db()

# ၃။ Master Bot Setup
logging.basicConfig(level=logging.INFO)
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class BuildStates(StatesGroup):
    waiting_for_token = State()
    waiting_for_text = State()
    waiting_for_btn_name = State()
    waiting_for_btn_link = State()

def get_main_menu(user_id):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("➕ Build Bot", "📊 My Stats")
    kb.add("🔗 Referral Link")
    # Database ထဲက Admin ID နဲ့ တိုက်စစ်မယ်
    conn = sqlite3.connect('bot_builder.db')
    admin_id = conn.execute("SELECT value FROM settings WHERE key='admin_id'").fetchone()[0]
    conn.close()
    if str(user_id) == admin_id:
        kb.add("👮 Admin Panel")
    return kb

# --- Start Command ---
@dp.message_handler(commands=['start'], state="*")
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    
    conn = sqlite3.connect('bot_builder.db')
    conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

    await message.reply("မင်္ဂလာပါ။ Bot Builder မှ ကြိုဆိုပါတယ်။ Token ပေးပြီး Bot တည်ဆောက်နိုင်ပါပြီ။", reply_markup=get_main_menu(user_id))

# --- Build Bot Logic ---
@dp.message_handler(lambda m: m.text == "➕ Build Bot", state="*")
async def ask_token(message: types.Message):
    await message.reply("ဟုတ်ကဲ့။ Bot Father ဆီကရလာတဲ့ **Bot Token** ကို ပေးပို့ပေးပါ။")
    await BuildStates.waiting_for_token.set()

# Token ပေးရင် ဒီနေရာကနေ အကြောင်းပြန်ပါမယ်
@dp.message_handler(state=BuildStates.waiting_for_token)
async def check_token(message: types.Message, state: FSMContext):
    token = message.text.strip()
    await message.reply("Token ကို စစ်ဆေးနေပါတယ်... ခဏစောင့်ပါ။")
    
    try:
        temp_bot = Bot(token=token)
        me = await temp_bot.get_me()
        await temp_bot.close()
        
        await state.update_data(target_token=token, buttons=[])
        await message.reply(f"✅ Bot ချိတ်ဆက်မှု အောင်မြင်သည်!\n🤖 Bot: @{me.username}\n\n/start မှာပြမည့် စာသားကို ပို့ပေးပါ။")
        await BuildStates.waiting_for_text.set()
        
    except Exception as e:
        await message.reply("❌ Token မှားနေပါတယ်။ Bot Father ဆီက Token အမှန်ကို ပြန်ကူးပြီး ပို့ပေးပါ။")

# စာသား လက်ခံခြင်း
@dp.message_handler(state=BuildStates.waiting_for_text)
async def get_text(message: types.Message, state: FSMContext):
    await state.update_data(start_text=message.text)
    await message.reply("ခလုတ်အမည် (Button Name) ကို ပို့ပေးပါ။ (မရှိလျှင် /done ဟု ပို့ပါ)")
    await BuildStates.waiting_for_btn_name.set()

# ခလုတ်အမည် လက်ခံခြင်း
@dp.message_handler(state=BuildStates.waiting_for_btn_name)
async def get_btn_name(message: types.Message, state: FSMContext):
    if message.text == "/done":
        data = await state.get_data()
        await message.reply("🎉 အားလုံးပြီးပါပြီ။ Bot Configuration အောင်မြင်သွားပါပြီ။", reply_markup=get_main_menu(message.from_user.id))
        await state.finish()
        return
    
    await state.update_data(current_btn=message.text)
    await message.reply(f"'{message.text}' အတွက် Link ကို ပို့ပေးပါ။")
    await BuildStates.waiting_for_btn_link.set()

# ခလုတ်လင့်ခ် လက်ခံခြင်း
@dp.message_handler(state=BuildStates.waiting_for_btn_link)
async def get_btn_link(message: types.Message, state: FSMContext):
    data = await state.get_data()
    btns = data.get('buttons', [])
    btns.append({'name': data['current_btn'], 'link': message.text})
    
    await state.update_data(buttons=btns)
    await message.reply("နောက်ထပ် ခလုတ်အမည် ထပ်ပို့ပါ။ (မရှိတော့လျှင် /done ကို နှိပ်ပါ)")
    await BuildStates.waiting_for_btn_name.set()

# --- Main Runner ---
async def main():
    Thread(target=run_flask, daemon=True).start()
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
