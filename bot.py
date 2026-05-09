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

# ၁။ Web Server
app = Flask('')
@app.route('/')
def home(): return Response("Bot System is Online!", status=200)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ၂။ Database Setup
def init_db():
    conn = sqlite3.connect('bot_pro.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings 
                 (key TEXT PRIMARY KEY, value TEXT)''')
    # Default Settings
    c.execute("INSERT OR IGNORE INTO settings VALUES ('status', 'on')")
    c.execute("INSERT OR IGNORE INTO settings VALUES ('admin_id', '5123456789')") # အစပိုင်းတွင် မိမိ ID ပြောင်းပါ
    conn.commit()
    conn.close()

init_db()

# ၃။ Bot Setup
logging.basicConfig(level=logging.INFO)
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class AdminStates(StatesGroup):
    waiting_for_new_admin = State()
    waiting_for_broadcast = State()

# Functions to check status and admin
def get_setting(key):
    conn = sqlite3.connect('bot_pro.db')
    val = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return val[0] if val else None

def set_setting(key, value):
    conn = sqlite3.connect('bot_pro.db')
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

# Keyboards
def main_menu(user_id):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("➕ Build Bot", "📊 My Stats")
    kb.add("🔗 Referral Link")
    if str(user_id) == get_setting('admin_id'):
        kb.add("👮 Admin Panel")
    return kb

def admin_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    status = "🔴 Stop Bot" if get_setting('status') == 'on' else "🟢 Start Bot"
    kb.add(status, "📢 Broadcast")
    kb.add("🔑 Change Admin ID", "📈 Total Users")
    kb.add("🔙 Back")
    return kb

# --- Middleware-like check for Maintenance ---
async def is_maintenance(message: types.Message):
    if get_setting('status') == 'off' and str(message.from_user.id) != get_setting('admin_id'):
        await message.reply("⚠️ Bot ကို ခေတ္တရပ်နားထားပါသည်။ ခဏအကြာမှ ပြန်လည်ကြိုးစားပါ။")
        return True
    return False

@dp.message_handler(commands=['start'], state="*")
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    if await is_maintenance(message): return

    user_id = message.from_user.id
    conn = sqlite3.connect('bot_pro.db')
    conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

    await message.reply("မင်္ဂလာပါ။ အလိုရှိရာကို ရွေးချယ်ပေးပါ။", reply_markup=main_menu(user_id))

# --- Admin Panel Logic ---
@dp.message_handler(lambda m: m.text == "👮 Admin Panel", state="*")
async def admin_start(message: types.Message):
    if str(message.from_user.id) != get_setting('admin_id'): return
    await message.reply("Admin Control Panel ရောက်ရှိနေပါသည်။", reply_markup=admin_menu())

@dp.message_handler(lambda m: m.text in ["🔴 Stop Bot", "🟢 Start Bot"], state="*")
async def toggle_status(message: types.Message):
    if str(message.from_user.id) != get_setting('admin_id'): return
    new_status = 'off' if get_setting('status') == 'on' else 'on'
    set_setting('status', new_status)
    msg = "Bot ကို ရပ်တန့်လိုက်ပါပြီ ❌" if new_status == 'off' else "Bot ကို ပြန်လည်ဖွင့်လှစ်လိုက်ပါပြီ ✅"
    await message.reply(msg, reply_markup=admin_menu())

@dp.message_handler(lambda m: m.text == "🔑 Change Admin ID")
async def change_admin_prompt(message: types.Message):
    if str(message.from_user.id) != get_setting('admin_id'): return
    await message.reply("Admin အသစ်ဖြစ်မည့်သူ၏ Telegram ID ကို ပို့ပေးပါ။")
    await AdminStates.waiting_for_new_admin.set()

@dp.message_handler(state=AdminStates.waiting_for_new_admin)
async def process_new_admin(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        set_setting('admin_id', message.text)
        await message.reply(f"✅ Admin ID ကို {message.text} သို့ ပြောင်းလဲလိုက်ပါပြီ။", reply_markup=main_menu(message.from_user.id))
        await state.finish()
    else:
        await message.reply("❌ ဂဏန်းသက်သက်သာ ပို့ပေးပါ။")

@dp.message_handler(lambda m: m.text == "📈 Total Users")
async def total_users(message: types.Message):
    if str(message.from_user.id) != get_setting('admin_id'): return
    conn = sqlite3.connect('bot_pro.db')
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    await message.reply(f"📊 စုစုပေါင်းအသုံးပြုသူ: {count} ယောက်")

@dp.message_handler(lambda m: m.text == "📢 Broadcast")
async def broad_prompt(message: types.Message):
    if str(message.from_user.id) != get_setting('admin_id'): return
    await message.reply("User အားလုံးဆီ ပို့မည့်စာသားကို ပို့ပေးပါ။")
    await AdminStates.waiting_for_broadcast.set()

@dp.message_handler(state=AdminStates.waiting_for_broadcast)
async def perform_broadcast(message: types.Message, state: FSMContext):
    conn = sqlite3.connect('bot_pro.db')
    users = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()
    
    count = 0
    for user in users:
        try:
            await bot.send_message(user[0], message.text)
            count += 1
            await asyncio.sleep(0.05) # Rate limit ရှောင်ရန်
        except: pass
    
    await message.reply(f"✅ လူပေါင်း {count} ယောက်ထံ ပေးပို့ပြီးပါပြီ။", reply_markup=admin_menu())
    await state.finish()

@dp.message_handler(lambda m: m.text == "🔙 Back", state="*")
async def go_back(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("ပင်မ Menu သို့ ပြန်ရောက်ပါပြီ။", reply_markup=main_menu(message.from_user.id))

# --- ပင်မ Menu Features များ ---
@dp.message_handler(lambda m: m.text == "📊 My Stats")
async def my_stats(message: types.Message):
    if await is_maintenance(message): return
    await message.reply(f"👤 အမည်: {message.from_user.full_name}\n🆔 ID: {message.from_user.id}")

@dp.message_handler(lambda m: m.text == "➕ Build Bot")
async def build_bot(message: types.Message):
    if await is_maintenance(message): return
    await message.reply("တည်ဆောက်လိုသော Bot Token ကို ပို့ပေးပါ။")

# Main Runner
async def main():
    Thread(target=run_flask, daemon=True).start()
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
