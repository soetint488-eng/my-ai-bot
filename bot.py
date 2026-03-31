import os
import logging
import asyncio
import sqlite3
import requests
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)

# Configuration
API_TOKEN = os.getenv("8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI")
SMM_API_KEY = os.getenv("SMM_API_KEY")
SMM_API_URL = "https://justanotherpanel.com/api/v2"

# Free Service IDs (Example IDs - User should update these with actual Free or Cheap IDs)
FREE_VIEWS_SERVICE_ID = int(os.getenv("FREE_VIEWS_SERVICE_ID", 1)) 
FREE_LIKES_SERVICE_ID = int(os.getenv("FREE_LIKES_SERVICE_ID", 2))

# Daily Limits
DAILY_VIEWS_LIMIT = 100
DAILY_LIKES_LIMIT = 10

# Database setup
DB_PATH = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            views_today INTEGER DEFAULT 0,
            likes_today INTEGER DEFAULT 0,
            last_reset TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_user_data(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT views_today, likes_today, last_reset FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    if row:
        views, likes, last_reset = row
        if last_reset != today:
            # Reset daily limits
            cursor.execute("UPDATE users SET views_today = 0, likes_today = 0, last_reset = ? WHERE user_id = ?", (today, user_id))
            conn.commit()
            views, likes = 0, 0
    else:
        cursor.execute("INSERT INTO users (user_id, views_today, likes_today, last_reset) VALUES (?, 0, 0, ?)", (user_id, today))
        conn.commit()
        views, likes = 0, 0
        
    conn.close()
    return views, likes

def update_user_usage(user_id, views_add=0, likes_add=0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET views_today = views_today + ?, likes_today = likes_today + ? WHERE user_id = ?", (views_add, likes_add, user_id))
    conn.commit()
    conn.close()

# Bot and Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# States
class OrderStates(StatesGroup):
    waiting_for_link = State()

# Keyboards
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🎁 Get Free Views (100/day)")
    builder.button(text="💝 Get Free Likes (10/day)")
    builder.button(text="📊 Check Status")
    builder.button(text="👤 My Profile")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# SMM API Wrapper
def smm_api_call(action, **kwargs):
    payload = {"key": SMM_API_KEY, "action": action}
    payload.update(kwargs)
    try:
        response = requests.post(SMM_API_URL, data=payload)
        return response.json()
    except Exception as e:
        logging.error(f"API Error: {e}")
        return {"error": "API Connection Failed"}

# Handlers
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    init_db()
    welcome_text = (
        "👋 *Welcome to Free TikTok Boost Bot!*\n\n"
        "I provide a limited amount of FREE TikTok views and likes every day!\n\n"
        "✅ *Daily Limits:*\n"
        f"• Views: {DAILY_VIEWS_LIMIT} per day\n"
        f"• Likes: {DAILY_LIKES_LIMIT} per day\n\n"
        "Select a service below to start boosting!"
    )
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=main_menu())

@dp.message(F.text.contains("Free Views"))
async def free_views(message: types.Message, state: FSMContext):
    views, _ = get_user_data(message.from_user.id)
    if views >= DAILY_VIEWS_LIMIT:
        await message.answer("❌ You have reached your daily limit for Free Views. Please try again tomorrow!")
        return
    
    await state.update_data(service_id=FREE_VIEWS_SERVICE_ID, amount=DAILY_VIEWS_LIMIT, type="views")
    await message.answer("🔗 Please send your TikTok video link:")
    await state.set_state(OrderStates.waiting_for_link)

@dp.message(F.text.contains("Free Likes"))
async def free_likes(message: types.Message, state: FSMContext):
    _, likes = get_user_data(message.from_user.id)
    if likes >= DAILY_LIKES_LIMIT:
        await message.answer("❌ You have reached your daily limit for Free Likes. Please try again tomorrow!")
        return
    
    await state.update_data(service_id=FREE_LIKES_SERVICE_ID, amount=DAILY_LIKES_LIMIT, type="likes")
    await message.answer("🔗 Please send your TikTok video link:")
    await state.set_state(OrderStates.waiting_for_link)

@dp.message(OrderStates.waiting_for_link)
async def process_link(message: types.Message, state: FSMContext):
    if "tiktok.com" not in message.text:
        await message.answer("❌ Invalid TikTok link. Please try again.")
        return
    
    data = await state.get_data()
    service_id = data['service_id']
    amount = data['amount']
    service_type = data['type']
    
    await message.answer(f"⏳ Processing your free {service_type}...")
    
    # Call SMM API
    result = smm_api_call("add", service=service_id, link=message.text, quantity=amount)
    
    if "order" in result:
        if service_type == "views":
            update_user_usage(message.from_user.id, views_add=amount)
        else:
            update_user_usage(message.from_user.id, likes_add=amount)
            
        await message.answer(
            f"✅ *Order Placed!*\n\nID: `{result['order']}`\n"
            f"Service: Free TikTok {service_type.capitalize()}\n"
            "Status: Pending\n\n"
            "Check back tomorrow for more free boosts!",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
    else:
        await message.answer(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    await state.clear()

@dp.message(F.text == "👤 My Profile")
async def my_profile(message: types.Message):
    views, likes = get_user_data(message.from_user.id)
    profile_text = (
        "👤 *Your Profile*\n\n"
        f"🆔 User ID: `{message.from_user.id}`\n"
        f"📊 Views Used Today: {views}/{DAILY_VIEWS_LIMIT}\n"
        f"❤️ Likes Used Today: {likes}/{DAILY_LIKES_LIMIT}\n\n"
        "Limits reset every 24 hours."
    )
    await message.answer(profile_text, parse_mode="Markdown")

@dp.message(F.text == "📊 Check Status")
async def check_status_prompt(message: types.Message):
    await message.answer("🔍 Please send your Order ID:")

@dp.message(F.text.isdigit())
async def process_status_check(message: types.Message):
    result = smm_api_call("status", order=message.text)
    if "status" in result:
        await message.answer(f"📋 Order ID: {message.text}\nStatus: {result['status']}")
    else:
        await message.answer("❌ Order not found.")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
