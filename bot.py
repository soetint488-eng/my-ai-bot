import os
import sys
import re
import time
import threading
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# =====================================================================
# 🛠️ RENDER PORT BINDING ERROR FIX (FLASK WEB SERVER)
# =====================================================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Multi-Game Premium Checker Bot is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host="0.0.0.0", port=port)

# =====================================================================
# Bot & RapidAPI Configuration (API အသစ်စက်စက် ချိန်ညှိပြီး)
# =====================================================================
BOT_TOKEN = "8702294693:AAGF_mmGKAg7-mWBuAl34jevVtDJ0mZE8HU"
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"
RAPIDAPI_HOST = "check-id-game.p.rapidapi.com"

bot = telebot.TeleBot(BOT_TOKEN)

BRANDING = "✨ 𝑷𝒂𝒚𝑿-𝑴𝑴 💫"

# 🌍 Universal Country/Region Code Mapping
COUNTRY_MAP = {
    "mm": "🇲🇲 Myanmar", "myanmar": "🇲🇲 Myanmar", "burma": "🇲🇲 Myanmar",
    "id": "🇮🇩 Indonesia", "indonesia": "🇮🇩 Indonesia",
    "ph": "🇵🇭 Philippines", "philippines": "🇵🇭 Philippines",
    "sg": "🇸🇬 Singapore", "singapore": "🇸🇬 Singapore",
    "my": "🇲🇾 Malaysia", "malaysia": "🇲🇾 Malaysia",
    "th": "🇹🇭 Thailand", "thailand": "🇹🇭 Thailand",
    "kh": "🇰🇭 Cambodia", "cambodia": "🇰🇭 Cambodia",
    "vn": "🇻🇳 Vietnam", "vietnam": "🇻🇳 Vietnam",
    "la": "🇱🇦 Laos", "laos": "🇱🇦 Laos"
}

def get_pretty_country(raw_region):
    if not raw_region:
        return "🌐 International / Global"
    clean_region = str(raw_region).strip().lower()
    return COUNTRY_MAP.get(clean_region, f"🏳️ {raw_region.title()}")

# =====================================================================
# ⚡ LIVE BLINKING BUTTON ANIMATION (စာလုံးပေါ်လိုက်ပျောက်လိုက် စနစ်)
# =====================================================================
BLINK_FRAMES = [
    "⚡ [  𝑷𝒂𝒚𝑿-𝑴𝑴  ] ⚡",
    "⚫ [             ] ⚫",
    "✨ [ 🌟 𝑷𝒂𝒚𝑿-𝑴𝑴 🌟 ] ✨",
    "⚫ [             ] ⚫"
]

def animate_start_menu(chat_id, message_id):
    """Background Thread အနေဖြင့် ခလုတ်စာသားကို ပေါ်လိုက်ပျောက်လိုက် အမြဲဖြစ်စေရန်"""
    frame_index = 0
    while True:
        try:
            time.sleep(2.0) # ၂ စက္ကန့်တစ်ခါ လင်းလိုက်မှိတ်လိုက်ဖြစ်မည်
            current_text = BLINK_FRAMES[frame_index]
            
            markup = InlineKeyboardMarkup()
            btn_ml = InlineKeyboardButton("🎮 Mobile Legends", callback_data="info_ml")
            btn_ff = InlineKeyboardButton("🔥 Free Fire", callback_data="info_ff")
            btn_pubg = InlineKeyboardButton("🔫 PUBG Mobile", callback_data="info_pubg")
            btn_brand = InlineKeyboardButton(current_text, callback_data="brand_click")
            
            markup.row(btn_ml, btn_ff)
            markup.row(btn_pubg)
            markup.row(btn_brand)
            
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)
            frame_index = (frame_index + 1) % len(BLINK_FRAMES)
            
        except Exception:
            break

# =====================================================================
# API Functions (New API Core Connection)
# =====================================================================
def call_game_api(endpoint, target_id):
    # check-id-game API အသစ်အတွက် တည်ဆောက်ပုံစနစ်
    url = f"https://{RAPIDAPI_HOST}/api/rapid_api/{endpoint}/{target_id}"
    
    # MLBB အတွက် Host အဟောင်းသုံးရန် လိုအပ်ပါက Dynamic ပြောင်းလဲခြင်း
    if endpoint == "mobile-legends":
        url = f"https://id-game-checker.p.rapidapi.com/mobile-legends/{target_id}"
        headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": "id-game-checker.p.rapidapi.com"}
    else:
        headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": RAPIDAPI_HOST, "Content-Type": "application/json"}
        
    try:
        r = requests.get(url, headers=headers, timeout=12)
        if r.status_code != 200: return None, f"Status {r.status_code}"
        return r.json(), None
    except Exception as e: return None, str(e)

# =====================================================================
# Bot Handlers & UI
# =====================================================================

# ၁။ /start Command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    guide = (
        "⚔️ **PREMIUM AUTOMATION ID CHECKER** ⚔️\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Welcome! Select your target game to get account database details:\n\n"
        "⚙️ _Status: Multi-Core System Active_"
    )
    
    markup = InlineKeyboardMarkup()
    btn_ml = InlineKeyboardButton("🎮 Mobile Legends", callback_data="info_ml")
    btn_ff = InlineKeyboardButton("🔥 Free Fire", callback_data="info_ff")
    btn_pubg = InlineKeyboardButton("🔫 PUBG Mobile", callback_data="info_pubg")
    btn_brand = InlineKeyboardButton("⚡ [  𝑷𝒂𝒚𝑿-𝑴𝑴  ] ⚡", callback_data="brand_click")
    
    markup.row(btn_ml, btn_ff)
    markup.row(btn_pubg)
    markup.row(btn_brand)
    
    sent_msg = bot.send_message(message.chat.id, guide, parse_mode="Markdown", reply_markup=markup)
    
    threading.Thread(target=animate_start_menu, args=(message.chat.id, sent_msg.message_id), daemon=True).start()

# Button Callback
@bot.callback_query_handler(func=lambda call: True)
def callback_game_info(call):
    bot.answer_callback_query(call.id)
    
    if call.data == "info_ml":
        bot.send_message(call.message.chat.id, "🎮 **MOBILE LEGENDS QUERY**\n\nFormat:\n`/ml [User_ID] ([Zone_ID])`\n\n💡 **Example:**\n`/ml 2112723799 (19915)`", parse_mode="Markdown")
    elif call.data == "info_ff":
        bot.send_message(call.message.chat.id, "🔥 **FREE FIRE QUERY**\n\nFormat:\n`/ff [Player_UID]`\n\n💡 **Example:**\n`/ff 11944852314`", parse_mode="Markdown")
    elif call.data == "info_pubg":
        bot.send_message(call.message.chat.id, "🔫 **PUBG MOBILE QUERY**\n\nFormat:\n`/pubg [Character_ID]`\n\n💡 **Example:**\n`/pubg 5930748140`", parse_mode="Markdown")
    elif call.data == "brand_click":
        bot.send_message(call.message.chat.id, f"🚀 **{BRANDING} Multi-Core Identity System v2.5**")

# ၂။ /ml Command Handler
@bot.message_handler(commands=['ml'])
def handle_ml_check(message):
    match = re.search(r'/ml\s+(\d+)\s*\((.*?)\)', message.text)
    if not match:
        bot.reply_to(message, "⚠️ **Invalid MLBB Format!**\nUse: `/ml 2112723799 (19915)`", parse_mode="Markdown")
        return
        
    user_id = match.group(1)
    zone_id = match.group(2).strip()
    
    status_msg = bot.reply_to(message, "🛸 *Connecting to Moonton Core...*", parse_mode="Markdown")
    result, error = call_game_api("mobile-legends", f"{user_id}/{zone_id}")
    
    if error:
        bot.edit_message_text(f"❌ **Error:** `{error}`\n\n🛠️ Developer: {BRANDING}", message.chat.id, status_msg.message_id, parse_mode="Markdown")
        return
        
    if result:
        nickname = result.get("nickname") or result.get("name") or result.get("username")
        raw_region = result.get("region") or result.get("country") or result.get("zone_name")
        
        if not nickname:
            for key in ["data", "result"]:
                if key in result and isinstance(result[key], dict):
                    nickname = result[key].get("nickname") or result[key].get("name")
                    raw_region = raw_region or result[key].get("region") or result[key].get("country")
                    break
                    
        nickname = nickname or "In-Game Hidden / VIP"
        pretty_region = get_pretty_country(raw_region)
        
        cool_ui = (
            "👑 **MOBILE LEGENDS ACCOUNT PROFILE** 👑\n"
            "🧬 𝘚𝘺𝘴𝘵𝘦𝘮: 𝘔𝘰𝘰𝘯𝘵𝘰𝘯 𝘋𝘢𝘵𝘢𝘣𝘢𝘴ε 𝘓𝘪𝘯𝘬\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 **𝘗𝘭𝘢𝘺𝘦𝘳 𝘕𝘢𝘮𝒆 :** `{nickname}`\n"
            f"🌐 **𝘙𝘦𝘨𝘪𝘰𝘯 / 𝘡𝘰𝘯𝘦 :** `{pretty_region}`\n"
            f"🆔 **𝘜𝘴𝘦𝘳 𝘐𝘋      :** `{user_id}`\n"
            f"📁 **𝘡𝘰𝘯𝘦 𝘐𝘋      :** `{zone_id}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛸 **𝘝𝘦𝘳𝘪𝘧𝘪𝘦𝘥 𝘚𝘦𝘳眷𝘷𝘪𝘤𝘦 𝘉𝘺 :** {BRANDING}"
        )
        bot.edit_message_text(cool_ui, message.chat.id, status_msg.message_id, parse_mode="Markdown")

# ၃။ /ff Command Handler (Free Fire New API)
@bot.message_handler(commands=['ff'])
def handle_ff_check(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ **Invalid FF Format!**\nUse: `/ff [Player_UID]`", parse_mode="Markdown")
        return
        
    player_id = args[1]
    status_msg = bot.reply_to(message, "🛸 *Infiltrating Garena Free Fire Live Core...*", parse_mode="Markdown")
    result, error = call_game_api("ff_idgame", player_id)
    
    if error:
        bot.edit_message_text(f"❌ **Error:** `{error}`\n\n🛠️ Developer: {BRANDING}", message.chat.id, status_msg.message_id, parse_mode="Markdown")
        return
        
    if result:
        nickname = result.get("nickname") or result.get("username") or result.get("name")
        raw_region = result.get("region") or result.get("country") or result.get("country_code")
        
        if not nickname:
            for key in ["data", "result"]:
                if key in result and isinstance(result[key], dict):
                    nickname = result[key].get("nickname") or result[key].get("username") or result[key].get("name") or result[key].get("userName")
                    raw_region = raw_region or result[key].get("region") or result[key].get("country")
                    break
                    
        nickname = nickname or "Unknown Garena Player"
        pretty_region = get_pretty_country(raw_region)
        
        cool_ui = (
            "🔥 **GARENA FREE FIRE PROFILE** 🔥\n"
            "🧬 𝘚𝘺𝘴𝘵𝘦𝘮: 𝘎𝘢𝘳𝘦𝘯𝘢 𝘋𝘢𝘵𝘢𝘣𝘢𝘴𝘦\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 **𝘗𝘭𝘢𝘺𝘦𝘳 𝘕𝘢𝘮𝒆 :** `{nickname}`\n"
            f"🌐 **𝘙𝘦𝘨𝘪𝘰𝘯 / 𝘊𝘰𝘶𝘯𝘵𝘳𝘺:** `{pretty_region}`\n"
            f"🆔 **𝘗𝘭𝘢𝘺𝘦𝘳 𝘜𝘲𝘐𝘋   :** `{player_id}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛸 **𝘘𝘶𝘦𝘳𝘺 𝘝𝘦𝘳𝘪𝘧𝘪𝘦𝘥 𝘉𝘺 :** {BRANDING}"
        )
        bot.edit_message_text(cool_ui, message.chat.id, status_msg.message_id, parse_mode="Markdown")

# ၄။ /pubg Command Handler (PUBG Mobile New API)
@bot.message_handler(commands=['pubg'])
def handle_pubg_check(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ **Invalid PUBG Format!**\nUse: `/pubg [Character_ID]`", parse_mode="Markdown")
        return
        
    player_id = args[1]
    status_msg = bot.reply_to(message, "🛸 *Infiltrating PUBG Mobile Server Core...*", parse_mode="Markdown")
    result, error = call_game_api("cekpubgmobile", player_id)
    
    if error:
        bot.edit_message_text(f"❌ **Error:** `{error}`\n\n🛠️ Developer: {BRANDING}", message.chat.id, status_msg.message_id, parse_mode="Markdown")
        return
        
    if result:
        nickname = result.get("nickname") or result.get("username") or result.get("name")
        raw_region = result.get("region") or result.get("country")
        
        if not nickname:
            for key in ["data", "result"]:
                if key in result and isinstance(result[key], dict):
                    nickname = result[key].get("nickname") or result[key].get("username") or result[key].get("name") or result[key].get("userName")
                    raw_region = raw_region or result[key].get("region") or result[key].get("country")
                    break
                    
        nickname = nickname or "Unknown PUBG Player"
        pretty_region = get_pretty_country(raw_region)
        
        cool_ui = (
            "🔫 **PUBG MOBILE GLOBAL PROFILE** 🔫\n"
            "🧬 𝘚𝘺𝘴𝘵𝘦𝘮: 𝘛𝘦𝘯𝘤𝘦𝘯𝘵 𝘋𝘢𝘵𝘢𝘣𝘢𝘴𝘦\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 **𝘗𝘭𝘢𝘺𝘦𝘳 𝘕𝘢𝘮𝒆 :** `{nickname}`\n"
            f"🌐 **𝘙𝘦𝘨𝘪𝘰𝘯 / 𝘊𝘰𝘶𝘯𝘵𝘳𝘺:** `{pretty_region}`\n"
            f"🆔 **𝘊𝘩𝘢𝘳𝘢𝘤𝘵𝘦𝘳 𝘐𝘋 :** `{player_id}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛸 **𝘘𝘶𝘦𝘳𝘺 𝘝𝘦𝘳𝘪𝘧𝘪𝘦𝘥 𝘉𝘺 :** {BRANDING}"
        )
        bot.edit_message_text(cool_ui, message.chat.id, status_msg.message_id, parse_mode="Markdown")

# =====================================================================
# Main Runner
# =====================================================================
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("Multi-Game Telebot Server v2.5 is running perfectly...")
    bot.infinity_polling()
