import logging
import requests
import json
from aiogram import Bot, Dispatcher, executor, types

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔑 CREDENTIALS & CONFIG (LITMATCH CODENAME: DOMINIC ENGINE v2)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_TOKEN = '8702294693:AAFQUh4aT3Wh5ur4XFxO5ftB_evXD_5MrFM'

APP_KEY = "1102190223222824#lit"
ORG_NAME, APP_NAME = APP_KEY.split("#")
REST_SERVER = "a1-sgp-ga.easemob.com"
BASE_URL = f"https://{REST_SERVER}/{ORG_NAME}/{APP_NAME}"

# ကိုကို အသစ်ပေးလိုက်တဲ့ Login Credentials များ
LIT_USERNAME = "love144883120849408"
LIT_PASSWORD = "b5a0000d4fb032795b18ef696a9fcd80"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.MARKDOWN)
dp = Dispatcher(bot)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔑 FUNCTION: GENERATE NEW LIVE TOKEN (အလိုအလျောက် Token တောင်းပေးသည့်စနစ်)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def get_live_token():
    url = f"{BASE_URL}/token"
    headers = {
        "User-Agent": "Easemob-SDK(Android) 4.5.3",
        "Content-Type": "application/json",
        "Host": REST_SERVER
    }
    payload = {
        "grant_type": "password",
        "username": LIT_USERNAME,
        "password": LIT_PASSWORD
    }
    try:
        # POST Request ဖြင့် Token အသစ်ကို လှမ်းတောင်းခြင်း
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
        if response.status_code == 200:
            res_data = response.json()
            return res_data.get("access_token")
        else:
            return None
    except Exception as e:
        print(f"Token Generation Error: {str(e)}")
        return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 COMMAND HANDLERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        "👋 **Welcome to Litmatch Advanced Tracker Bot!**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 **အသုံးပြုနိုင်သည့် Command:**\n"
        "➡️ /check - Token အသစ်ကို Auto တောင်းပြီး Live Report ထုတ်ရန်\n\n"
        "🌌 *Powered by Dominic Auto-Login Engine*"
    )

@dp.message_handler(commands=['check'])
async def handle_advanced_check(message: types.Message):
    status_msg = await message.reply("🔑 **DOMINIC ENGINE: GENERATING NEW TOKEN & FETCHING DATA...**")
    
    # ၁။ Token အသစ်စက်စက်ကို ဆာဗာဆီက တောင်းယူခြင်း
    new_token = get_live_token()
    
    if not new_token:
        await bot.edit_message_text("🛑 **LOGIN FAILED:** Token generation rejected by Litmatch server. Check password/username.", message.chat.id, status_msg.message_id)
        return

    # Header တွင် Token အသစ်ကို တပ်ဆင်ခြင်း
    headers = {
        "User-Agent": "Easemob-SDK(Android) 4.5.3",
        "Authorization": f"Bearer {new_token}",
        "Content-Type": "application/json"
    }

    report = "📊 **LITMATCH ADVANCED LIVE REPORT**\n"
    report += "━━━━━━━━━━━━━━━━━━━━\n"

    try:
        # ၂။ User Profile စစ်ဆေးခြင်း
        profile_url = f"{BASE_URL}/users/{LIT_USERNAME}"
        p_res = requests.get(profile_url, headers=headers)
        if p_res.status_code == 200:
            p_data = p_res.json()
            user_info = p_data.get("entities", [{}])[0]
            nickname = user_info.get("nickname", "N/A")
            activated = user_info.get("activated", "N/A")
            report += f"👤 **User ID:** `{LIT_USERNAME}`\n"
            report += f"🏷️ **Nickname:** `{nickname}`\n"
            report += f"🟢 **Account Active:** `{activated}`\n"
        else:
            report += f"👤 **Profile:** 🛑 Fetch Failed (HTTP {p_res.status_code})\n"

        # ၃။ Friend List စစ်ဆေးခြင်း
        friend_url = f"{BASE_URL}/users/{LIT_USERNAME}/contacts/users"
        f_res = requests.get(friend_url, headers=headers)
        if f_res.status_code == 200:
            f_data = f_res.json()
            friends_list = f_data.get("data", [])
            report += f"👥 **Total Friends:** `{len(friends_list)}`\n"
            if friends_list:
                preview_friends = friends_list[:5]
                report += f"📌 **Friend IDs:** `{', '.join(preview_friends)}`\n"
        else:
            report += f"👥 **Friends:** 🛑 Fetch Failed\n"

        # ၄။ Online Status စစ်ဆေးခြင်း
        status_url = f"{BASE_URL}/users/{LIT_USERNAME}/status"
        s_res = requests.get(status_url, headers=headers)
        if s_res.status_code == 200:
            s_data = s_res.json()
            status_dict = s_data.get("data", {})
            online_state = status_dict.get(LIT_USERNAME, "offline")
            report += f"🌐 **Connection Status:** `{online_state.upper()}`\n"
        else:
            report += f"🌐 **Status:** 🛑 Fetch Failed\n"

        report += "━━━━━━━━━━━━━━━━━━━━\n"
        report += "🌌 *Engine: Litmatch Token & REST Master Tuan*"
        
        await bot.edit_message_text(report, message.chat.id, status_msg.message_id)

    except Exception as e:
        await bot.edit_message_text(
            f"🛑 **CRITICAL ENGINE ERROR:**\n`{str(e)}`", 
            message.chat.id, status_msg.message_id
        )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
