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
from aiohttp import web

# Logging setup
logging.basicConfig(level=logging.INFO)

# --- CONFIGURATION ---
# သင့်ရဲ့ Token ကို ဒီမှာ တိုက်ရိုက်ထည့်ထားပေးပါတယ်
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
SMM_API_KEY = os.getenv("SMM_API_KEY") # Render Environment Variables ထဲမှာ ထည့်ပေးပါ
SMM_API_URL = "https://justanotherpanel.com/api/v2"

FREE_VIEWS_SERVICE_ID = int(os.getenv("FREE_VIEWS_SERVICE_ID", "1")) 
FREE_LIKES_SERVICE_ID = int(os.getenv("FREE_LIKES_SERVICE_ID", "2"))

DAILY_VIEWS_LIMIT = 100
DAILY_LIKES_LIMIT = 10
DB_PATH = "bot_data.db"

# --- RENDER WEB SERVER (To prevent status 1 error) ---
async def handle(request):
    return web.Response(text="TikTok Boost Bot is Running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server started on port {port}")

# --- DATABASE SETUP ---
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

# --- BOT HANDLERS ---
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class OrderStates(StatesGroup):
    waiting_for_link = State()

def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🎁 Free Views (100)")
    builder.button(text="💝 Free Likes (10)")
    builder.button(text="👤 My Profile")
    builder.button(text="📊 Status")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def smm_api_call(action, **kwargs):
    payload = {"key": SMM_API_KEY, "action": action}
    payload.update(kwargs)
    try:
        response = requests.post(SMM_API_URL, data=payload)
        return response.json()
    except:
        return {"error": "Connection Failed"}

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    init_db()
    await message.answer("👋 *TikTok Free Booster* မှ ကြိုဆိုပါတယ်ဗျ!\nအောက်က Menu ကို သုံးနိုင်ပါပြီ။", parse_mode="Markdown", reply_markup=main_menu())

@dp.message(F.text.contains("Free Views"))
async def free_views(message: types.Message, state: FSMContext):
    views, _ = get_user_data(message.from_user.id)
    if views >= DAILY_VIEWS_LIMIT:
        await message.answer("❌ ဒီနေ့အတွက် Limit ပြည့်သွားပါပြီ။")
        return
    await state.update_data(service_id=FREE_VIEWS_SERVICE_ID, amount=DAILY_VIEWS_LIMIT, type="views")
    await message.answer("🔗 TikTok Video Link ပို့ပေးပါဗျ။")
    await state.set_state(OrderStates.waiting_for_link)

@dp.message(F.text.contains("Free Likes"))
async def free_likes(message: types.Message, state: FSMContext):
    _, likes = get_user_data(message.from_user.id)
    if likes >= DAILY_LIKES_LIMIT:
        await message.answer("❌ ဒီနေ့အတွက် Limit ပြည့်သွားပါပြီ။")
        return
    await state.update_data(service_id=FREE_LIKES_SERVICE_ID, amount=DAILY_LIKES_LIMIT, type="likes")
    await message.answer("🔗 TikTok Video Link ပို့ပေးပါဗျ။")
    await state.set_state(OrderStates.waiting_for_link)

@dp.message(OrderStates.waiting_for_link)
async def process_link(message: types.Message, state: FSMContext):
    if "tiktok.com" not in message.text:
        await message.answer("❌ TikTok Link မှားနေပါတယ်ဗျ။")
        return
    data = await state.get_data()
    res = smm_api_call("add", service=data['service_id'], link=message.text, quantity=data['amount'])
    if "order" in res:
        if data['type'] == "views": update_user_usage(message.from_user.id, views_add=data['amount'])
        else: update_user_usage(message.from_user.id, likes_add=data['amount'])
        await message.answer(f"✅ Order တင်ပြီးပါပြီ! ID: `{res['order']}`", parse_mode="Markdown")
    else:
        await message.answer(f"❌ API Error: {res.get('error')}")
    await state.clear()

@dp.message(F.text == "👤 My Profile")
async def profile(message: types.Message):
    v, l = get_user_data(message.from_user.id)
    await message.answer(f"📊 *သင့်အသုံးပြုမှု*\nViews: {v}/{DAILY_VIEWS_LIMIT}\nLikes: {l}/{DAILY_LIKES_LIMIT}", parse_mode="Markdown")

async def main():
    init_db()
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
