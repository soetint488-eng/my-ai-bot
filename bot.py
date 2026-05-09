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
def home(): return Response("Multi-Bot Engine is Live!", status=200)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ၂။ Database Setup
def init_db():
    conn = sqlite3.connect('engine.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bots 
                 (token TEXT PRIMARY KEY, start_text TEXT, buttons TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ၃။ Master Bot Setup
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class BuildStates(StatesGroup):
    waiting_for_token = State()
    waiting_for_text = State()
    waiting_for_btn_name = State()
    waiting_for_btn_link = State()

# --- Target Bot များကို Manage လုပ်မည့် Function ---
# ဤ Function သည် Token အသစ်ဝင်လာတိုင်း ထို Bot ကို Polling စတင်ပေးပါမည်
active_bots = {}

async def start_target_bot(token, start_text, buttons_data):
    if token in active_bots: return
    
    try:
        t_bot = Bot(token=token)
        t_dp = Dispatcher(t_bot)
        
        @t_dp.message_handler(commands=['start'])
        async def target_start(message: types.Message):
            kb = types.InlineKeyboardMarkup(row_width=1)
            # Buttons data ကို list ပြန်ပြောင်းပြီး ထည့်ခြင်း
            import json
            btns = json.loads(buttons_data)
            for b in btns:
                kb.add(types.InlineKeyboardButton(text=b['name'], url=b['link']))
            await message.reply(start_text, reply_markup=kb)
        
        active_bots[token] = t_dp
        asyncio.create_task(t_dp.start_polling())
        print(f"Started polling for bot: {token[:10]}...")
    except Exception as e:
        print(f"Error starting bot {token[:10]}: {e}")

# Master Bot Start
@dp.message_handler(commands=['start'], state="*")
async def master_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("မင်္ဂလာပါ။ Bot Token ပေးပို့ရန် '➕ Build Bot' ကို နှိပ်ပါ။", 
                       reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("➕ Build Bot"))

@dp.message_handler(lambda m: m.text == "➕ Build Bot", state="*")
async def ask_token(message: types.Message):
    await message.reply("Bot Token ကို ပေးပို့ပေးပါ။")
    await BuildStates.waiting_for_token.set()

@dp.message_handler(state=BuildStates.waiting_for_token)
async def get_token(message: types.Message, state: FSMContext):
    token = message.text.strip()
    try:
        tmp = Bot(token=token)
        me = await tmp.get_me()
        await tmp.close()
        await state.update_data(target_token=token, buttons=[])
        await message.reply(f"🤖 Bot: @{me.username}\n\n/start မှာပြမည့် စာသားကို ပို့ပေးပါ။")
        await BuildStates.waiting_for_text.set()
    except:
        await message.reply("❌ Token မှားနေပါသည်။")

@dp.message_handler(state=BuildStates.waiting_for_text)
async def get_text(message: types.Message, state: FSMContext):
    await state.update_data(start_text=message.text)
    await message.reply("ခလုတ်အမည် ပို့ပေးပါ။ (ပြီးလျှင် /done)")
    await BuildStates.waiting_for_btn_name.set()

@dp.message_handler(state=BuildStates.waiting_for_btn_name)
async def get_btn_name(message: types.Message, state: FSMContext):
    if message.text == "/done":
        data = await state.get_data()
        import json
        btns_json = json.dumps(data['buttons'])
        
        # Database သိမ်းဆည်းခြင်း
        conn = sqlite3.connect('engine.db')
        conn.execute("INSERT OR REPLACE INTO bots VALUES (?, ?, ?)", 
                     (data['target_token'], data['start_text'], btns_json))
        conn.commit()
        conn.close()
        
        # Target Bot ကို ချက်ချင်း Run ပေးခြင်း
        await start_target_bot(data['target_token'], data['start_text'], btns_json)
        
        await message.reply("🎉 အောင်မြင်ပါပြီ။ ယခု သင်၏ Bot ထဲသို့သွား၍ /start စမ်းကြည့်နိုင်ပါပြီ။")
        await state.finish()
        return
    
    await state.update_data(curr_btn=message.text)
    await message.reply(f"'{message.text}' အတွက် Link ပို့ပေးပါ။")
    await BuildStates.waiting_for_btn_link.set()

@dp.message_handler(state=BuildStates.waiting_for_btn_link)
async def get_btn_link(message: types.Message, state: FSMContext):
    data = await state.get_data()
    btns = data.get('buttons', [])
    btns.append({'name': data['curr_btn'], 'link': message.text})
    await state.update_data(buttons=btns)
    await message.reply("နောက်ထပ်ခလုတ်အမည် ပို့ပေးပါ။ (ပြီးလျှင် /done)")
    await BuildStates.waiting_for_btn_name.set()

# Bot ပြန်ပွင့်လာတိုင်း သိမ်းထားသော Bot အဟောင်းများကို ပြန်နှိုးခြင်း
async def resume_bots():
    conn = sqlite3.connect('engine.db')
    bots = conn.execute("SELECT * FROM bots").fetchall()
    conn.close()
    for b in bots:
        asyncio.create_task(start_target_bot(b[0], b[1], b[2]))

async def main():
    Thread(target=run_flask, daemon=True).start()
    await resume_bots() # Bot ဟောင်းများ ပြန်နှိုးခြင်း
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
