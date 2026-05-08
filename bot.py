import os
import logging
import asyncio
from flask import Flask, Response
from threading import Thread
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from gtts import gTTS # အသံပြောင်းဖို့အတွက်

# ၁။ Web Server
app = Flask('')
@app.route('/')
def home(): return Response("Super Bot Manager is Online!", status=200)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ၂။ Bot Setup
logging.basicConfig(level=logging.INFO)
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# States များ
class BotPro(StatesGroup):
    waiting_for_username = State()
    main_menu = State()
    making_buttons = State()
    making_tts = State()
    broadcasting = State()

# Keyboard များ
def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🔗 Create Buttons", "🎙 Text to Voice")
    keyboard.add("📢 Broadcast", "🆔 My ID")
    keyboard.add("⚙️ Settings", "❌ Reset")
    return keyboard

@dp.message_handler(commands=['start'], state="*")
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("မင်္ဂလာပါ ကိုကို! \nBot Manager ကို သုံးဖို့ ကိုကို့ Bot ရဲ့ **Username** (@botname) ကို အရင်ပို့ပေးပါဗျ။")
    await BotPro.waiting_for_username.set()

@dp.message_handler(state=BotPro.waiting_for_username)
async def set_username(message: types.Message, state: FSMContext):
    username = message.text if message.text.startswith('@') else '@' + message.text
    await state.update_data(bot_username=username)
    await message.reply(f"ဟုတ်ကဲ့ {username} အတွက် အသင့်ဖြစ်ပါပြီ! \nအောက်က Menu ကနေ စိတ်ကြိုက် လုပ်လို့ရပါပြီ ကိုကို။", reply_markup=main_keyboard())
    await BotPro.main_menu.set()

# --- Feature Handlers ---

@dp.message_handler(state=BotPro.main_menu)
async def handle_menu(message: types.Message, state: FSMContext):
    choice = message.text

    if choice == "🔗 Create Buttons":
        await message.reply("စာသားနဲ့ Button လင့်ခ်တွေကို ပို့ပေးပါ။ \n\nပုံစံ: \nစာသား | ခလုတ်အမည် | လင့်ခ်")
        await BotPro.making_buttons.set()

    elif choice == "🎙 Text to Voice":
        await message.reply("အသံပြောင်းချင်တဲ့ စာသားကို ပို့ပေးပါ ကိုကို။")
        await BotPro.making_tts.set()

    elif choice == "🆔 My ID":
        await message.reply(f"ကိုကို့ရဲ့ ID က: `{message.from_user.id}` \nChat ID က: `{message.chat.id}`", parse_mode="Markdown")

    elif choice == "📢 Broadcast":
        await message.reply("User အားလုံးဆီ ပို့ချင်တဲ့စာကို ပို့ပေးပါ။")
        await BotPro.broadcasting.set()

    elif choice == "❌ Reset":
        await state.finish()
        await message.reply("အကုန်လုံးကို ဖျက်လိုက်ပါပြီ။ /start ပြန်နှိပ်ပါ ကိုကို။", reply_markup=types.ReplyKeyboardRemove())

# --- Button Maker Logic ---
@dp.message_handler(state=BotPro.making_buttons)
async def process_buttons(message: types.Message, state: FSMContext):
    try:
        parts = message.text.split('|')
        text = parts[0].strip()
        btn_name = parts[1].strip()
        btn_link = parts[2].strip()

        kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(btn_name, url=btn_link))
        await message.reply("ကိုကို့ Bot အတွက် ပုံစံလေး ရပါပြီ-")
        await bot.send_message(message.chat.id, text, reply_markup=kb)
    except:
        await message.reply("ပုံစံမှားနေပါတယ် ကိုကို။ \n'စာသား | ခလုတ်အမည် | လင့်ခ်' ပုံစံ ပို့ပေးပါ။")
    await BotPro.main_menu.set()

# --- TTS Logic ---
@dp.message_handler(state=BotPro.making_tts)
async def process_tts(message: types.Message):
    await message.reply("အသံဖိုင် လုပ်နေပါတယ်...")
    tts = gTTS(message.text, lang='en') # မြန်မာစာအတွက်ဆို 'my' ပြောင်းနိုင်တယ် (support ရရင်)
    voice_io = io.BytesIO()
    tts.write_to_fp(voice_io)
    voice_io.seek(0)
    await bot.send_voice(message.chat.id, voice_io, caption="ကိုကို့အတွက် အသံဖိုင် ရပါပြီ!")
    await BotPro.main_menu.set()

# --- Broadcast Logic ---
@dp.message_handler(state=BotPro.broadcasting)
async def process_broadcast(message: types.Message):
    # ဒီမှာကတော့ လက်ရှိ User တစ်ယောက်တည်းမို့လို့ ကိုယ့်ကိုယ်ကိုယ်ပဲ ပြန်ပို့ပြမယ်
    await message.reply(f"သတင်းစကားကို ပို့လိုက်ပါပြီ- \n\n{message.text}")
    await BotPro.main_menu.set()

async def main():
    Thread(target=run_flask, daemon=True).start()
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
