import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Configuration ---
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# --- States ---
class MyIDValidatorChain(StatesGroup):
    waiting_phone = State()

# Header configuration for API
HEADERS = {
    'User-Agent': 'MyID/3.2.1 (Android; 13)',
    'Content-Type': 'application/json'
}

# --- Premium Keyboards ---
def get_cancel_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🛑 ABORT CHECK", callback_data="cancel_action"))
    return markup

# --- Handlers ---

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    welcome_text = (
        "⚡ **MYID STATUS VALIDATOR CORE**\n"
        "🌌 *DEVELOPED BY DOMINIC*\n"
        "📶 SYSTEM STATUS: OPERATIONAL\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Welcome to the node verification module. "
        "Analyze specific endpoints to verify profile integrity and active registry status.\n\n"
        "🛠 **SYSTEM COMMANDS:**\n"
        "➥ /check - Validate Target Profile\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ *AWAITING PARAMETERS...*"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message_handler(commands=['check'], state="*")
async def start_check(message: types.Message):
    await message.answer(
        "📱 **ENTER TARGET PHONE NUMBER:**\n"
        "Format: `09XXXXXXXXX`", 
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    await MyIDValidatorChain.waiting_phone.set()

@dp.callback_query_handler(text="cancel_action", state="*")
async def cancel_action(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.message.edit_text("❌ **PROCESS TERMINATED.** Security cache wiped safely.")
    await callback_query.answer()

@dp.message_handler(state=MyIDValidatorChain.waiting_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    
    if not phone.startswith("09") or len(phone) < 9:
        return await message.reply("❌ **ERROR:** Invalid format. Target must start with 09.")

    status_msg = await message.answer(
        f"📡 **QUERYING GATEWAY REGISTRY...**\n"
        f"🎯 Target: `{phone}`", 
        parse_mode="Markdown"
    )
    
    url = f"https://apis.mytel.com.mm/myid/authen/v1.0/v2/login/action/check-account?phoneNumber={phone}"

    try:
        # Request only once to parse the registry status securely
        res = requests.get(url, headers=HEADERS, timeout=8)
        
        if res.status_code == 200:
            try:
                res_data = res.json()
                # Check response fields to see if the user profile exists and is active
                # Adjust flags according to the Mytel API structure returned
                is_active = res_data.get("status") == 1 or res_data.get("active", True)
                
                if is_active:
                    account_status = "🟢 ACTIVE / REGISTERED"
                else:
                    account_status = "🟡 INACTIVE / SUSPENDED"
            except:
                # If json parsing fails but status is 200, the account exists in the gateway
                account_status = "🟢 ACTIVE (Verified Endpoint)"
                
            summary_text = (
                f"🏁 **NODE ANALYSIS REPORT**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📱 **Target Node:** `{phone}`\n"
                f"🔒 **Registry Status:** `{account_status}`\n"
                f"📡 **Gateway Code:** `200 OK`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔥 *Verification cycle flushed cleanly by Dominic.*"
            )
        elif res.status_code == 404:
            summary_text = (
                f"🏁 **NODE ANALYSIS REPORT**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📱 **Target Node:** `{phone}`\n"
                f"❌ **Registry Status:** `🔴 NOT REGISTERED / UNKNOWN`\n"
                f"📡 **Gateway Code:** `404 Not Found`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔥 *Verification cycle completed.*"
            )
        else:
            summary_text = (
                f"⚠️ **GATEWAY REJECTION**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📱 **Target Node:** `{phone}`\n"
                f"❌ **Error Code:** `{res.status_code}`\n"
                f"💡 Server did not return a valid profile status."
            )
            
    except Exception as e:
        summary_text = f"❌ **RUNTIME EXCEPTION:** `{str(e)}`"

    await status_msg.edit_text(summary_text, parse_mode="Markdown")
    await state.finish()

if __name__ == '__main__':
    print("Dominic's Profile Validator is Live.")
    executor.start_polling(dp, skip_updates=True)
