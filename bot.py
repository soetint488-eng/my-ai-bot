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
# Bot & RapidAPI Configuration
# =====================================================================
BOT_TOKEN = "8702294693:AAGF_mmGKAg7-mWBuAl34jevVtDJ0mZE8HU"
RAPIDAPI_KEY = "06b1562a59msh39810b847e9d0e2p151fd6jsn3a9d60ae50a9"
RAPIDAPI_HOST = "id-game-checker.p.rapidapi.com"

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
    "la": "🇱🇦 Laos", "laos": "🇱🇦 Laos",
    "br": "🇧🇷 Brazil", "brazil": "🇧🇷 Brazil",
    "in": "🇮🇳 India", "india": "🇮🇳 India",
    "us": "🇺🇸 United States", "usa": "🇺🇸 United States"
}

def get_pretty_country(raw_region):
    if not raw_region:
        return "🌐 International / Global"
    clean_region = str(raw_region).strip().lower()
    return COUNTRY_MAP.get(clean_region, f"🏳️ {raw_region.title()}")

# =====================================================================
# ⚡ LIVE BLINKING BUTTON ANIMATION (စာလုံးပေါ်လိုက်ပျောက်လိုက် စနစ်)
# =====================================================================
# နာမည်လေး လင်းလိုက်၊ ပျောက်လိုက်၊ တဖျတ်ဖျတ်ဖြစ်နေစေမည့် Loop Frames
BLINK_FRAMES = [
    "⚡ [  𝑷𝒂𝒚𝑿-𝑴𝑴  ] ⚡",
    "⚫ [             ] ⚫",
    "✨ [ 🌟 𝑷𝒂𝒚𝑿-𝑴𝑴 🌟 ] ✨",
    "⚫ [             ] ⚫"
]

def animate_start_menu(chat_id, message_id):
    """Background Thread အနေဖြင့် စာသားကို အမြဲတမ်း ပေါ်လိုက်ပျောက်လိုက် ဖြစ်စေရန်"""
    frame_index = 0
    while True:
        try:
            time.sleep(2.0) # ၂ စက္ကန့်တစ်ခါ လင်းလိုက်မှိတ်လိုက်ဖြစ်မည်
            
            current_text = BLINK_FRAMES[frame_index]
            
            markup = InlineKeyboardMarkup()
            btn_ml = InlineKeyboardButton("🎮 Mobile Legends", callback_data="info_ml")
            btn_ff = InlineKeyboardButton("🔥 Garena Free Fire", callback_data="info_ff")
            btn_brand = InlineKeyboardButton(current_text, callback_data="brand_click")
            
            markup.row(btn_ml, btn_ff)
            markup.row(btn_brand)
            
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)
            frame_index = (frame_index + 1) % len(BLINK_FRAMES)
            
        except Exception:
            break # User က Message ဖျက်လိုက်ရင် Loop ရပ်မည်

# =====================================================================
# API Functions
# =====================================================================
def check_mlbb_id(user_id, zone_id):
    url = f"https://id-game-checker.p.rapidapi.com/mobile-legends/{user_id}/{zone_id}"
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": RAPIDAPI_HOST}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200: return None, f"Status {r.status_code}"
        return r.json(), None
    except Exception as e: return None, str(e)

def check_ff_id(player_id):
    url = f"https://id-game-checker.p.rapidapi.com/dfm-garena/{player_id}"
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": RAPIDAPI_HOST}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200: return None, f"Status {r.status_code}"
        return r.json(), None
    except Exception as e: return None, str(e)

# =====================================================================
# Bot Handlers & UI
# =====================================================================

# ၁။ /start Command (Blinking Button စတင်ခြင်း)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    guide = (
        "⚔️ **PREMIUM AUTOMATION ID CHECKER** ⚔️\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Welcome! Select your target game to get account database details:\n\n"
        "⚙️ _Status: High-Speed Response Core Active_"
    )
    
    markup = InlineKeyboardMarkup()
    btn_ml = InlineKeyboardButton("🎮 Mobile Legends", callback_data="info_ml")
    btn_ff = InlineKeyboardButton("🔥 Garena Free Fire", callback_data="info_ff")
    btn_brand = InlineKeyboardButton("⚡ [  𝑷𝒂𝒚𝑿-𝑴𝑴  ] ⚡", callback_data="brand_click")
    
    markup.row(btn_ml, btn_ff)
    markup.row(btn_brand)
    
    sent_msg = bot.send_message(message.chat.id, guide, parse_mode="Markdown", reply_markup=markup)
    
    # Blinking Thread အား နှိုးခြင်း
    threading.Thread(
        target=animate_start_menu, 
        args=(message.chat.id, sent_msg.message_id), 
        daemon=True
    ).start()

# Button Callback
@bot.callback_query_handler(func=lambda call: True)
def callback_game_info(call):
    bot.answer_callback_query(call.id)
    
    if call.data == "info_ml":
        text = (
            "🎮 **MOBILE LEGENDS QUERY MODE**\n\n"
            "Send ID in bracket format:\n"
            "`/ml [User_ID] ([Zone_ID])`\n\n"
            "💡 **Example:**\n"
            "`/ml 2112723799 (19915)`"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
        
    elif call.data == "info_ff":
        text = (
            "🔥 **FREE FIRE QUERY MODE**\n\n"
            "Send Player UID directly:\n"
            "`/ff [Player_UID]`\n\n"
            "💡 **Example:**\n"
            "`/ff 182200303107200135203`"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
        
    elif call.data == "brand_click":
        bot.send_message(call.message.chat.id, f"🚀 **{BRANDING} Gaming Platform Verification Tool v2.0**")

# ၂။ /ml Command Handler (Premium UI)
@bot.message_handler(commands=['ml'])
def handle_ml_check(message):
    match = re.search(r'/ml\s+(\d+)\s*\((.*?)\)', message.text)
    
    if not match:
        bot.reply_to(
            message,
            "⚠️ **Invalid MLBB Format!**\nUse: `/ml 2112723799 (19915)`",
            parse_mode="Markdown"
        )
        return
        
    user_id = match.group(1)
    zone_id = match.group(2).strip()
    
    status_msg = bot.reply_to(message, "🛸 *Extracting keys and connecting to Moonton Core...*", parse_mode="Markdown")
    result, error = check_mlbb_id(user_id, zone_id)
    
    if error:
        bot.edit_message_text(f"❌ **Error:** `{error}`\n\n🛠️ Developer: {BRANDING}", message.chat.id, status_msg.message_id, parse_mode="Markdown")
        return
        
    if result:
        nickname = result.get("nickname") or result.get("name") or result.get("username") or result.get("userName") or result.get("player_name")
        raw_region = result.get("region") or result.get("country") or result.get("zone_name") or result.get("zoneName") or result.get("region_code")
        
        if not nickname:
            for key in ["data", "result", "player"]:
                if key in result and isinstance(result[key], dict):
                    inner = result[key]
                    nickname = inner.get("nickname") or inner.get("name") or inner.get("username") or inner.get("player_name")
                    raw_region = raw_region or inner.get("region") or inner.get("country") or inner.get("zone_name")
                    break

        if not nickname: nickname = "In-Game Hidden / VIP"
        pretty_region = get_pretty_country(raw_region)
            
        cool_ui = (
            "👑 **MOBILE LEGENDS ACCOUNT PROFILE** 👑\n"
            "🧬 𝘚𝘺𝘴𝘵𝘦𝘮: 𝘔𝘰𝘰𝘯𝘵𝘰𝘯 𝘋𝘢𝘵𝘢𝘣𝘢𝘴𝘦 𝘓𝘪𝘯𝘬\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 **𝘗𝘭𝘢𝘺𝘦𝘳 𝘕𝘢𝘮𝘦 :** `{nickname}`\n"
            f"🌐 **𝘙𝘦𝘨𝘪𝘰𝘯 / 𝘡𝘰𝘯𝘦 :** `{pretty_region}`\n"
            f"🆔 **𝘜𝘴𝘦𝘳 𝘐𝘋      :** `{user_id}`\n"
            f"📁 **𝘡𝘰𝘯𝘦 𝘐𝘋      :** `{zone_id}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛸 **𝘝𝘦𝘳𝘪𝘧𝘪𝘦𝘥 𝘚𝘦𝘳𝘷𝘪𝘤𝘦 𝘉𝘺 :** {BRANDING}"
        )
        bot.edit_message_text(cool_ui, message.chat.id, status_msg.message_id, parse_mode="Markdown")

# ၃။ /ff Command Handler (Premium UI + Region Checker Added)
@bot.message_handler(commands=['ff'])
def handle_ff_check(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ **Invalid FF Format!**\nUse: `/ff [Player_UID]`", parse_mode="Markdown")
        return
        
    player_id = args[1]
    status_msg = bot.reply_to(message, "🛸 *Infiltrating Garena Free Fire Servers...*", parse_mode="Markdown")
    result, error = check_ff_id(player_id)
    
    if error:
        bot.edit_message_text(f"❌ **Error:** `{error}`\n\n🛠️ Developer: {BRANDING}", message.chat.id, status_msg.message_id, parse_mode="Markdown")
        return
        
    if result:
        # Free Fire Name & Region Parser
        nickname = result.get("nickname") or result.get("username") or result.get("name") or result.get("player_name")
        raw_region = result.get("region") or result.get("country") or result.get("country_code") or result.get("region_code")
        
        # Nested Node စစ်ဆေးခြင်း (FF API Keys စုံအောင် လိုက်ရှာပေးခြင်း)
        if not nickname or not raw_region:
            for key in ["data", "result", "player"]:
                if key in result and isinstance(result[key], dict):
                    inner = result[key]
                    nickname = nickname or inner.get("nickname") or inner.get("username") or inner.get("name")
                    raw_region = raw_region or inner.get("region") or inner.get("country") or inner.get("country_code")
                    break
                    
        if not nickname: nickname = "Unknown Garena Player"
        pretty_region = get_pretty_country(raw_region)
            
        cool_ui = (
            "🔥 **GARENA FREE FIRE PROFILE** 🔥\n"
            "🧬 𝘚𝘺𝘴𝘵𝘦𝘮: 𝘎𝘢𝘳𝘦𝘯𝘢 𝘓𝘪𝘷𝘦 𝘊𝘰𝘳𝘦\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 **𝘗授权𝘢𝘺𝘦𝘳 𝘕𝘢𝘮𝘦 :** `{nickname}`\n"
            f"🌐 **𝘙𝘦𝘨𝘪𝘰𝘯 / 𝘊𝘰𝘶𝘯𝘵𝘳𝘺:** `{pretty_region}`\n"
            f"🆔 **𝘗𝘭𝘢𝘺𝘦𝘳 𝘜𝘐𝘋   :** `{player_id}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛸 **𝘘𝘶𝘦𝘳𝘺 𝘝𝘦𝘳𝘪𝘧𝘪𝘦𝘥 𝘉𝘺 :** {BRANDING}"
        )
        bot.edit_message_text(cool_ui, message.chat.id, status_msg.message_id, parse_mode="Markdown")

# =====================================================================
# 4. Main Runner
# =====================================================================
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("Multi-Game Premium Checker Bot is Live with Blinking effect & FF Region...")
    bot.infinity_polling()
