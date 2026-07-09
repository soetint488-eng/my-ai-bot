import logging
import requests
import json
import datetime
from aiogram import Bot, Dispatcher, executor, types

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔑 CREDENTIALS & CONFIG (DOMINIC ENGINE ULTIMATE v5.0)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_TOKEN = '8702294693:AAFQUh4aT3Wh5ur4XFxO5ftB_evXD_5MrFM'

APP_KEY = "1102190223222824#lit"
ORG_NAME, APP_NAME = APP_KEY.split("#")
REST_SERVER = "a1-sgp-ga.easemob.com"
BASE_URL = f"https://{REST_SERVER}/{ORG_NAME}/{APP_NAME}"

LIT_USERNAME = "love144883120849408"
LIT_PASSWORD = "b5a0000d4fb032795b18ef696a9fcd80"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode="HTML")
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
        "🌌 <b>Dominic Ultimate Litmatch Messenger Bot v5.0</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 <b>အသုံးပြုနိုင်သည့် Command များ:</b>\n"
        "➡️ /check - အကောင့်အခြေအနေနှင့် Block စာရင်း စစ်ရန်\n"
        "➡️ /messages - မဖတ်ရသေးသော မက်ဆေ့ခ်ျများနှင့် ပို့သူကို Live ဖတ်ရန်\n"
        "➡️ /reply [User_ID] [စာသား] - သတ်မှတ်ထားသောသူထံသို့ စာလှမ်းပြန်ရန်\n"
        "➡️ /join [Party_ID] - Party ခန်းဝင်ရန် (Admin Permission လိုအပ်နိုင်ပါသည်)\n\n"
        "HTML Chat Engine ဖြင့် အဆင်သင့် မောင်းနှင်ထားပါတယ်ဗျာ။",
        parse_mode="HTML"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📩 COMMAND: FETCH UNREAD MESSAGES (စာဝင်စစ်သည့်စနစ်)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['messages'])
async def handle_fetch_messages(message: types.Message):
    status_msg = await message.reply("📥 <b>DOMINIC MESSENGER: FETCHING OFFLINE MESSAGES...</b>", parse_mode="HTML")
    
    new_token = get_live_token()
    if not new_token:
        await bot.edit_message_text("🛑 <b>TOKEN ERROR:</b> Sync failed.", message.chat.id, status_msg.message_id, parse_mode="HTML")
        return

    headers = {
        "User-Agent": "Easemob-SDK(Android) 4.5.3",
        "Authorization": f"Bearer {new_token}",
        "Content-Type": "application/json"
    }

    # အကောင့်ထဲက Offline Messages (မဖတ်ရသေးသောစာများ) ကို လှမ်းဆွဲသည့် URL
    msg_url = f"{BASE_URL}/users/{LIT_USERNAME}/offline_msg_count"
    
    try:
        res = requests.get(msg_url, headers=headers, timeout=15)
        if res.status_code == 200:
            count_data = res.json().get("data", {})
            unread_count = count_data.get(LIT_USERNAME, 0)
            
            msg_report = "📥 <b>LITMATCH LIVE MESSAGES REPORT</b>\n"
            msg_report += "━━━━━━━━━━━━━━━━━━━━━━\n"
            msg_report += f"📩 <b>မဖတ်ရသေးသော စာစုစုပေါင်း:</b> <code>{unread_count} စောင်</code>\n\n"
            
            if unread_count > 0:
                # မဖတ်ရသေးတဲ့စာရှိရင် သက်ဆိုင်ရာ စကားပြောခန်း သို့မဟုတ် စာပို့ထားသူ ID စာရင်းကိုပါ ထပ်မံစစ်ဆေးခြင်း
                msg_report += "📌 <b>နောက်ဆုံးဝင်ထားသော စာများနှင့် ပို့သူများ:</b>\n"
                
                # Easemob User Chat History metadata လမ်းကြောင်းမှ ပို့သူများကို စစ်ဆေးခြင်း
                history_url = f"{BASE_URL}/users/{LIT_USERNAME}/user_channels"
                h_res = requests.get(history_url, headers=headers, timeout=15)
                
                if h_res.status_code == 200:
                    channels = h_res.json().get("data", [])
                    active_chats = 0
                    for chat in channels:
                        from_user = chat.get("meta", {}).get("last_msg", {}).get("from", "Unknown")
                        msg_body = chat.get("meta", {}).get("last_msg", {}).get("payload", {}).get("bodies", [{}])[0].get("msg", "(ပုံ သို့မဟုတ် အသံဖိုင်ဖြစ်နိုင်ပါသည်)")
                        
                        if from_user != LIT_USERNAME and from_user != "Unknown":
                            active_chats += 1
                            msg_report += f"👤 <b>From ID:</b> <code>{from_user}</code>\n"
                            msg_report += f"💬 <b>Message:</b> <code>{msg_body}</code>\n"
                            msg_report += f"✍️ <i>စာပြန်ရန်:</i> <code>/reply {from_user} [စာသား]</code>\n"
                            msg_report += "──────────────────\n"
                    
                    if active_chats == 0:
                        msg_report += "<i>(စာစောင်အရေအတွက် ရှိသော်လည်း စာသားအကြမ်းများကို လောလောဆယ် ဆွဲမရသေးပါ။)</i>\n"
                else:
                    msg_report += "⚠️ <i>ပို့သူအသေးစိတ်စာရင်းကို လှမ်းယူ၍မရပါ။</i>\n"
            else:
                msg_report += "✨ <b>လက်ရှိမှာ မဖတ်ရသေးတဲ့ စာအသစ် လုံးဝမရှိသေးပါဘူး ကိုကို။</b>\n"
                
            msg_report += "━━━━━━━━━━━━━━━━━━━━━━\n"
            msg_report += "🌌 <i>Engine: Dominic Live Message Synchronizer</i>"
            await bot.edit_message_text(msg_report, message.chat.id, status_msg.message_id, parse_mode="HTML")
        else:
            await bot.edit_message_text(f"🛑 <b>FETCH FAILED:</b> HTTP {res.status_code}", message.chat.id, status_msg.message_id, parse_mode="HTML")
            
    except Exception as e:
        await bot.edit_message_text(f"🛑 <b>MESSENGER ERROR:</b>\n<code>{str(e)}</code>", message.chat.id, status_msg.message_id, parse_mode="HTML")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✍️ COMMAND: REPLY / SEND MESSAGE (Bot ထဲမှ စာလှမ်းပြန်သည့်စနစ်)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['reply'])
async def handle_send_reply(message: types.Message):
    args = message.get_args()
    if not args or len(args.split()) < 2:
        await message.reply("❌ <b>အသုံးပြုပုံ မှားယွင်းနေပါသည်။</b>\nဥပမာ- <code>/reply [Target_User_ID] [ပြန်ချင်တဲ့စာသား]</code>\n<i>(ဥပမာ- /reply love123456 ဟဲလို ကိုကိုပါ)</i>", parse_mode="HTML")
        return

    # ID နှင့် စာသားကို ခွဲထုတ်ခြင်း
    parts = args.split(maxsplit=1)
    target_id = parts[0].strip()
    reply_text = parts[1].strip()

    status_msg = await message.reply(f"🚀 <b>DOMINIC MESSENGER: SENDING MESSAGE TO [{target_id}]...</b>", parse_mode="HTML")

    new_token = get_live_token()
    if not new_token:
        await bot.edit_message_text("🛑 <b>TOKEN ERROR:</b> Auto-login failed.", message.chat.id, status_msg.message_id, parse_mode="HTML")
        return

    # Easemob REST API Message Sending URL
    send_msg_url = f"{BASE_URL}/messages"
    
    headers = {
        "User-Agent": "Easemob-SDK(Android) 4.5.3",
        "Authorization": f"Bearer {new_token}",
        "Content-Type": "application/json"
    }

    # စာသားပေးပို့ရန် Easemob standard payload ပုံစံ
    payload = {
        "target_type": "users",
        "target": [target_id],
        "msg": {
            "type": "txt",
            "msg": reply_text
        },
        "from": LIT_USERNAME
    }

    try:
        response = requests.post(send_msg_url, headers=headers, data=json.dumps(payload), timeout=15)
        
        if response.status_code in [200, 201]:
            await bot.edit_message_text(
                f"🚀 <b>MESSAGE SENT SUCCESS!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📤 <b>To ID:</b> <code>{target_id}</code>\n"
                f"💬 <b>Message Body:</b> <code>{reply_text}</code>\n"
                f"🟢 <b>Status:</b> စာသားကို Litmatch ဆာဗာဆီသို့ အောင်မြင်စွာ ပို့လွှတ်ပြီးပါပြီ။\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🌌 <i>Engine: Dominic Message Injector</i>",
                message.chat.id, status_msg.message_id, parse_mode="HTML"
            )
        else:
            await bot.edit_message_text(
                f"🛑 <b>MESSAGE SEND FAILED!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"❌ <b>HTTP Error:</b> <code>{response.status_code}</code>\n"
                f"📝 <b>Reason:</b> <pre>{response.text}</pre>",
                message.chat.id, status_msg.message_id, parse_mode="HTML"
            )

    except Exception as e:
        await bot.edit_message_text(f"🛑 <b>MESSENGER CRITICAL ERROR:</b>\n<code>{str(e)}</code>", message.chat.id, status_msg.message_id, parse_mode="HTML")

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

    headers = {
        "User-Agent": "Easemob-SDK(Android) 4.5.3",
        "Authorization": f"Bearer {new_token}",
        "Content-Type": "application/json"
    }

    report = "🚀 <b>DOMINIC ULTIMATE LITMATCH REPORT</b>\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━\n"

    try:
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

        status_url = f"{BASE_URL}/users/{LIT_USERNAME}/status"
        s_res = requests.get(status_url, headers=headers)
        if s_res.status_code == 200:
            online_state = s_res.json().get("data", {}).get(LIT_USERNAME, "offline")
            visual_status = "🟢 ONLINE" if online_state.lower() == "online" else "🔴 OFFLINE"
            report += f"🌐 <b>Live Connection:</b> <code>{visual_status}</code>\n"

        report += "━━━━━━━━━━━━━━━━━━━━━━\n"
        f_res = requests.get(f"{BASE_URL}/users/{LIT_USERNAME}/contacts/users", headers=headers)
        fol_res = requests.get(f"{BASE_URL}/users/{LIT_USERNAME}/followings", headers=headers)
        friends_list = f_res.json().get("data", []) if f_res.status_code == 200 else []
        following_list = fol_res.json().get("data", fol_res.json().get("entities", [])) if fol_res.status_code == 200 else []

        report += f"👥 <b>Friends (Mutual):</b> <code>{len(friends_list)}</code>\n"
        report += f"❤️ <b>Following:</b> <code>{len(following_list)}</code>\n"

        unread_url = f"{BASE_URL}/users/{LIT_USERNAME}/offline_msg_count"
        un_res = requests.get(unread_url, headers=headers)
        unread_count = un_res.json().get("data", {}).get(LIT_USERNAME, 0) if un_res.status_code == 200 else 0
        report += f"📥 <b>Unread Messages:</b> <code>{unread_count} စောင်</code>\n"

        group_url = f"{BASE_URL}/users/{LIT_USERNAME}/joined_chatgroups"
        g_res = requests.get(group_url, headers=headers)
        groups_list = g_res.json().get("data", []) if g_res.status_code == 200 else []
        report += f"💬 <b>Joined Groups:</b> <code>{len(groups_list)} ခု</code>\n"

        block_url = f"{BASE_URL}/users/{LIT_USERNAME}/blocks/users"
        b_res = requests.get(block_url, headers=headers)
        if b_res.status_code == 200:
            block_list = b_res.json().get("data", [])
            report += f"🚫 <b>Blacklisted Users:</b> <code>{len(block_list)} ယောက်</code>\n"
            if block_list:
                report += "📌 <b>Block ထားသူများစာရင်း:</b>\n"
                for block_id in block_list[:5]: # အယောက် ၅၀ ကျော်ရင် စာရှည်မှာစိုးလို့ ၅ ယောက်ဖြတ်ပြထားပါသည်
                    b_prof_res = requests.get(f"{BASE_URL}/users/{block_id}", headers=headers)
                    if b_prof_res.status_code == 200:
                        bp_ent = b_prof_res.json().get("entities", [{}])[0]
                        b_nickname = bp_ent.get("nickname") or b_prof_res.json().get("data", [{}])[0].get("nickname") or "Unknown"
                        report += f"• <code>{block_id}</code> - <b>{b_nickname}</b>\n"

        report += "━━━━━━━━━━━━━━━━━━━━━━\n"
        report += "🌌 <i>Engine: Dominic Ultimate Monitor System</i>"
        await bot.edit_message_text(report, message.chat.id, status_msg.message_id, parse_mode="HTML")
    except Exception as e:
        await bot.edit_message_text(f"🛑 <b>ENGINE ERROR:</b>\n<code>{str(e)}</code>", message.chat.id, status_msg.message_id, parse_mode="HTML")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎪 COMMAND: AUTO JOIN PARTY ROOM
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
    headers = {"User-Agent": "Easemob-SDK(Android) 4.5.3", "Authorization": f"Bearer {new_token}", "Content-Type": "application/json"}
    try:
        response = requests.post(join_url, headers=headers, timeout=15)
        if response.status_code in [200, 201]:
            await bot.edit_message_text(f"🎉 <b>PARTY JOIN SUCCESS!</b>\n━━━━━━━━━━━━━━━━━━━━━━\n🎪 <b>Joined Party ID:</b> <code>{party_id}</code>", message.chat.id, status_msg.message_id, parse_mode="HTML")
        else:
            await bot.edit_message_text(f"🛑 <b>PARTY JOIN FAILED!</b>\n━━━━━━━━━━━━━━━━━━━━━━\n❌ <b>HTTP Error:</b> <code>{response.status_code}</code>\n📝 <b>Reason:</b> <pre>{response.text}</pre>", message.chat.id, status_msg.message_id, parse_mode="HTML")
    except Exception as e:
        await bot.edit_message_text(f"🛑 <b>INJECTOR CRITICAL ERROR:</b>\n<code>{str(e)}</code>", message.chat.id, status_msg.message_id, parse_mode="HTML")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
