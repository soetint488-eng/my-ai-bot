import logging
import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔑 CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_TOKEN = '8702294693:AAHFj1uHEkpBfUVd9CTu2d7x3O_O767bxA8'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Slot API Response Standard Data
API_DATA = {
    'package_name': 'com.fsf.gfh.jhg', 
    'login_ip': 'game.zhangt999.com', 
    'port': 20000, 
    'language': 'mm', 
    'default_language': 1, 
    'region': 'mm', 
    'desc': '4-34', 
    'login_download_url': 'https://nhgkn8978.com/', 
    'login_version': '1.0.1',
    'balance': '15,500 MMK'
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎰 FUNCTION: REAL-TIME RTP & TIME SLOTS CALCULATOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def calculate_realtime_slot(pkg_name):
    current_hour = datetime.now().hour
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # နေ့ရက်နှင့် နာရီအလိုက် Seed ပေးခြင်းဖြင့် အချိန်နှင့်အမျှ Rate အလိုအလျောက် ပြောင်းလဲမည်
    random.seed(f"{pkg_name}-{today_str}-{current_hour}")
    
    current_rtp = round(random.uniform(89.0, 98.5), 2)
    start_time = f"{current_hour:02d}:00"
    end_time = f"{(current_hour + 1) % 24:02d}:00"
    lucky_slot = f"⏰ {start_time} - {end_time}"
    
    return lucky_slot, current_rtp

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 FUNCTION: BUILD SLOT REPORT & KEYBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def get_slot_payload():
    pkg_name = API_DATA.get('package_name', 'Unknown')
    download_url = API_DATA.get('login_download_url', '#')
    account_balance = API_DATA.get('balance', '0 MMK')
    
    lucky_slot, rtp_rate = calculate_realtime_slot(pkg_name)
    status_text = "🟢 အောင်မြင်သည် (နိုင်ချေ မြင့်မားသည်)" if rtp_rate > 93 else "🟡 ပုံမှန်အခြေအနေ"
    
    report = (
        "🎰 <b>DOMINIC SLOT REAL-TIME SYSTEM</b> 🎰\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Status:</b> {status_text}\n"
        f"📦 <b>Package:</b> <code>{pkg_name}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>လက်ကျန်ငွေ (Balance):</b> <code>{account_balance}</code>\n"
        f"🔥 <b>လက်ရှိအချိန် RTP Rate:</b> 🌟 <code>{rtp_rate}%</code>\n"
        f"⚡ <b>လက်ရှိကစားသင့်သည့်အချိန်:</b> {lucky_slot}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ <i>RTP နှုန်းထားသည် လက်ရှိနာရီအလိုက် အလိုအလျောက် ပြောင်းလဲနေပါသည်။</i>"
    )
    
    # Inline Buttons UI ဖန်တီးခြင်း
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🔄 Live Check Update", callback_data="refresh_slot"),
        types.InlineKeyboardButton(text="🌐 Download App", url=download_url)
    )
    
    return report, builder.as_markup()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 COMMAND: START & SLOT ENTRY POINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message(Command("start"))
@dp.message(Command("slot"))
async def handle_slot_command(message: types.Message):
    text, reply_markup = get_slot_payload()
    await message.reply(text, parse_mode="HTML", reply_markup=reply_markup)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔄 CALLBACK: REFRESH BUTTON DATA HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.callback_query(lambda c: c.data == "refresh_slot")
async def handle_refresh_callback(callback_query: types.CallbackQuery):
    text, reply_markup = get_slot_payload()
    
    try:
        await bot.edit_message_text(
            text=text,
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        # အသုံးပြုသူအား Alert တိုတိုလေးပြသခြင်း
        await callback_query.answer("📊 ဒေတာများကို Real-Time အသစ်ပြင်ဆင်ပြီးပါပြီ။")
    except Exception:
        # ဒေတာ ပြောင်းလဲမှုမရှိသေးလျှင် Error မတက်စေရန် ကာကွယ်ခြင်း
        await callback_query.answer("⚡ နောက်ဆုံးရ ဒေတာကို ပြသနေဆဲဖြစ်သည်။")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏁 RUN ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
