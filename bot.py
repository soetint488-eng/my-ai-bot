import logging
import requests
import json
import datetime
from aiogram import Bot, Dispatcher, executor, types

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔑 CREDENTIALS & CONFIG (DOMINIC ENGINE ULTIMATE v4.0)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_TOKEN = '8702294693:AAFQUh4aT3Wh5ur4XFxO5ftB_evXD_5MrFM'

APP_KEY = "1102190223222824#lit"
ORG_NAME, APP_NAME = APP_KEY.split("#")
REST_SERVER = "a1-sgp-ga.easemob.com"
BASE_URL = f"https://{REST_SERVER}/{ORG_NAME}/{APP_NAME}"

LIT_USERNAME = "love144883120849408"
LIT_PASSWORD = "b5a0000d4fb032795b18ef696a9fcd80"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode="HTML") # HTML mode အားလုံးအတွက် သတ်မှတ်သည်
dp = Dispatcher(bot)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔑 FUNCTION: GENERATE LIVE TOKEN (Auto-Login Engine)
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
# 🚀 COMMAND: START
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        "🌌 <b>Dominic Ultimate Litmatch Tracker Bot v4.0</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 <b>အသုံးပြုနိုင်သည့် Command များ:</b>\n"
        "➡️ /check - အကောင့်ရဲ့ Data နှင့် Block ထားသူများနာမည် Live ဆွဲထုတ်ရန်\n"
        "➡️ /join [Party_ID] - သတ်မှတ်ထားသော Party ခန်းထဲသို့ Auto-Join ဝင်ရန်\n\n"
        "All-in-One HTML Engine ဖြင့် စစ်ဆေးမောင်းနှင်ပေးထားပါတယ်ဗျာ။",
        parse_mode="HTML"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 COMMAND: DATA LIVE CHECK + BLACKLIST NICKNAMES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['check'])
async def handle_ultimate_check(message: types.Message):
    status_msg = await message.reply("🔑 <b>DOMINIC ENGINE: AUTOLOGIN & GENERATING TOKEN...</b>", parse_mode="HTML")
    
    new_token = get_live_token()
    if not new_token:
        await bot.edit_message_text("🛑 <b>LOGIN FAILED:</b> Token generation rejected.", message.chat.id, status_msg.message_id, parse_mode="HTML")
        return

    await bot.edit_message_text("⚡ <b>TOKEN ACTIVE! EXTRACTING ALL DATA FIELDS...</b>", message.chat.id, status_msg.message_id, parse_mode="HTML")

    headers = {
        "User-Agent": "Easemob-SDK(Android) 4.5.3",
        "Authorization": f"Bearer {new_token}",
        "Content-Type": "application/json"
    }

    report = "🚀 <b>DOMINIC ULTIMATE LITMATCH REPORT</b>\n"
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
            report += f"👤 <b>User ID:</b> <code>{LIT_USERNAME}</code>\n"
            report += f"🏷️ <b>Nickname:</b> <code>{nickname}</code>\n"
            report += f"📅 <b>Account Created:</b> <code>{account_creation_date}</code>\n"
        else:
            report += "👤 <b>Profile:</b> 🛑 Fetch Failed\n"

        # ၂။ Connection Live Status
        status_url = f"{BASE_URL}/users/{LIT_USERNAME}/status"
        s_res = requests.get(status_url, headers=headers)
        if s_res.status_code == 200:
            online_state = s_res.json().get("data", {}).get(LIT_USERNAME, "offline")
            visual_status = "🟢 ONLINE" if online_state.lower() == "online" else "🔴 OFFLINE"
            report += f"🌐 <b>Live Connection:</b> <code>{visual_status}</code>\n"
        else:
            report += "🌐 <b>Live Connection:</b> 🛑 Fetch Failed\n"

        report += "━━━━━━━━━━━━━━━━━━━━━━\n"

        # ၃။ Friends & Following Counts
        f_res = requests.get(f"{BASE_URL}/users/{LIT_USERNAME}/contacts/users", headers=headers)
        fol_res = requests.get(f"{BASE_URL}/users/{LIT_USERNAME}/followings", headers=headers)
        
        friends_list = f_res.json().get("data", []) if f_res.status_code == 200 else []
        fol_data = fol_res.json() if fol_res.status_code == 200 else {}
        following_list = fol_data.get("data", fol_data.get("entities", []))

        report += f"👥 <b>Friends (Mutual):</b> <code>{len(friends_list)}</code>\n"
        report += f"❤️ <b>Following:</b> <code>{len(following_list)}</code>\n"

        # ၄။ Unread / Offline Messages Count
        unread_url = f"{BASE_URL}/users/{LIT_USERNAME}/offline_msg_count"
        un_res = requests.get(unread_url, headers=headers)
        if un_res.status_code == 200:
            unread_count = un_res.json().get("data", {}).get(LIT_USERNAME, 0)
            report += f"📥 <b>Unread Messages:</b> <code>{unread_count} စောင်</code>\n"
        else:
            report += "📥 <b>Unread Messages:</b> 🛑 Fetch Failed\n"

        # ၅။ Joined Chat Rooms / Groups
        group_url = f"{BASE_URL}/users/{LIT_USERNAME}/joined_chatgroups"
        g_res = requests.get(group_url, headers=headers)
        if g_res.status_code == 200:
            groups_list = g_res.json().get("data", [])
            report += f"💬 <b>Joined Groups:</b> <code>{len(groups_list)} ခု</code>\n"
        else:
            report += "💬 <b>Joined Groups:</b> 🛑 Fetch Failed\n"

        # ၆။ Blacklist (Blocks) Count + **🔥 Live Nickname Resolver**
        block_url = f"{BASE_URL}/users/{LIT_USERNAME}/blocks/users"
        b_res = requests.get(block_url, headers=headers)
        if b_res.status_code == 200:
            block_list = b_res.json().get("data", [])
            report += f"🚫 <b>Blacklisted Users:</b> <code>{len(block_list)} ယောက်</code>\n"
            
            if block_list:
                report += "📌 <b>Block ထားသူများစာရင်း:</b>\n"
                # Block ထားတဲ့သူတစ်ယောက်ချင်းစီရဲ့ Nickname ကို Live လိုက်ဆွဲခြင်း
                for block_id in block_list:
                    b_profile_url = f"{BASE_URL}/users/{block_id}"
                    b_prof_res = requests.get(b_profile_url, headers=headers)
                    if b_prof_res.status_code == 200:
                        bp_data = b_prof_res.json()
                        bp_entities = bp_data.get("entities", [{}])[0]
                        bp_data_field = bp_data.get("data", [{}])[0]
                        b_nickname = bp_entities.get("nickname") or bp_data_field.get("nickname") or "Unknown"
                        report += f"• <code>{block_id}</code> - <b>{b_nickname}</b>\n"
                    else:
                        report += f"• <code>{block_id}</code> - (Fetch Failed)\n"
        else:
            report += "🚫 <b>Blacklisted Users:</b> 🛑 Fetch Failed\n"

        report += "━━━━━━━━━━━━━━━━━━━━━━\n"
        report += "🌌 <i>Engine: Dominic Ultimate Monitor System</i>"
        
        await bot.edit_message_text(report, message.chat.id, status_msg.message_id, parse_mode="HTML")

    except Exception as e:
        await bot.edit_message_text(f"🛑 <b>ENGINE ERROR:</b>\n<code>{str(e)}</code>", message.chat.id, status_msg.message_id, parse_mode="HTML")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎪 COMMAND: AUTO JOIN PARTY ROOM (HTML Parser Fixed)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['join'])
async def handle_join_party(message: types.Message):
    args = message.get_args()
    if not args:
        await message.reply("❌ <b>ကျေးဇူးပြု၍ Party ID ထည့်ပေးပါဗျာ။</b>\nဥပမာ- <code>/join 239487529</code>", parse_mode="HTML")
        return

    party_id = args.strip()
    status_msg = await message.reply(f"🎪 <b>DOMINIC ENGINE: ATTEMPTING TO JOIN PARTY [{party_id}]...</b>", parse_mode="HTML")

    new_token = get_live_token()
    if not new_token:
        await bot.edit_message_text("🛑 <b>TOKEN ERROR:</b> Auto-login failed.", message.chat.id, status_msg.message_id, parse_mode="HTML")
        return

    join_url = f"{BASE_URL}/chatgroups/{party_id}/users/{LIT_USERNAME}"
    
    headers = {
        "User-Agent": "Easemob-SDK(Android) 4.5.3",
        "Authorization": f"Bearer {new_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(join_url, headers=headers, timeout=15)
        
        if response.status_code in [200, 201]:
            await bot.edit_message_text(
                f"🎉 <b>PARTY JOIN SUCCESS!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>Account:</b> <code>{LIT_USERNAME}</code>\n"
                f"🎪 <b>Joined Party ID:</b> <code>{party_id}</code>\n"
                f"🟢 <b>Status:</b> အခန်းထဲသို့ အောင်မြင်စွာ ရောက်ရှိသွားပါပြီ။\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🌌 <i>Engine: Dominic Room Injector</i>",
                message.chat.id, status_msg.message_id, parse_mode="HTML"
            )
        else:
            await bot.edit_message_text(
                f"🛑 <b>PARTY JOIN FAILED!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"❌ <b>HTTP Error:</b> <code>{response.status_code}</code>\n"
                f"📝 <b>Reason:</b> <pre>{response.text}</pre>\n"
                f"💡 <i>Note: Party ID မှားယွင်းနေခြင်း သို့မဟုတ် Room Full ဖြစ်နေခြင်း ဖြစ်နိုင်ပါသည်။</i>",
                message.chat.id, status_msg.message_id, parse_mode="HTML"
            )

    except Exception as e:
        await bot.edit_message_text(
            f"🛑 <b>INJECTOR CRITICAL ERROR:</b>\n<code>{str(e)}</code>", 
            message.chat.id, status_msg.message_id, parse_mode="HTML"
        )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏁 RUN ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
