import logging
import requests
import json
import datetime
from aiogram import Bot, Dispatcher, executor, types

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔑 CREDENTIALS & CONFIG (LITMATCH CODENAME: DOMINIC ENGINE v2.1)
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
        "👋 **Welcome to Litmatch Advanced Visual Tracker Bot!**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 **အသုံးပြုနိုင်သည့် Command:**\n"
        "➡️ /check - Token အသစ်ကို Auto တောင်းပြီး Advanced Visual Report ထုတ်ရန်\n\n"
        "🌌 *Powered by Dominic Auto-Login Engine v2.1*"
    )

@dp.message_handler(commands=['check'])
async def handle_advanced_visual_check(message: types.Message):
    status_msg = await message.reply("🔑 **DOMINIC ENGINE: GENERATING NEW TOKEN...**")
    
    new_token = get_live_token()
    
    if not new_token:
        await bot.edit_message_text("🛑 **LOGIN FAILED:** Token generation rejected. Check password/username.", message.chat.id, status_msg.message_id)
        return

    await bot.edit_message_text("⚡ **TOKEN FOUND! FETCHING ADVANCED DATA...**", message.chat.id, status_msg.message_id)

    headers = {
        "User-Agent": "Easemob-SDK(Android) 4.5.3",
        "Authorization": f"Bearer {new_token}",
        "Content-Type": "application/json"
    }

    report = "🌟 **LITMATCH ADVANCED VISUAL REPORT**\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━\n"

    try:
        # ၂။ User Profile စစ်ဆေးခြင်း
        profile_url = f"{BASE_URL}/users/{LIT_USERNAME}"
        p_res = requests.get(profile_url, headers=headers)
        if p_res.status_code == 200:
            p_data = p_res.json()
            
            # 💡 Nickname Response ပုံစံသစ်အတွက် တိုးချဲ့စစ်ဆေးခြင်း
            user_info_entities = p_data.get("entities", [{}])[0]
            user_info_data = p_data.get("data", [{}])[0]
            
            nickname = user_info_entities.get("nickname") or user_info_data.get("nickname") or user_info_entities.get("username") or LIT_USERNAME
            
            activated = user_info_entities.get("activated", user_info_data.get("activated", "N/A"))
            created_timestamp = user_info_entities.get("created", user_info_data.get("created"))
            
            account_creation_date = "N/A"
            if created_timestamp:
                # Timestamp ကို ပိုဖတ်ရလွယ်ကူတဲ့ Date အဖြစ် ပြောင်းလဲခြင်း
                account_creation_date = datetime.datetime.fromtimestamp(created_timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')

            report += f"👤 **User ID:** `{LIT_USERNAME}`\n"
            report += f"🏷️ **Nickname:** `{nickname}`\n"
            report += f"📅 **Account Created:** `{account_creation_date}`\n"
            report += f"🟢 **Account Active:** `{activated}`\n"
        else:
            report += f"👤 **Profile:** 🛑 Fetch Failed (HTTP {p_res.status_code})\n"

        # ၃။ Friend List စစ်ဆေးခြင်း
        friend_url = f"{BASE_URL}/users/{LIT_USERNAME}/contacts/users"
        f_res = requests.get(friend_url, headers=HEADERS if 'HEADERS' in locals() else headers) # Handle both old/new structure
        if f_res.status_code == 200:
            f_data = f_res.json()
            friends_list = f_data.get("data", [])
            report += f"👥 **Total Friends:** `{len(friends_list)}`\n"
            if friends_list:
                preview_friends = friends_list[:5]
                report += f"📌 **Friend IDs:** `{', '.join(preview_friends)}`\n"
            else:
                report += "📌 *No friends found for this account.*\n"
        else:
            report += f"👥 **Friends:** 🛑 Fetch Failed\n"

        # ၄။ Online Status စစ်ဆေးခြင်း
        status_url = f"{BASE_URL}/users/{LIT_USERNAME}/status"
        s_res = requests.get(status_url, headers=headers)
        if s_res.status_code == 200:
            s_data = s_res.json()
            status_dict = s_data.get("data", {})
            online_state = status_dict.get(LIT_USERNAME, "offline")
            
            # Online Status ကို Visual Emoji ဖြင့် ဖော်ပြခြင်း
            visual_status = "🟢 ONLINE" if online_state.lower() == "online" else "🔴 OFFLINE"
            report += f"🌐 **Connection Status:** `{visual_status}`\n"
        else:
            report += f"🌐 **Status:** 🛑 Fetch Failed\n"

        report += "━━━━━━━━━━━━━━━━━━━━━━\n"
        report += "🌌 *Engine: Litmatch Advanced Visual Tuan*"
        
        await bot.edit_message_text(report, message.chat.id, status_msg.message_id)

    except Exception as e:
        await bot.edit_message_text(
            f"🛑 **CRITICAL ENGINE ERROR:**\n`{str(e)}`", 
            message.chat.id, status_msg.message_id
        )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
