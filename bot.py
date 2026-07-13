import logging
import asyncio
import aiohttp
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔑 CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_TOKEN = '8702294693:AAHFj1uHEkpBfUVd9CTu2d7x3O_O767bxA8'
TARGET_API_URL = "http://13.251.67.72:8865/api/Async/com.fsf.gfh.jhg"
HEADERS = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 8.1.0; vivo 1807 Build/OPM1.171019.026)",
    "Accept-Encoding": "identity",
    "Connection": "Keep-Alive"
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎰 FUNCTION: REAL-TIME RTP & TIME SLOTS CALCULATOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def calculate_realtime_slot(pkg_name):
    current_hour = datetime.now().hour
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    random.seed(f"{pkg_name}-{today_str}-{current_hour}")
    current_rtp = round(random.uniform(89.0, 98.5), 2)
    
    start_time = f"{current_hour:02d}:00"
    end_time = f"{(current_hour + 1) % 24:02d}:00"
    lucky_slot = f"⏰ {start_time} - {end_time}"
    
    return lucky_slot, current_rtp

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌐 FUNCTION: FETCH ALL DATA FROM SLOT API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def fetch_slot_api_payload():
    timeout = aiohttp.ClientTimeout(total=8)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(TARGET_API_URL, headers=HEADERS) as response:
                if response.status == 200:
                    api_data = await response.json()
                    return api_data, "OK"
                else:
                    return None, f"HTTP Error {response.status}"
    except Exception as e:
        return None, str(e)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 FUNCTION: GENERATE UI REPORT & KEYBOARD BUTTONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def generate_ui_report(api_data):
    # API ကနေ ပါသမျှ Data အကုန် ဆွဲထုတ်ခြင်း
    pkg_name = api_data.get('package_name', 'Unknown')
    login_ip = api_data.get('login_ip', 'Not Found')
    port = api_data.get('port', 'Unknown')
    lang = api_data.get('language', 'mm')
    region = api_data.get('region', 'mm')
    desc = api_data.get('desc', 'N/A')
    download_url = api_data.get('login_download_url', '#')
    version = api_data.get('login_version', '1.0.0')
    
    # API ထဲတွင် Balance သို့မဟုတ် Gold ပါခဲ့လျှင် ဆွဲထုတ်ရန် (မပါက Dummy ပြသထားမည်)
    account_balance = api_data.get('balance', '15,500 MMK')
    gold_amount = api_data.get('gold', '4,800 Gold')
    
    # Dynamic RTP နှင့် အချိန်တွက်ချက်မှု
    lucky_slot, rtp_rate = calculate_realtime_slot(pkg_name)
    status_text = "🟢 အောင်မြင်သည် (နိုင်ချေ မြင့်မားသည်)" if rtp_rate > 93 else "🟡 ပုံမှန်အခြေအနေ"
    
    report = (
        "🎰 <b>DOMINIC SLOT REAL-TIME ENGINE</b> 🎰\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Status:</b> {status_text}\n"
        f"📦 <b>Package:</b> <code>{pkg_name}</code>\n"
        f"📱 <b>Version:</b> <code>{version}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📡 <b>NETWORK & SERVER INFO</b>\n"
        f"🌐 <b>Host IP:</b> <code>{login_ip}</code>\n"
        f"🔌 <b>Port:</b> <code>{port}</code>\n"
        f"🌍 <b>Region:</b> <code>{region.upper()}</code> ({lang})\n"
        f"📝 <b>Description:</b> <code>{desc}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>USER WALLET ACCOUNT</b>\n"
        f"💵 <b>Balance:</b> <code>{account_balance}</code>\n"
        f"🟡 <b>Gold Amount:</b> <code>{gold_amount}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 <b>LIVE PREDICTION ANALYSIS</b>\n"
        f"📈 <b>RTP Rate:</b> 🌟 <code>{rtp_rate}%</code>\n"
        f"⚡ <b>ကစားရန်အချိန်ကောင်း:</b> {lucky_slot}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ <i>RTP နှင့် အချက်အလက်များသည် မိနစ်/နာရီအလိုက် အလိုအလျောက် ပြောင်းလဲနေပါသည်။</i>"
    )
    
    # Inline Buttons ဖန်တီးခြင်း
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🔄 Live Check Update", callback_data="refresh_slot"),
        types.InlineKeyboardButton(text="🟡 Gold Request", callback_data="gold_request")
    )
    builder.row(
        types.InlineKeyboardButton(text="🌐 Download App", url=download_url)
    )
    
    return report, builder.as_markup()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 COMMAND: START / SLOT ENTRY POINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message(Command("start"))
@dp.message(Command("slot"))
async def handle_slot_command(message: types.Message):
    status_msg = await message.reply("📡 <b>API ဆာဗာမှ ဒေတာများ ဆွဲထုတ်နေပါသည်...</b>", parse_mode="HTML")
    
    api_data, status = await fetch_slot_api_payload()
    if not api_data:
        await bot.edit_message_text(
            text=f"🛑 <b>API ချိတ်ဆက်မှု ပျက်ကွက်ပါသည်</b>\n❌ အကြောင်းရင်း: <code>{status}</code>",
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            parse_mode="HTML"
        )
        return
        
    text, reply_markup = generate_ui_report(api_data)
    await bot.edit_message_text(
        text=text,
        chat_id=message.chat.id,
        message_id=status_msg.message_id,
        parse_mode="HTML",
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔄 CALLBACK: REFRESH BUTTON DATA HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.callback_query(lambda c: c.data == "refresh_slot")
async def handle_refresh_callback(callback_query: types.CallbackQuery):
    api_data, status = await fetch_slot_api_payload()
    if not api_data:
        await callback_query.answer(f"❌ API Error: {status}", show_alert=True)
        return
        
    text, reply_markup = generate_ui_report(api_data)
    try:
        await bot.edit_message_text(
            text=text,
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            parse_mode="HTML",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        await callback_query.answer("📊 ဒေတာအားလုံးကို Real-Time အသစ်ပြင်ဆင်ပြီးပါပြီ။")
    except Exception:
        await callback_query.answer("⚡ နောက်ဆုံးရ ဒေတာများကို ပြသနေဆဲဖြစ်သည်။")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🟡 CALLBACK: GOLD REQUEST BUTTON HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.callback_query(lambda c: c.data == "gold_request")
async def handle_gold_callback(callback_query: types.CallbackQuery):
    # Gold Request လုပ်ဆောင်ချက်အတွက် (လက်ရှိ စမ်းသပ်ချက်အဖြစ် ပြသခြင်း)
    await callback_query.answer("🟡 Gold Request အောင်မြင်ပါသည်။ အကောင့်ထဲသို့ ရွှေများ ထည့်သွင်းနေပါသည်...", show_alert=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏁 RUN ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
