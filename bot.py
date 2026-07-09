import logging
import requests
import json
import datetime
from aiogram import Bot, Dispatcher, executor, types

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔑 CREDENTIALS & CONFIG (DOMINIC ENGINE ULTIMATE v3.0)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_TOKEN = '8702294693:AAFQUh4aT3Wh5ur4XFxO5ftB_evXD_5MrFM'

APP_KEY = "1102190223222824#lit"
ORG_NAME, APP_NAME = APP_KEY.split("#")
REST_SERVER = "a1-sgp-ga.easemob.com"
BASE_URL = f"https://{REST_SERVER}/{ORG_NAME}/{APP_NAME}"

LIT_USERNAME = "love144883120849408"
LIT_PASSWORD = "b5a0000d4fb032795b18ef696a9fcd80"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.MARKDOWN)
dp = Dispatcher(bot)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔑 FUNCTION: GENERATE LIVE TOKEN
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
            return response.json().get("access_token")
        return None
    except Exception as e:
        print(f"Token Error: {str(e)}")
        return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 COMMAND HANDLERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        "🌌 **Dominic Ultimate Litmatch Tracker Bot v3.0**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 **အသုံးပြုနိုင်သည့် Command:**\n"
        "➡️ /check - အကောင့်ရဲ့ Data အကုန်လုံးကို Live ဆွဲထုတ်ရန်\n\n"
        "All-in-One Engine ဖြင့် စစ်ဆေးပေးသွားမှာ ဖြစ်ပါတယ်ဗျာ။"
    )

@dp.message_handler(commands=['check'])
async def handle_ultimate_check(message: types.Message):
    status_msg = await message.reply("🔑 **DOMINIC ENGINE: AUTOLOGIN & GENERATING TOKEN...**")
    
    new_token = get_live_token()
    if not new_token:
        await bot.edit_message_text("🛑 **LOGIN FAILED:** Token generation rejected.", message.chat.id, status_msg.message_id)
        return

    await bot.edit_message_text("⚡ **TOKEN ACTIVE! EXTRACTING ALL DATA FIELDS...**", message.chat.id, status_msg.message_id)

    headers = {
        "User-Agent": "Easemob-SDK(Android) 4.5.3",
        "Authorization": f"Bearer {new_token}",
        "Content-Type": "application/json"
    }

    report = "🚀 **DOMINIC ULTIMATE LITMATCH REPORT**\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━\n"

    try:
        # ၁။ User Profile & Active Status
        profile_url = f"{BASE_URL}/users/{LIT_USERNAME}"
        p_res = requests.get(profile_url, headers=headers)
        if p_res.status_code == 200:
            p_data = p_res.json()
            user_info_entities = p_data.get("entities", [{}])[0]
            user_info_data = p_data.get("data", [{}])[0]
            nickname = user_info_entities.get("nickname") or user_info_data.get("nickname") or LIT_USERNAME
            created_timestamp = user_info_entities.get("created", user_info_data.get("created"))
            
            account_creation_date = datetime.datetime.fromtimestamp(created_timestamp/1000).strftime('%Y-%m-%d %H:%M:%S') if created_timestamp else "N/A"
            report += f"👤 **User ID:** `{LIT_USERNAME}`\n"
            report += f"🏷️ **Nickname:** `{nickname}`\n"
            report += f"📅 **Account Created:** `{account_creation_date}`\n"
        else:
            report += "👤 **Profile:** 🛑 Fetch Failed\n"

        # ၂။ Connection Live Status
        status_url = f"{BASE_URL}/users/{LIT_USERNAME}/status"
        s_res = requests.get(status_url, headers=headers)
        if s_res.status_code == 200:
            online_state = s_res.json().get("data", {}).get(LIT_USERNAME, "offline")
            visual_status = "🟢 ONLINE" if online_state.lower() == "online" else "🔴 OFFLINE"
            report += f"🌐 **Live Connection:** `{visual_status}`\n"
        else:
            report += "🌐 **Live Connection:** 🛑 Fetch Failed\n"

        report += "━━━━━━━━━━━━━━━━━━━━━━\n"

        # ၃။ Friends & Following Counts
        f_res = requests.get(f"{BASE_URL}/users/{LIT_USERNAME}/contacts/users", headers=headers)
        fol_res = requests.get(f"{BASE_URL}/users/{LIT_USERNAME}/followings", headers=headers)
        
        friends_list = f_res.json().get("data", []) if f_res.status_code == 200 else []
        fol_data = fol_res.json() if fol_res.status_code == 200 else {}
        following_list = fol_data.get("data", fol_data.get("entities", []))

        report += f"👥 **Friends (Mutual):** `{len(friends_list)}`\n"
        report += f"❤️ **Following:** `{len(following_list)}`\n"

        # ၄။ Unread / Offline Messages Count
        unread_url = f"{BASE_URL}/users/{LIT_USERNAME}/offline_msg_count"
        un_res = requests.get(unread_url, headers=headers)
        if un_res.status_code == 200:
            unread_count = un_res.json().get("data", {}).get(LIT_USERNAME, 0)
            report += f"📥 **Unread Messages:** `{unread_count} စောင်`\n"
        else:
            report += "📥 **Unread Messages:** 🛑 Fetch Failed\n"

        # ၅။ Joined Chat Rooms / Groups
        group_url = f"{BASE_URL}/users/{LIT_USERNAME}/joined_chatgroups"
        g_res = requests.get(group_url, headers=headers)
        if g_res.status_code == 200:
            groups_list = g_res.json().get("data", [])
            report += f"💬 **Joined Groups:** `{len(groups_list)} ခု`\n"
        else:
            report += "💬 **Joined Groups:** 🛑 Fetch Failed\n"

        # ၆။ Blacklist (Blocks) Count
        block_url = f"{BASE_URL}/users/{LIT_USERNAME}/blocks/users"
        b_res = requests.get(block_url, headers=headers)
        if b_res.status_code == 200:
            block_list = b_res.json().get("data", [])
            report += f"🚫 **Blacklisted Users:** `{len(block_list)} ယောက်`\n"
        else:
            report += "🚫 **Blacklisted Users:** 🛑 Fetch Failed\n"

        report += "━━━━━━━━━━━━━━━━━━━━━━\n"
        report += "🌌 *Engine: Dominic Ultimate Monitor System*"
        
        await bot.edit_message_text(report, message.chat.id, status_msg.message_id)

    except Exception as e:
        await bot.edit_message_text(f"🛑 **ENGINE ERROR:**\n`{str(e)}`", message.chat.id, status_msg.message_id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
