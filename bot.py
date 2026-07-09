import logging
import requests
import json
from aiogram import Bot, Dispatcher, executor, types

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔑 TELEGRAM BOT & LITMATCH CONFIG SETUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_TOKEN = '8702294693:AAFQUh4aT3Wh5ur4XFxO5ftB_evXD_5MrFM'

# Litmatch credentials
APP_KEY = "1102190223222824#lit"
ORG_NAME, APP_NAME = APP_KEY.split("#")
REST_SERVER = "a1-sgp-ga.easemob.com" 
USER_ID = "love143872087742769"
BEARER_TOKEN = "YWMt_MlvVHsvEfGJ5puF0MkOFwC3x2A3exHpkKgjudNTjb0mnqlAcGcR8ItMGWYExFEOAwMAAAGfRFmHyTht7EBFaNAbT9IyqPh6UP9LCYx3eGSeJc5D3CITerjpNxd7DA"

BASE_URL = f"https://{REST_SERVER}/{ORG_NAME}/{APP_NAME}"
HEADERS = {
    "User-Agent": "Easemob-SDK(Android) 4.5.3",
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.MARKDOWN)
dp = Dispatcher(bot)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 COMMANDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        "👋 **Welcome to Litmatch Data Checker Bot!**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 **အသုံးပြုနိုင်သည့် Command:**\n"
        "➡️ /check - Litmatch အကောင့်ရဲ့ Live Data များကို လှမ်းစစ်ရန်\n\n"
        "Dominic Engine မှ အလိုအလျောက် REST API ဆွဲထုတ်ပေးမှာ ဖြစ်ပါတယ်ဗျာ။"
    )

@dp.message_handler(commands=['check'])
async def handle_check(message: types.Message):
    status_msg = await message.reply("⚡ **DOMINIC ENGINE: FETCHING LITMATCH DATA...**")
    
    report = "📊 **LITMATCH LIVE REPORT**\n"
    report += "━━━━━━━━━━━━━━━━━━━━\n"

    try:
        # ၁။ User Profile စစ်ဆေးခြင်း
        profile_url = f"{BASE_URL}/users/{USER_ID}"
        p_res = requests.get(profile_url, headers=HEADERS)
        if p_res.status_code == 200:
            p_data = p_res.json()
            user_info = p_data.get("entities", [{}])[0]
            nickname = user_info.get("nickname", "N/A")
            activated = user_info.get("activated", "N/A")
            report += f"👤 **User ID:** `{USER_ID}`\n"
            report += f"🏷️ **Nickname:** `{nickname}`\n"
            report += f"🟢 **Account Active:** `{activated}`\n"
        else:
            report += f"👤 **Profile:** 🛑 Fetch Failed (HTTP {p_res.status_code})\n"

        # ၂။ Friend List စစ်ဆေးခြင်း
        friend_url = f"{BASE_URL}/users/{USER_ID}/contacts/users"
        f_res = requests.get(friend_url, headers=HEADERS)
        if f_res.status_code == 200:
            f_data = f_res.json()
            friends_list = f_data.get("data", [])
            report += f"👥 **Total Friends:** `{len(friends_list)}`\n"
            if friends_list:
                # ပထမဆုံး သူငယ်ချင်း ၅ ယောက်ရဲ့ ID ကို ပြပေးရန်
                preview_friends = friends_list[:5]
                report += f"📌 **Friend IDs (Top 5):** `{', '.join(preview_friends)}`\n"
        else:
            report += f"👥 **Friends:** 🛑 Fetch Failed\n"

        # ၃။ Online Status စစ်ဆေးခြင်း
        status_url = f"{BASE_URL}/users/{USER_ID}/status"
        s_res = requests.get(status_url, headers=HEADERS)
        if s_res.status_code == 200:
            s_data = s_res.json()
            status_dict = s_data.get("data", {})
            online_state = status_dict.get(USER_ID, "offline")
            report += f"🌐 **Connection Status:** `{online_state.upper()}`\n"
        else:
            report += f"🌐 **Status:** 🛑 Fetch Failed\n"

        report += "━━━━━━━━━━━━━━━━━━━━\n"
        report += "🌌 *Engine: Litmatch REST Checker Tuan*"
        
        await bot.edit_message_text(report, message.chat.id, status_msg.message_id)

    except Exception as e:
        await bot.edit_message_text(
            f"🛑 **CRITICAL ENGINE ERROR:**\n`{str(e)}`", 
            message.chat.id, status_msg.message_id
        )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏁 RUN POLLING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
