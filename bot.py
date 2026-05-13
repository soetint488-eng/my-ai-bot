import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# --- Setup ---
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# --- States ---
class MytelLogin(StatesGroup):
    waiting_phone = State()
    waiting_otp = State()

# Common Headers (Mytel API တွေက ဒါမျိုးတွေ တောင်းတတ်ပါတယ်)
HEADERS = {
    'User-Agent': 'MyID/3.2.1 (Android; 13)',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# --- Handlers ---

@dp.message_handler(commands=['start', 'login'])
async def start_login(m: types.Message):
    await m.reply("📱 **Mytel MyID Login**\n\nဖုန်းနံပါတ် ရိုက်ထည့်ပေးပါ ကိုကို။\n(ဥပမာ - 0969xxxxxxx)")
    await MytelLogin.waiting_phone.set()

@dp.message_handler(state=MytelLogin.waiting_phone)
async def process_phone(m: types.Message, state: FSMContext):
    phone = m.text.strip()
    
    # ၁။ Check Account API
    check_url = f"https://apis.mytel.com.mm/myid/authen/v1.0/v2/login/action/check-account?phoneNumber={phone}"
    
    try:
        res = requests.get(check_url, headers=HEADERS)
        data = res.json()
        
        if res.status_code == 200:
            # ဒီနေရာမှာ OTP ပို့တဲ့ API ကိုပါ တန်းခေါ်ပေးရမှာပါ (ကိုကိုပေးထားတဲ့ထဲ မပါလို့ Logic ပဲ ထည့်ထားတယ်)
            await state.update_data(phone=phone)
            await m.reply(f"✅ အကောင့်ရှိပါတယ်။ ဖုန်းထဲကို ပို့လိုက်တဲ့ **OTP ၆ လုံး** ကို ရိုက်ထည့်ပေးပါ ကိုကို။")
            await MytelLogin.waiting_otp.set()
        else:
            await m.reply("❌ အကောင့်စစ်ဆေးရတာ မအောင်မြင်ပါ။ ဖုန်းနံပါတ် ပြန်စစ်ပေးပါ။")
            await state.finish()
    except Exception as e:
        await m.reply(f"Error: {str(e)}")
        await state.finish()

@dp.message_handler(state=MytelLogin.waiting_otp)
async def process_otp(m: types.Message, state: FSMContext):
    otp = m.text.strip()
    user_data = await state.get_data()
    phone = user_data.get("phone")

    # ၂။ Validate OTP API
    validate_url = "https://apis.mytel.com.mm/myid/authen/v1.0/login/method/otp/validate-otp"
    
    payload = {
        "phoneNumber": phone,
        "otp": otp,
        "isWap": False # ဒါက API requirement ပေါ်မူတည်ပြီး ပြောင်းနိုင်ပါတယ်
    }

    try:
        res = requests.post(validate_url, json=payload, headers=HEADERS)
        result = res.json()

        if res.status_code == 200:
            # Login အောင်မြင်ရင် Access Token တွေ ပြန်လာပါလိမ့်မယ်
            await m.reply(f"🎉 **Login Successful!**\n\nAPI Response:\n`{result}`", parse_mode="Markdown")
        else:
            await m.reply(f"❌ OTP မှားယွင်းနေပါတယ်။\nMessage: {result.get('message', 'Unknown Error')}")
    except Exception as e:
        await m.reply(f"Error: {str(e)}")
    
    await state.finish()

if __name__ == '__main__':
    print("Mytel Bot is running...")
    executor.start_polling(dp, skip_updates=True)
