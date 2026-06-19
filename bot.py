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
# Bot Configuration (ပုံပါ RapidAPI Key အသစ်ဖြင့် လဲလှယ်ထားသည်)
# =====================================================================
BOT_TOKEN = "8761954371:AAE3NExXJOGJa1D3Lp1aN2t6F_yA8h2imOo"
RAPIDAPI_KEY = "06b1562a59msh39810b847e9d0e2p151fd6jsn3a9d60ae50a9"

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
    frame_index = 0
    while True:
        try:
            time.sleep(2.0)
            current_text = BLINK_FRAMES[frame_index]
            
            markup = InlineKeyboardMarkup()
            btn_ml = InlineKeyboardButton("🎮 Mobile Legends", callback_data="info_ml")
            btn_ff = InlineKeyboardButton("🔥 Free Fire", callback_data="info_ff")
            btn_pubg = InlineKeyboardButton("🔫 PUBG Mobile", callback_data="info_pubg")
            btn_coc = InlineKeyboardButton("🏰 Clash of Clans", callback_data="info_coc")
            btn_brand = InlineKeyboardButton(current_text, callback_data="brand_click")
            
            markup.row(btn_ml, btn_ff)
            markup.row(btn_pubg, btn_coc)
            markup.row(btn_brand)
            
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)
            frame_index = (frame_index + 1) % len(BLINK_FRAMES)
            
        except Exception:
            break

# =====================================================================
# ⌨️ INTRO TYPEWRITER & ERASE CORE
# =====================================================================
def run_start_intro_animation(chat_id, initial_msg_id):
    typing_steps = [
        "⏳ 𝑷...", "⏳ 𝑷𝒂...", "⏳ 𝑷𝒂𝒚...", "⏳ 𝑷𝒂𝒚𝑿...", 
        "⏳ 𝑷𝒂𝒚𝑿-...", "⏳ 𝑷𝒂𝒚𝑿-𝑴...", "✨ 𝑷𝒂𝒚𝑿-𝑴𝑴 💫"
    ]
    for step in typing_steps:
        try:
            bot.edit_message_text(f"`{step}`", chat_id, initial_msg_id, parse_mode="Markdown")
            time.sleep(0.25)
        except Exception:
            pass
            
    time.sleep(0.6)
    
    erase_steps = [
        "⏳ 𝑷𝒂𝒚𝑿-𝑴...", "⏳ 𝑷𝒂𝒚𝑿-...", "⏳ 𝑷𝒂𝒚𝑿...", 
        "⏳ 𝑷𝒂𝒚...", "⏳ 𝑷...", "⏳ System Loading..."
    ]
    for step in erase_steps:
        try:
            bot.edit_message_text(f"`{step}`", chat_id, initial_msg_id, parse_mode="Markdown")
            time.sleep(0.15)
        except Exception:
            pass

    time.sleep(0.3)

    guide = (
        "⚔️ **PREMIUM AUTOMATION ID CHECKER** ⚔️\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Welcome! Select your target platform to get account database details:\n\n"
        "⚙️ _Status: Multi-Host Core Routing Active_"
    )
    
    markup = InlineKeyboardMarkup()
    btn_ml = InlineKeyboardButton("🎮 Mobile Legends", callback_data="info_ml")
    btn_ff = InlineKeyboardButton("🔥 Free Fire", callback_data="info_ff")
    btn_pubg = InlineKeyboardButton("🔫 PUBG Mobile", callback_data="info_pubg")
    btn_coc = InlineKeyboardButton("🏰 Clash of Clans", callback_data="info_coc")
    btn_brand = InlineKeyboardButton("⚡ [  𝑷𝒂𝒚𝑿-𝑴𝑴  ] ⚡", callback_data="brand_click")
    
    markup.row(btn_ml, btn_ff)
    markup.row(btn_pubg, btn_coc)
    markup.row(btn_brand)
    
    try:
        bot.edit_message_text(guide, chat_id, initial_msg_id, parse_mode="Markdown", reply_markup=markup)
        threading.Thread(target=animate_start_menu, args=(chat_id, initial_msg_id), daemon=True).start()
    except Exception:
        pass

# =====================================================================
# 🎯 API DYNAMIC ROUTER
# =====================================================================
def call_game_api(game_type, target_id):
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "Content-Type": "application/json"
    }
    
    if game_type == "mlbb":
        url = f"https://id-game-checker.p.rapidapi.com/mobile-legends/{target_id}"
        headers["x-rapidapi-host"] = "id-game-checker.p.rapidapi.com"
    elif game_type == "ff":
        url = f"https://check-id-game.p.rapidapi.com/api/rapid_api/ff_idgame/{target_id}"
        headers["x-rapidapi-host"] = "check-id-game.p.rapidapi.com"
    elif game_type == "pubg":
        url = f"https://check-id-game.p.rapidapi.com/api/rapid_api/cekpubgmobile/{target_id}"
        headers["x-rapidapi-host"] = "check-id-game.p.rapidapi.com"
    elif game_type == "coc":
        url = f"https://id-game-checker.p.rapidapi.com/coc/{target_id}"
        headers["x-rapidapi-host"] = "id-game-checker.p.rapidapi.com"
        
    try:
        r = requests.get(url, headers=headers, timeout=12)
        if r.status_code != 200: return None, f"Status {r.status_code}"
        return r.json(), None
    except Exception as e: return None, str(e)

# =====================================================================
# Bot Handlers & UI (Font Error ကင်းစင်အောင် ပြင်ဆင်ပြီး)
# =====================================================================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    sent_msg = bot.send_message(message.chat.id, "`⏳ Connecting...`", parse_mode="Markdown")
    threading.Thread(target=run_start_intro_animation, args=(message.chat.id, sent_msg.message_id), daemon=True).start()

@bot.callback_query_handler(func=lambda call: True)
def callback_game_info(call):
    bot.answer_callback_query(call.id)
    if call.data == "info_ml":
        bot.send_message(call.message.chat.id, "🎮 **MOBILE LEGENDS QUERY**\n\nFormat:\n`/ml [User_ID] ([Zone_ID])`\n\n💡 **Example:**\n`/ml 2112723799 (19915)`", parse_mode="Markdown")
    elif call.data == "info_ff":
        bot.send_message(call.message.chat.id, "🔥 **FREE FIRE QUERY**\n\nFormat:\n`/ff [Player_UID]`\n\n💡 **Example:**\n`/ff 11944852314`", parse_mode="Markdown")
    elif call.data == "info_pubg":
        bot.send_message(call.message.chat.id, "🔫 **PUBG MOBILE QUERY**\n\nFormat:\n`/pubg [Character_ID]`\n\n💡 **Example:**\n`/pubg 5930748140`", parse_mode="Markdown")
    elif call.data == "info_coc":
        bot.send_message(call.message.chat.id, "🏰 **CLASH OF CLANS QUERY**\n\nFormat:\n`/coc [Player_Tag]`\n\n💡 **Example:**\n`/coc 20C0RVGL`", parse_mode="Markdown")
    elif call.data == "brand_click":
        bot.send_message(call.message.chat.id, f"🚀 **{BRANDING} Multi-Platform Identity Engine v4.0**")

def parse_and_send_result(message, game_type, target_id, extra_id=None):
    display_id = f"{target_id} ({extra_id})" if extra_id else target_id
    api_query_id = f"{target_id}/{extra_id}" if extra_id else target_id
    
    status_msg = bot.reply_to(message, "🛸 *Infiltrating central server database...*", parse_mode="Markdown")
    result, error = call_game_api(game_type, api_query_id)
    
    if error:
        bot.edit_message_text(f"❌ **Error:** `{error}`\n\n🛠️ Developer: {BRANDING}", message.chat.id, status_msg.message_id, parse_mode="Markdown")
        return
        
    if result:
        nickname = result.get("nickname") or result.get("username") or result.get("name")
        raw_region = result.get("region") or result.get("country") or result.get("country_code") or result.get("zone_name")
        
        if not nickname:
            for key in ["data", "result"]:
                if key in result and isinstance(result[key], dict):
                    inner = result[key]
                    nickname = inner.get("nickname") or inner.get("username") or inner.get("name") or inner.get("userName")
                    raw_region = raw_region or inner.get("region") or inner.get("country")
                    break
                    
        nickname = nickname or "Hidden / VIP Account"
        pretty_region = get_pretty_country(raw_region)
        
        titles = {"mlbb": "🎮 MOBILE LEGENDS PROFILE", "ff": "🔥 Garena Free Fire Profile", "pubg": "🔫 PUBG MOBILE GLOBAL Profile", "coc": "🏰 CLASH OF CLANS PROFILE"}
        systems = {"mlbb": "Moonton Live Link", "ff": "Garena Core Database", "pubg": "Tencent Live Core", "coc": "Supercell Live Core"}
        id_labels = {"mlbb": "User ID & Zone", "ff": "Player UID", "pubg": "Character ID", "coc": "Player Tag"}
        
        # 🛠️ FONT ERROR FIX: စာလုံးအစောင်းကွက်များကို Standard Text ပုံစံသို့ ပြောင်းလဲထားပါသည်
        cool_ui = (
            f"👑 **{titles[game_type]}** 👑\n"
            f"🧬 System: {systems[game_type]}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 **Player Name :** `{nickname}`\n"
            f"🌐 **Region / Country :** `{pretty_region}`\n"
            f"🆔 **{id_labels[game_type]} :** `{display_id}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛸 **Query Verified By :** {BRANDING}"
        )
        
        bot.edit_message_text(cool_ui, message.chat.id, status_msg.message_id, parse_mode="Markdown")

# Commands routing
@bot.message_handler(commands=['ml'])
def handle_ml(message):
    match = re.search(r'/ml\s+(\d+)\s*\((.*?)\)', message.text)
    if not match: return bot.reply_to(message, "⚠️ **Invalid MLBB Format!**\nUse: `/ml 2112723799 (19915)`", parse_mode="Markdown")
    parse_and_send_result(message, "mlbb", match.group(1), match.group(2).strip())

@bot.message_handler(commands=['ff'])
def handle_ff(message):
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "⚠️ **Invalid FF Format!**\nUse: `/ff [UID]`", parse_mode="Markdown")
    parse_and_send_result(message, "ff", args[1])

@bot.message_handler(commands=['pubg'])
def handle_pubg(message):
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "⚠️ **Invalid PUBG Format!**\nUse: `/pubg [ID]`", parse_mode="Markdown")
    parse_and_send_result(message, "pubg", args[1])

@bot.message_handler(commands=['coc'])
def handle_coc(message):
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "⚠️ **Invalid COC Format!**\nUse: `/coc [Player_Tag]`", parse_mode="Markdown")
    player_tag = args[1].replace("#", "").strip()
    parse_and_send_result(message, "coc", player_tag)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
