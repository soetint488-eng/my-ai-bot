import os
import sqlite3
import logging
import asyncio
import json
from flask import Flask, Response
from threading import Thread
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# ၁။ Web Server
app = Flask('')
@app.route('/')
def home(): return Response("Bot System Online", status=200)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ၂။ Master Bot Setup
MASTER_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
bot = Bot(token=MASTER_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class BuildStates(StatesGroup):
    waiting_for_token = State()
    waiting_for_text = State()
    waiting_for_btn_name = State()
    waiting_for_btn_link = State()

# --- Target Bot ကို အသက်သွင်းမည့် Function ---
async def activate_target_bot(token, start_text, buttons):
    try:
        t_bot = Bot(token=token)
        # အရင်ရှိနေတဲ့ Webhook သို့မဟုတ် Polling တွေကို ရှင်းထုတ်ပစ်ရန်
        await t_bot.delete_webhook(drop_pending_updates=True)
        
        # Dispatcher အသစ်တစ်ခုနဲ့ Polling စတင်ရန်
        t_dp = Dispatcher(t_bot)

        @t_dp.message_handler(commands=['start'])
        async def send_welcome(message: types.Message):
            kb = types.InlineKeyboardMarkup(row_width=1)
            for b in buttons:
                kb.add(types.InlineKeyboardButton(text=b['name'], url=b['link']))
            await message.reply(start_text, reply_markup=kb)

        # Polling ကို Background မှာ Run ခိုင်းခြင်း
        asyncio.create_task(t_dp.start_polling())
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# --- Master Bot UI ---
@dp.message_handler(commands=['start'], state="*")
async def start_cmd(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("မင်္ဂလာပါ။ Bot အသစ်ပြုလုပ်ရန် ခလုတ်ကိုနှိပ်ပါ။", 
                       reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("➕ Build Bot"))

@dp.message_handler(lambda m: m.text == "➕ Build Bot", state="*")
async def ask_token(message: types.Message):
    await message.reply("အသုံးပြုမည့် Bot Token ကို ပေးပို့ပါ။")
    await BuildStates.waiting_for_token.set()

@dp.message_handler(state=BuildStates.waiting_for_token)
async def get_token(message: types.Message, state: FSMContext):
    token = message.text.strip()
    try:
        tmp = Bot(token=token)
        me = await tmp.get_me()
        await tmp.close()
        await state.update_data(target_token=token, buttons=[])
        await message.reply(f"🤖 Bot: @{me.username}\n\n/start မှာပြမည့်စာကို ပို့ပေးပါ။")
        await BuildStates.next()
    except:
        await message.reply("❌ Token မှားနေပါသည်။")

@dp.message_handler(state=BuildStates.waiting_for_text)
async def get_text(message: types.Message, state: FSMContext):
    await state.update_data(start_text=message.text)
    await message.reply("ခလုတ်အမည် ပို့ပါ။ (မရှိလျှင် /done)")
    await BuildStates.next()

@dp.message_handler(state=BuildStates.waiting_for_btn_name)
async def get_btn_name(message: types.Message, state: FSMContext):
    if message.text == "/done":
        data = await state.get_data()
        success = await activate_target_bot(data['target_token'], data['start_text'], data['buttons'])
        if success:
            await message.reply("🎉 အောင်မြင်ပါပြီ။ သင့် Bot ကို စမ်းသပ်နိုင်ပါပြီ။")
        else:
            await message.reply("❌ တစ်စုံတစ်ခု မှားယွင်းနေပါသည်။")
        await state.finish()
        return
    await state.update_data(curr_name=message.text)
    await message.reply(f"'{message.text}' အတွက် Link ပို့ပါ။")
    await BuildStates.next()

@dp.message_handler(state=BuildStates.waiting_for_btn_link)
async def get_btn_link(message: types.Message, state: FSMContext):
    data = await state.get_data()
    btns = data.get('buttons', [])
    btns.append({'name': data['curr_name'], 'link': message.text})
    await state.update_data(buttons=btns)
    await message.reply("နောက်ထပ် ခလုတ်အမည်ပို့ပါ။ သို့မဟုတ် /done", 
                       reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("/done"))
    await BuildStates.waiting_for_btn_name.set()

async def main():
    Thread(target=run_flask, daemon=True).start()
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
