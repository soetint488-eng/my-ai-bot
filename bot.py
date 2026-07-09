import logging
import requests
import json
import datetime
from aiogram import Bot, Dispatcher, executor, types

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔑 CREDENTIALS & CONFIG (DOMINIC ENGINE ULTIMATE v6.0)
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
        "🌌 <b>Dominic Ultimate Litmatch Messenger Bot v6.0</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 <b>အသုံးပြုနိုင်သည့် Command များ:</b>\n"
        "➡️ /check - အကောင့်အခြေအနေနှင့် Block စာရင်း စစ်ရန်\n"
        "➡️ /messages - မဖတ်ရသေးသော မက်ဆေ့ခ်ျများနှင့် ပို့သူကို Live ဖတ်ရန် (Direct Force System)\n"
        "➡️ /reply [User_ID] [စာသား] - သတ်မှတ်ထားသောသူထံသို့ စာလှမ်းပြန်ရန်\n"
        "➡️ /join [Party_ID] - Party ခန်းဝင်ရန်\n\n"
        "ဆာဗာဒေတာတိုက်ရိုက်စနစ်ဖြင့် အဆင့်မြှင့်တင်ထားပါတယ်ဗျာ။",
        parse_mode="HTML"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📩 COMMAND: FETCH UNREAD MESSAGES (Direct Payload System)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['messages'])
async def handle_fetch_messages(message: types.Message):
    status_msg = await message.reply("📥 <b>DOMINIC MESSENGER: CRACKING OFFLINE MSG PAYLOADS...</b>", parse_mode="HTML")
    
    new_token = get_live_token()
    if not not new_token == False and not new_token:
        await bot.edit_message_text("🛑 <b>TOKEN ERROR:</b> Sync failed.", message.chat.id, status_msg.message_id, parse_mode="HTML")
        return

    headers = {
        "User-Agent": "Easemob-SDK(Android) 4.5.3",
        "Authorization": f"Bearer {new_token}",
        "Content-Type": "application/json"
    }

    # ၁။ ပထမဆုံး မဖတ်ရသေးတဲ့ အရေအတွက်ကို စစ်မယ်
    count_url = f"{BASE_URL}/users/{LIT_USERNAME}/offline_msg_count"
    
    try:
        c_res = requests.get(count_url, headers=headers, timeout=15)
        unread_count = 0
        if c_res.status_code == 200:
            unread_count = c_res.json().get("data", {}).get(LIT_USERNAME, 0)
            
        msg_report = "📥 <b>LITMATCH LIVE MESSAGES REPORT</b>\n"
        msg_report += "━━━━━━━━━━━━━━━━━━━━━━\n"
        msg_report += f"📩 <b>မဖတ်ရသေးသော စာစုစုပေါင်း:</b> <code>{unread_count} စောင်</code>\n\n"

        # ၂။ သမရိုးကျ လမ်းကြောင်းအလုပ်မလုပ်ရင် Direct Message Box Payload စနစ်နဲ့ စာတွေကို လှမ်းဆွဲထုတ်မယ်
        # Easemob Direct Chat Message Fetching Endpoint
        direct_msg_url = f"{BASE_URL}/users/{LIT_USERNAME}/offline_msg_status"
        
        res = requests.get(direct_msg_url, headers=headers, timeout=15)
        
        if res.status_code == 200:
            # ဆာဗာကနေ ဝင်လာတဲ့ message data array ကိုဖတ်မယ်
            entities = res.json().get("entities", []) or res.json().get("data", [])
            
            if isinstance(entities, dict):
                # Dict ပုံစံနဲ့လာရင် list ပြောင်းပေးမယ်
                entities = [entities]

            msg_report += "📌 <b>နောက်ဆုံးဝင်ထားသော စာများနှင့် ပို့သူများ:</b>\n\n"
            active_extracted = 0

            for msg_item in entities:
                # API Mapping အရ ပို့သူ ID နှင့် စာသားကို ရှာဖွေဖော်ထုတ်ခြင်း
                from_user = msg_item.get("from") or msg_item.get("meta", {}).get("from")
                
                # စာသား payload ကို ဖြုတ်ချခြင်း
                msg_body = "စာသားမဟုတ်သော ဖိုင်တစ်ခုဖြစ်နိုင်ပါသည်"
                payload_data = msg_item.get("payload", {})
                if payload_data:
                    bodies = payload_data.get("bodies", [{}])
                    if bodies:
                        msg_body = bodies[0].get("msg", "အသံ (သို့) ပုံရိပ်ဖိုင်")
                else:
                    msg_body = msg_item.get("msg", {}).get("msg", "မက်ဆေ့ခ်ျဖတ်မရပါ")

                if from_user and from_user != LIT_USERNAME:
                    active_extracted += 1
                    msg_report += f"👤 <b>From ID:</b> <code>{from_user}</code>\n"
                    msg_report += f"💬 <b>Message:</b> <code>{msg_body}</code>\n"
                    msg_report += f"✍️ <i>စာပြန်ရန်:</i> <code>/reply {from_user} [စာသား]</code>\n"
                    msg_report += "──────────────────\n"

            if active_extracted == 0 and unread_count > 0:
                # အကယ်၍ ဆာဗာက offline_msg_status မှာ data block ထားရင် fallback အနေနဲ့ chatroom list ကနေ ပို့သူကို ရှာမယ်
                fallback_url = f"{BASE_URL}/users/{LIT_USERNAME}/joined_chatgroups"
                fb_res = requests.get(fallback_url, headers=headers, timeout=15)
                msg_report += "⚠️ <i>ဆာဗာလုံခြုံရေးကြောင့် စာသားကို တိုက်ရိုက်ဆွဲမရပါ။ သို့သော် အကောင့်ထဲသို့ Message Box မှ စာလှမ်းပို့ထားခြင်း ဖြစ်ပါသည်။</i>\n"
                msg_report += "💡 <i>စာပြန်ချင်ပါက သိရှိထားသော User ID ကိုသုံးပြီး တိုက်ရိုက် `/reply` လုပ်နိုင်ပါတယ်ဗျာ။</i>\n"

        else:
            msg_report += f"⚠️ <b>ဆာဗာမှ ဒေတာထုတ်ပေးရန် ငြင်းပယ်ထားပါသည် (HTTP {res.status_code})</b>\n"
            msg_report += "💡 <i>ဒါပေမဲ့ `/reply [User_ID] [စာသား]` command ကို သုံးပြီး စာလှမ်းပို့လို့ ရနေဆဲ ဖြစ်ပါတယ် ကိုကို Dominic။</i>\n"

        msg_report += "━━━━━━━━━━━━━━━━━━━━━━\n"
        msg_report += "🌌 <i>Engine: Dominic Direct Payload Synchronizer v6.0</i>"
        
        await bot.edit_message_text(msg_report, message.chat.id, status_msg.message_id, parse_mode="HTML")
            
    except Exception as e:
        await bot.edit_message_text(f"🛑 <b>MESSENGER ERROR:</b>\n<code>{str(e)}</code>", message.chat.id, status_msg.message_id, parse_mode="HTML")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✍️ COMMAND: REPLY / SEND MESSAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['reply'])
async def handle_send_reply(message: types.Message):
    args = message.get_args()
    if not args or len(args.split()) < 2:
        await message.reply("❌ <b>အသုံးပြုပုံ မှားယွင်းနေပါသည်။</b>\nဥပမာ- <code>/reply [Target_User_ID] [ပြန်ချင်တဲ့စာသား]</code>", parse_mode="HTML")
        return

    parts = args.split(maxsplit=1)
    target_id = parts[0].strip()
    reply_text = parts[1].strip()

    status_msg = await message.reply(f"🚀 <b>DOMINIC MESSENGER: SENDING MESSAGE TO [{target_id}]...</b>", parse_mode="HTML")

    new_token = get_live_token()
    if not new_token:
        await bot.edit_message_text("🛑 <b>TOKEN ERROR:</b> Auto-login failed.", message.chat.id, status_msg.message_id, parse_mode="HTML")
        return

    send_msg_url = f"{BASE_URL}/messages"
    headers = {
        "User-Agent": "Easemob-SDK(Android) 4.5.3",
        "Authorization": f"Bearer {new_token}",
        "Content-Type": "application/json"
    }

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
                f"🟢 <b>Status:</b> စာသားကို အောင်မြင်စွာ ပို့လွှတ်ပြီးပါပြီ။\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🌌 <i>Engine: Dominic Message Injector</i>",
                message.chat.id, status_msg.message_id, parse_mode="HTML"
            )
        else:
            await bot.edit_message_text(f"🛑 <b>MESSAGE SEND FAILED!</b>\nHTTP: {response.status_code}", message.chat.id, status_msg.message_id, parse_mode="HTML")
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

    headers = {"User-Agent": "Easemob-SDK(Android) 4.5.3", "Authorization": f"Bearer {new_token}", "Content-Type": "application/json"}
    report = "🚀 <b>DOMINIC ULTIMATE LITMATCH REPORT</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"
    try:
        profile_url = f"{BASE_URL}/users/{LIT_USERNAME}"
        p_res = requests.get(profile_url, headers=headers)
        if p_res.status_code == 200:
            p_ent = p_res.json().get("entities", [{}])[0]
            nickname = p_ent.get("nickname") or LIT_USERNAME
            report += f"👤 <b>User ID:</b> <code>{LIT_USERNAME}</code>\n🏷️ <b>Nickname:</b> <code>{nickname}</code>\n"

        unread_url = f"{BASE_URL}/users/{LIT_USERNAME}/offline_msg_count"
        un_res = requests.get(unread_url, headers=headers)
        unread_count = un_res.json().get("data", {}).get(LIT_USERNAME, 0) if un_res.status_code == 200 else 0
        report += f"📥 <b>Unread Messages:</b> <code>{unread_count} စောင်</code>\n"

        block_url = f"{BASE_URL}/users/{LIT_USERNAME}/blocks/users"
        b_res = requests.get(block_url, headers=headers)
        if b_res.status_code == 200:
            block_list = b_res.json().get("data", [])
            report += f"🚫 <b>Blacklisted Users:</b> <code>{len(block_list)} ယောက်</code>\n"
            if block_list:
                report += "📌 <b>Block ထားသူများ:</b>\n"
                for block_id in block_list[:5]:
                    bp = requests.get(f"{BASE_URL}/users/{block_id}", headers=headers)
                    bn = bp.json().get("entities", [{}])[0].get("nickname", "Unknown") if bp.status_code == 200 else "Unknown"
                    report += f"• <code>{block_id}</code> - <b>{bn}</b>\n"

        report += "━━━━━━━━━━━━━━━━━━━━━━\n🌌 <i>Engine: Dominic Ultimate Monitor System</i>"
        await bot.edit_message_text(report, message.chat.id, status_msg.message_id, parse_mode="HTML")
    except Exception as e:
        await bot.edit_message_text(f"🛑 <b>ENGINE ERROR:</b> {str(e)}", message.chat.id, status_msg.message_id, parse_mode="HTML")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎪 COMMAND: AUTO JOIN PARTY ROOM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['join'])
async def handle_join_party(message: types.Message):
    args = message.get_args()
    if not args: return
    party_id = args.strip()
    status_msg = await message.reply("🎪 <b>JOINING...</b>", parse_mode="HTML")
    new_token = get_live_token()
    join_url = f"{BASE_URL}/chatgroups/{party_id}/users/{LIT_USERNAME}"
    headers = {"User-Agent": "Easemob-SDK(Android) 4.5.3", "Authorization": f"Bearer {new_token}", "Content-Type": "application/json"}
    res = requests.post(join_url, headers=headers)
    await bot.edit_message_text(f"<b>Response Code:</b> {res.status_code}\n<pre>{res.text}</pre>", message.chat.id, status_msg.message_id, parse_mode="HTML")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
