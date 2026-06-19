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
    return "Multi-Game Checker Bot is Online!"

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

# 🌍 Country Code Mapping
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
# ⚡ ANIMATION BUTTON TEXT LOOP (စာသားအရှင် ပြေးစေမည့် စနစ်)
# =====================================================================
# ခလုတ်ထဲက နာမည်လေးကို ဘယ်ညာ ရွေ့လျားပြေးနေစေမည့် frames များ
ANIMATION_FRAMES = [
    "✨ [ 𝑷𝒂𝒚𝑿-𝑴𝑴 ] ✨",
    "🌟 [  𝑷𝒂𝒚𝑿-𝑴𝑴  ] 🌟",
    "💫 [   𝑷𝒂𝒚𝑿-𝑴𝑴   ] 💫",
    "✨ [    𝑷𝒂𝒚𝑿-𝑴𝑴    ] ✨",
    "💫 [   𝑷𝒂𝒚𝑿-𝑴𝑴   ] 💫",
    "🌟 [  𝑷𝒂𝒚𝑿-𝑴𝑴  ] 🌟"
]

def animate_start_menu(chat_id, message_id):
    """အနောက်ကွယ်ကနေ ခလုတ်စာသားကို အဆက်မပြတ် Loop ပတ်ပြီး ပြောင်းလဲပေးမည့် Thread"""
    frame_index = 0
    while True:
        try:
            time.sleep(2.5) # ၂.၅ စက္ကန့်တည်းတစ်ခါ စာသားပြေးမည်
            
            # လက်ရှိ frame အား ယူခြင်း
            current_brand = ANIMATION_FRAMES[frame_index]
            
            # Markup ကို ခလုတ်အသစ်စာသားနဲ့ ပြန်ပြင်ဆင်ခြင်း
            markup = InlineKeyboardMarkup()
            btn_ml = InlineKeyboardButton("Mobile Legends 🎮", callback_data="info_ml")
            btn_ff = InlineKeyboardButton("Garena Free Fire 🔥", callback_data="info_ff")
            btn_brand = InlineKeyboardButton(current_brand, callback_data="brand_click")
            
            markup.row(btn_ml, btn_ff)
            markup.row(btn_brand) # အောက်ခြေမှာ နာမည်ပြေးနေမည့် ခလုတ်
            
            # Telegram ထံ စာသားအသစ်အား Edit လုပ်ရန် လှမ်းပို့ခြင်း
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)
            
            # Frame ပတ်လမ်းအား တိုးမြှင့်ခြင်း
            frame_index = (frame_index + 1) % len(ANIMATION_FRAMES)
            
        except Exception as e:
            # အသုံးပြုသူက Menu ကို ဖျက်လိုက်လျှင် သို့မဟုတ် Error တက်လျှင် Loop အား ရပ်တန့်ရန်
            break

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

# ၁။ /start command (ခလုတ်အရှင်များ စတင်မည့်နေရာ)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    guide = (
        "⚔️ **Welcome to Premium Game Checker Bot** ⚔️\n\n"
        "Select the game you want to check from the buttons below:\n\n"
        "⚡ _Powered by High-Speed API Automation_"
    )
    
    markup = InlineKeyboardMarkup()
    btn_ml = InlineKeyboardButton("Mobile Legends 🎮", callback_data="info_ml")
    btn_ff = InlineKeyboardButton("Garena Free Fire 🔥", callback_data="info_ff")
    btn_brand = InlineKeyboardButton("✨ [ 𝑷𝒂𝒚𝑿-𝑴𝑴 ] ✨", callback_data="brand_click")
    
    markup.row(btn_ml, btn_ff)
    markup.row(btn_brand)
    
    sent_msg = bot.send_message(message.chat.id, guide, parse_mode="Markdown", reply_markup=markup)
    
    # 🧵 စာသားအရှင်ပြေးစေရန် သီးသန့် Background Thread တစ်ခု ချက်ချင်းမောင်းနှင်ခြင်း
    threading.Thread(
        target=animate_start_menu, 
        args=(message.chat.id, sent_msg.message_id), 
        daemon=True
    ).start()

# Button Callback Handler
@bot.callback_query_handler(func=lambda call: True)
def callback_game_info(call):
    bot.answer_callback_query(call.id)
    
    if call.data == "info_ml":
        text = (
            "🎮 **MOBILE LEGENDS CHECKER**\n\n"
            "Please send your ID exactly in this bracket format:\n"
            "`/ml [User_ID] ([Zone_ID])`\n\n"
            "💡 **Example:**\n"
            "`/ml 2112723799 (19915)`"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
        
    elif call.data == "info_ff":
        text = (
            "🔥 **FREE FIRE CHECKER**\n\n"
            "Please send the ID in this format:\n"
            "`/ff [Player_UID]`\n\n"
            "💡 **Example:**\n"
            "`/ff 182200303107200135203`"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
        
    elif call.data == "brand_click":
        bot.send_message(call.message.chat.id, "🚀 **PayX-MM ID Checker Automation System is Fully Active!**")

# ၂။ /ml Command Handler
@bot.message_handler(commands=['ml'])
def handle_ml_check(message):
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
        bot.edit_message_text(f"❌ **Error:** `{error}`\n\n🛠️ Developer: `𝑷𝒂𝒚𝑿-𝑴𝑴`", message.chat.id, status_msg.message_id, parse_mode="Markdown")
        return
        
    if result:
        nickname = result.get("nickname") or result.get("name") or result.get("username") or result.get("userName") or result.get("player_name")
        raw_region = result.get("region") or result.get("country") or result.get("zone_name") or result.get("zoneName") or result.get("region_code")
        
        if not nickname:
            for key in ["data", "result", "player"]:
                if key in result and isinstance(result[key], dict):
                    inner = result[key]
                    nickname = inner.get("nickname") or inner.get("name") or inner.get("username") or inner.get("userName") or inner.get("player_name")
                    raw_region = raw_region or inner.get("region") or inner.get("country") or inner.get("zone_name")
                    break

        if not nickname:
            nickname = "In-game Hidden / VIP"
            
        pretty_region = get_pretty_country(raw_region)
            
        cool_ui = (
            "🎮 **MOBILE LEGENDS PROFILE** 🎮\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 **Player Name :** `{nickname}`\n"
            f"🌐 **Region/Zone  :** `{pretty_region}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 **User ID :** `{user_id}`\n"
            f"📁 **Zone ID :** `{zone_id}`\n\n"
            f"💫 *Verified via 𝑷𝒂𝒚𝑿-𝑴𝑴 Automation*"
        )
        bot.edit_message_text(cool_ui, message.chat.id, status_msg.message_id, parse_mode="Markdown")

# ၃။ /ff Command Handler
@bot.message_handler(commands=['ff'])
def handle_ff_check(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ **Invalid FF Format!**\n\nUse: `/ff [Player_UID]`", parse_mode="Markdown")
        return
        
    player_id = args[1]
    status_msg = bot.reply_to(message, "⏳ *Scanning Garena Free Fire Data...*", parse_mode="Markdown")
    result, error = check_ff_id(player_id)
    
    if error:
        bot.edit_message_text(f"❌ **Error:** `{error}`\n\n🛠️ Developer: `𝑷𝒂𝒚𝑿-𝑴𝑴`", message.chat.id, status_msg.message_id, parse_mode="Markdown")
        return
        
    if result:
        nickname = result.get("nickname") or result.get("username") or result.get("name") or result.get("player_name") or "Unknown Player"
        
        if nickname == "Unknown Player" and "data" in result and isinstance(result["data"], dict):
            nickname = result["data"].get("nickname") or result["data"].get("username") or result["data"].get("name") or "Unknown Player"
            
        cool_ui = (
            "🔥 **GARENA FREE FIRE PROFILE** 🔥\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 **Player Name :** `{nickname}`\n"
            f"🆔 **Player UID   :** `{player_id}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💫 *Verified via 𝑷𝒂𝒚𝑿-𝑴𝑴 Automation*"
        )
        bot.edit_message_text(cool_ui, message.chat.id, status_msg.message_id, parse_mode="Markdown")

# =====================================================================
# 4. Main Runner
# =====================================================================
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("Multi-Game Telebot Server is Live with Text Animation...")
    bot.infinity_polling()
