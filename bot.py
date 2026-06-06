import logging
import requests
import asyncio
import os
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
class MyIDLoginSystem(StatesGroup):
    waiting_phone = State()
    waiting_otp = State()

# Header configuration for API
HEADERS = {
    'User-Agent': 'MyID/3.2.1 (Android; 13)',
    'Content-Type': 'application/json'
}

# --- Premium Keyboards ---
def get_cancel_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🛑 TERMINATE PROCESS", callback_data="cancel_action"))
    return markup

# --- Handlers ---

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    welcome_text = (
        "⚡ **MYID AUTHENTICATION CORE**\n"
        "🌌 *DEVELOPED BY DOMINIC*\n"
        "📶 SYSTEM STATUS: ONLINE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Welcome to the high-speed MyID Session Utility. "
        "Securely authenticate and parse your data payloads.\n\n"
        "🛠 **SYSTEM COMMANDS:**\n"
        "➥ /login  - Initiate Authentication Chain\n"
        "➥ /cancel - Force Terminal Reset\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ *READY FOR COMMANDS...*"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message_handler(commands=['login'], state="*")
async def start_login(message: types.Message):
    await message.answer(
        "📱 **ENTER TARGET PHONE NUMBER:**\n"
        "Format: `09XXXXXXXXX`", 
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    await MyIDLoginSystem.waiting_phone.set()

@dp.callback_query_handler(text="cancel_action", state="*")
async def cancel_action(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.message.edit_text("❌ **PROCESS TERMINATED BY USER.**\nAll temporary cache wiped.")
    await callback_query.answer()

@dp.message_handler(state=MyIDLoginSystem.waiting_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    
    if not phone.startswith("09") or len(phone) < 9:
        return await message.reply("❌ **INVALID FORMAT.** Please provide a valid number starting with 09.")

    await state.update_data(phone=phone)
    
    status_msg = await message.answer("📡 **QUERIED NETWORK GATEWAY... PLEASE WAIT...**")
    url = f"https://apis.mytel.com.mm/myid/authen/v1.0/v2/login/action/check-account?phoneNumber={phone}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            await status_msg.edit_text(
                f"📥 **OTP DISPATCHED SUCCESSFULLY**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **Target Phone:** `{phone}`\n"
                f"🔒 **Status:** `Awaiting Verification Code`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 Please input the 6-digit OTP sent to your device:",
                parse_mode="Markdown"
            )
            await MyIDLoginSystem.waiting_otp.set()
        else:
            await status_msg.edit_text("❌ **GATEWAY REFUSED.** Account validation failed. Try again later.")
            await state.finish()
    except Exception as e:
        await status_msg.edit_text(f"⚠️ **NETWORK EXCEPTION:** `{e}`")
        await state.finish()

@dp.message_handler(state=MyIDLoginSystem.waiting_otp)
async def process_otp(message: types.Message, state: FSMContext):
    otp = message.text.strip()
    user_data = await state.get_data()
    phone = user_data.get("phone")

    validate_url = "https://apis.mytel.com.mm/myid/authen/v1.0/login/method/otp/validate-otp"
    payload = {"phoneNumber": phone, "otp": otp, "isWap": False}

    status_msg = await message.answer("🔄 **VERIFYING SECURITY TOKENS...**")

    try:
        response = requests.post(validate_url, json=payload, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            await status_msg.edit_text(
                f"🔥 **ACCESS GRANTED (Login Successful)**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 **SERVER RESPONSE DATA:**\n\n"
                f"`{response.json()}`", 
                parse_mode="Markdown"
            )
        else:
            await status_msg.edit_text("❌ **INVALID OTP TOKEN.** Verification failed. Process killed.")
    except Exception as e:
        await status_msg.edit_text(f"⚠️ **RUNTIME ERROR:** `{e}`")
    
    await state.finish()

if __name__ == '__main__':
    print("Dominic's Premium MyID System is Live.")
    executor.start_polling(dp, skip_updates=True)
