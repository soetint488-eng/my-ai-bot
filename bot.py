import os
import sys
import re
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
    return "Multi-Game Checker Bot is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host="0.0.0.0", port=port)

# =====================================================================
# Bot & RapidAPI Configuration
# =====================================================================
BOT_TOKEN = "8761954371:AAFJjatvSIsLuy6DHvSOlQ3koZ1LbDyNH3A"
RAPIDAPI_KEY = "06b1562a59msh39810b847e9d0e2p151fd6jsn3a9d60ae50a9"
RAPIDAPI_HOST = "id-game-checker.p.rapidapi.com"

bot = telebot.TeleBot(BOT_TOKEN)

# Moving text & Static dynamic branding text
BRANDING = "✨ 𝑷𝒂𝒚𝑿-𝑴𝑴 💫"

# 🌍 Country Code များကို အလန်းစား Flag + အမည်အပြည့်စုံသို့ ပြောင်းပေးမည့် Map
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
        return "🌐 International"
    clean_region = str(raw_region).strip().lower()
    return COUNTRY_MAP.get(clean_region, f"🏳️ {raw_region.title()}")

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
# Bot Handlers & UI (telebot စနစ်)
# =====================================================================

# 1. /start command with Inline Buttons
@bot.message_handler(commands=['start'])
def send_welcome(message):
    guide = (
        "⚔️ **Welcome to Premium Game Checker Bot** ⚔️\n\n"
        "Select the game you want to check from the buttons below:\n\n"
        f"⏳ __System active via {BRANDING}__"
    )
    
    # Inline Buttons ဖန်တီးခြင်း
    markup = InlineKeyboardMarkup()
    btn_ml = InlineKeyboardButton("Mobile Legends 🎮", callback_data="info_ml")
    btn_ff = InlineKeyboardButton("Garena Free Fire 🔥", callback_data="info_ff")
    markup.row(btn_ml, btn_ff)
    
    bot.reply_to(message, guide, parse_mode="Markdown", reply_markup=markup)

# Button ကလစ်နှိပ်မှုများကို တုံ့ပြန်ခြင်း
@bot.callback_query_handler(func=lambda call: call.data in ["info_ml", "info_ff"])
def callback_game_info(call):
    if call.data == "info_ml":
        text = (
            "🎮 **MOBILE LEGENDS CHECKER**\n\n"
            "Please send the ID exactly in this format:\n"
            "`/ml [User_ID] ([Zone_ID])`\n\n"
            "💡 **Example:**\n"
            "`/ml 2112723799 (19915)`"
        )
    elif call.data == "info_ff":
        text = (
            "🔥 **FREE FIRE CHECKER**\n\n"
            "Please send the ID in this format:\n"
            "`/ff [Player_UID]`\n\n"
            "💡 **Example:**\n"
            "`/ff 182200303107200135203`"
        )
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

# 2. /ml Command Handler with Bracket Regex Format
@bot.message_handler(commands=['ml'])
def handle_ml_check(message):
    # Regex သုံးပြီး '2112723799 (19915)' ပုံစံကို ဖမ်းယူခြင်း
    match = re.search(r'/ml\s+(\d+)\s*\((.*?)\)', message.text)
    
    if not match:
        bot.reply_to(
            message,
            "⚠️ **Invalid MLBB Format!**\n\n"
            "You must use bracket style:\n"
            "`/ml 2112723799 (19915)`",
            parse_mode="Markdown"
        )
        return
        
    user_id = match.group(1)
    zone_id = match.group(2).strip()
    
    status_msg = bot.reply_to(message, "⏳ *Extracting keys and connecting to Moonton...*", parse_mode="Markdown")
    
    result, error = check_mlbb_id(user_id, zone_id)
    
    if error:
        bot.edit_message_text(f"❌ **Error:** `{error}`\n\n🛠️ Developer: {BRANDING}", message.chat.id, status_msg.message_id, parse_mode="Markdown")
        return
        
    if result:
        nickname = result.get("nickname") or result.get("username") or result.get("name") or "Hidden / Not Found"
        raw_region = result.get("region") or result.get("country") or result.get("zone_name") or ""
        
        # 🇲🇲 နိုင်ငံအမည်ကို အရှည်ကောက် ပြောင်းလဲခြင်း
        pretty_region = get_pretty_country(raw_region)
            
        cool_ui = (
            "🎮 **MOBILE LEGENDS PROFILE** 🎮\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 **Player Name :** `{nickname}`\n"
            f"🌐 **Region/Zone  :** `{pretty_region}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 **User ID :** `{user_id}`\n"
            f"📁 **Zone ID :** `{zone_id}`\n\n"
            f"💫 *Verified via {BRANDING}*"
        )
        bot.edit_message_text(cool_ui, message.chat.id, status_msg.message_id, parse_mode="Markdown")

# 3. /ff Command Handler (Garena Free Fire)
@bot.message_handler(commands=['ff'])
def handle_ff_check(message):
    args = message.text.split()
    if len(args) < 2:
        结构 = "⚠️ **Invalid FF Format!**\n\nUse: `/ff [Player_UID]`\nExample: `/ff 182200303107200135203`"
        bot.reply_to(message, 结构, parse_mode="Markdown")
        return
        
    player_id = args[1]
    status_msg = bot.reply_to(message, "⏳ *Scanning Garena Free Fire Data...*", parse_mode="Markdown")
    
    result, error = check_ff_id(player_id)
    
    if error:
        bot.edit_message_text(f"❌ **Error:** `{error}`\n\n🛠️ Developer: {BRANDING}", message.chat.id, status_msg.message_id, parse_mode="Markdown")
        return
        
    if result:
        nickname = result.get("nickname") or result.get("username") or result.get("name") or "Unknown Player"
        
        cool_ui = (
            "🔥 **GARENA FREE FIRE PROFILE** 🔥\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 **Player Name :** `{nickname}`\n"
            f"🆔 **Player UID   :** `{player_id}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💫 *Verified via {BRANDING}*"
        )
        bot.edit_message_text(cool_ui, message.chat.id, status_msg.message_id, parse_mode="Markdown")

# =====================================================================
# 4. Main Runner
# =====================================================================
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("Multi-Game Telebot Server is Live...")
    bot.infinity_polling()
