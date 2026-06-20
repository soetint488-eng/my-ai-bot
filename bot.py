import os
import sys
import re
import time
import hashlib
import threading
import requests
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# =====================================================================
# FLASK WEB SERVER (PORT: 8000)
# =====================================================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "200 OK - PayX-MM Core Nitro Engine Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host="0.0.0.0", port=port)

# =====================================================================
# CORE CONFIGURATION & CREDENTIALS
# =====================================================================
BOT_TOKEN = "8761954371:AAEwo75dbsAWpvxavxqWr3UbhjeRwknlWnI"
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"
RAPIDAPI_HOST = "id-game-checker.p.rapidapi.com"

OWNER_ID = 8584422107
ADMINS = {OWNER_ID}

bot = telebot.TeleBot(BOT_TOKEN)
BRANDING = "PAYX-MM NITRO"

# Datastores (In-Memory Database Sync)
USER_KEYS = {}        # { user_id: { "key": str, "generated_at": float } }
BANNED_KEYS = set()   # { user_id (banned from using keys) }
MUTED_USERS = set()

COOLDOWN_LIMIT = 3 * 60 * 60  # 3 Hours Premium Gate Cooldown Metric

# =====================================================================
# FAST UI ANIMATION ENGINE (CLEAN FRAMES)
# =====================================================================
FAST_FRAMES = [
    "[ P ]", "[ PA ]", "[ PAY ]", "[ PAYX ]", 
    "[ PAYX- ]", "[ PAYX-M ]", "[ PAYX-MM ]"
]

def run_fast_loading(chat_id, message_id):
    try:
        for frame in FAST_FRAMES:
            bot.edit_message_text(frame, chat_id, message_id)
            time.sleep(0.08)
    except Exception: pass

# =====================================================================
# DYNAMIC ROLE KEYBOARD SYSTEM
# =====================================================================
def get_dynamic_keyboard(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    if user_id in ADMINS:
        btn_adm_panel = KeyboardButton("RED MATRIX PANEL (ADMIN ONLY)")
        markup.add(btn_adm_panel)
    else:
        # Key ထုတ်သည့် နေရာတစ်ခုတည်းတွင်သာ 🎁 Emoji ကို ခွင့်ပြုထားပါသည်
        btn_free_key = KeyboardButton("🎁 Get Free Key (3 Hours)")
        markup.add(btn_free_key)
        
    return markup

@bot.message_handler(commands=['start'])
def handle_start_command(message):
    user_id = message.from_user.id
    
    welcome_text = (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"WELCOME TO {BRANDING}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Hi {message.from_user.first_name or 'User'},\n"
        f"I am fully ready to parse and fetch your game profiles instantly!\n\n"
        f"Input Format: Send game data directly (e.g., 2112723799 (19915))\n"
        f"System auto-detected your role access matrix panel below."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_dynamic_keyboard(user_id))

# =====================================================================
# 🎁 FREE USER 3-HOURS KEY GENERATOR LOGIC
# =====================================================================
@bot.message_handler(func=lambda msg: msg.text == "🎁 Get Free Key (3 Hours)")
def generate_free_access_key(message):
    user_id = message.from_user.id
    current_time = time.time()
    
    if user_id in BANNED_KEYS:
        return bot.reply_to(message, "Access Denied: Your key generation privileges have been suspended by admin.", parse_mode="Markdown")
        
    # Check 3-Hours Time Cooldown Limitation
    if user_id in USER_KEYS:
        last_generated = USER_KEYS[user_id]["generated_at"]
        elapsed_time = current_time - last_generated
        
        if elapsed_time < COOLDOWN_LIMIT:
            remaining_seconds = int(COOLDOWN_LIMIT - elapsed_time)
            hours = remaining_seconds // 3600
            minutes = (remaining_seconds % 3600) // 60
            
            buy_markup = InlineKeyboardMarkup()
            btn_buy = InlineKeyboardButton(text="Owner Request (Buy Premium)", url="https://t.me/PayX_MM?text=key%20ဝယ်ချင်လို့ပါ")
            buy_markup.add(btn_buy)
            
            return bot.send_message(
                message.chat.id, 
                f"🎁 Cooldown Active: You can generate your next free key in {hours}h {minutes}m.\n\nWant to bypass limitation with stable authorization?", 
                parse_mode="Markdown", 
                reply_markup=buy_markup
            )

    # Generate MD5 Token Array
    raw_token = f"PAYX-{user_id}-{current_time}"
    generated_key = "PX-" + hashlib.md5(raw_token.encode()).hexdigest()[:12].upper()
    
    USER_KEYS[user_id] = {
        "key": generated_key,
        "generated_at": current_time,
        "username": message.from_user.username or "None",
        "first_name": message.from_user.first_name
    }
    
    success_msg = (
        f"🎁 SUCCESSFULLY GENERATED KEY 🎁\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Key: {generated_key}\n"
        f"Status: Active for next 3 Hours\n"
        f"Scope: MLBB Verification Unlocked\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Tap key block to instantly copy your key."
    )
    bot.reply_to(message, success_msg, parse_mode="Markdown")
    
    # Admin Log Monitor Notification
    admin_alert = (
        f"NEW KEY ISSUED\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"User: {message.from_user.first_name}\n"
        f"ID: {user_id}\n"
        f"User Name: @{message.from_user.username or 'None'}\n"
        f"Token generated: {generated_key}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    try: bot.send_message(OWNER_ID, admin_alert, parse_mode="Markdown")
    except Exception: pass

# =====================================================================
# ADMIN PANEL CONTROL DASHBOARD
# =====================================================================
@bot.message_handler(func=lambda msg: msg.text == "RED MATRIX PANEL (ADMIN ONLY)")
def trigger_admin_dashboard_from_keyboard(message):
    if message.from_user.id not in ADMINS: return
    
    admin_text = (
        f"PAYX-MM RED COMMAND DASHBOARD\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Welcome Supreme Commander. Manage temporary keys, ban regulations and parameters below:"
    )
    
    markup = InlineKeyboardMarkup()
    btn_check = InlineKeyboardButton("Check Key Users (Active)", callback_data="adm_check_keys")
    btn_ban = InlineKeyboardButton("Ban Key Privileges", callback_data="adm_ban_prompt")
    btn_unban = InlineKeyboardButton("Unban Key Privileges", callback_data="adm_unban_prompt")
    btn_close = InlineKeyboardButton("Dismiss Panel", callback_data="delete_msg")
    
    markup.row(btn_check)
    markup.row(btn_ban, btn_unban)
    markup.row(btn_close)
    
    bot.send_message(message.chat.id, admin_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_") or call.data == "delete_msg")
def admin_callback_processor(call):
    if call.data == "delete_msg":
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        return

    if call.from_user.id not in ADMINS: return

    bot.answer_callback_query(call.id)
    
    if call.data == "adm_check_keys":
        if not USER_KEYS:
            bot.send_message(call.message.chat.id, "No keys are currently recorded in volatile active memory.")
            return
            
        report = "ACTIVE KEY REALTIME USERS:\n━━━━━━━━━━━━━━━━━━━━━━\n"
        for uid, data in USER_KEYS.items():
            report += f"User: {data['first_name']} ({uid}) -> Key: {data['key']}\n"
        bot.send_message(call.message.chat.id, report, parse_mode="Markdown")
        
    elif call.data == "adm_ban_prompt":
        msg = bot.send_message(call.message.chat.id, "Please reply to this message or type the User ID to BAN from key system:")
        bot.register_next_step_handler(msg, process_ban_action)
        
    elif call.data == "adm_unban_prompt":
        msg = bot.send_message(call.message.chat.id, "Please reply to this message or type the User ID to UNBAN from key system:")
        bot.register_next_step_handler(msg, process_unban_action)

def process_ban_action(message):
    try:
        target_id = int(message.text.strip())
        BANNED_KEYS.add(target_id)
        USER_KEYS.pop(target_id, None)
        bot.reply_to(message, f"Target {target_id} successfully blacklisted from generating keys.", parse_mode="Markdown")
    except ValueError:
        bot.reply_to(message, "Invalid syntax. Please output numerical profile IDs only.")

def process_unban_action(message):
    try:
        target_id = int(message.text.strip())
        BANNED_KEYS.discard(target_id)
        bot.reply_to(message, f"Target {target_id} successfully reinstated to system infrastructure.", parse_mode="Markdown")
    except ValueError:
        bot.reply_to(message, "Invalid syntax. Please output numerical profile IDs only.")

# =====================================================================
# MULTI-GAME ROUTER & REGION PARSER
# =====================================================================
def call_game_api(game_type, main_id, extra_id=None):
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY, 
        "Content-Type": "application/json",
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    
    if game_type == "mlbb":
        url = f"https://{RAPIDAPI_HOST}/mobile-legends/{main_id}/{extra_id}"
    elif game_type == "ff":
        url = f"https://{RAPIDAPI_HOST}/ff-global/{main_id}"
    elif game_type == "pubg":
        url = f"https://{RAPIDAPI_HOST}/pubgm-global/{main_id}"
    elif game_type == "coc":
        url = f"https://{RAPIDAPI_HOST}/coc/{main_id}"
        
    try:
        r = requests.get(url, headers=headers, timeout=12)
        if r.status_code != 200: return None
        return r.json()
    except Exception: return None

def check_user_key_validity(user_id):
    if user_id in ADMINS: return True
    if user_id not in USER_KEYS: return False
    
    elapsed = time.time() - USER_KEYS[user_id]["generated_at"]
    if elapsed > COOLDOWN_LIMIT:
        USER_KEYS.pop(user_id, None)
        return False
    return True

def process_and_build_ui(message, game_type, main_id, extra_id=None):
    user_id = message.from_user.id
    
    # Key မရှိလျှင်/သက်တမ်းကုန်လျှင် စစ်ခွင့်မပြုခြင်း
    if not check_user_key_validity(user_id):
        buy_markup = InlineKeyboardMarkup()
        buy_markup.add(InlineKeyboardButton(text="Owner Request (Buy Premium)", url="https://t.me/PayX_MM?text=key%20ဝယ်ချင်လို့ပါ"))
        bot.reply_to(message, "Access Blocked: You need an active key to parse data frames.\nClick button below to purchase or generate key from dashboard.", parse_mode="Markdown", reply_markup=buy_markup)
        return

    # Free Key သမားအတွက် MLBB မှလွဲ၍ ကျန်ဂိမ်းများကို Lock ချခြင်း
    if user_id not in ADMINS and game_type != "mlbb":
        buy_markup = InlineKeyboardMarkup()
        buy_markup.add(InlineKeyboardButton(text="Owner Request (Unlock Premium)", url="https://t.me/PayX_MM?text=key%20ဝယ်ချင်လို့ပါ"))
        bot.reply_to(message, f"PREMIUM FEATURE:\n{game_type.upper()} parsing infrastructure is strictly reserved for Premium Subscribers only.", parse_mode="Markdown", reply_markup=buy_markup)
        return

    status_msg = bot.reply_to(message, "PROCESSING MATRIX FRAME...")
    threading.Thread(target=run_fast_loading, args=(message.chat.id, status_msg.message_id), daemon=True).start()
    
    raw_data = call_game_api(game_type, main_id, extra_id)
    
    if not raw_data:
        bot.edit_message_text("API Transmission Interrupted or Account Invalid.", message.chat.id, status_msg.message_id, parse_mode="Markdown")
        return
        
    nickname = raw_data.get("nickname") or raw_data.get("username") or raw_data.get("name")
    if not nickname:
        for key in ["data", "result"]:
            if key in raw_data and isinstance(raw_data[key], dict):
                inner = raw_data[key]
                nickname = inner.get("nickname") or inner.get("username") or inner.get("name")
                break
    nickname = nickname or "Unknown Player"
    
    region = raw_data.get("region") or raw_data.get("country") or raw_data.get("zone")
    if not region:
        for key in ["data", "result", "meta"]:
            if key in raw_data and isinstance(raw_data[key], dict):
                inner = raw_data[key]
                region = inner.get("region") or inner.get("country") or inner.get("area") or inner.get("zone_id")
                break
    region = region or "Global Server"

    payload_data = f"NAME  : {nickname}\nID    : {main_id}\nREGION: {region}"
    if extra_id:
        payload_data = f"NAME  : {nickname}\nID    : {main_id} ({extra_id})\nREGION: {region}"

    cool_neon_ui = (
        f"NEON MATRIX RESULT\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"```\n"
        f"{payload_data}\n"
        f"```\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Tap dark code block area above to auto copy instantly"
    )
    
    markup = InlineKeyboardMarkup()
    btn_delete = InlineKeyboardButton(text="Delete Result", callback_data="delete_msg")
    markup.row(btn_delete)
    
    try:
        bot.edit_message_text(cool_neon_ui, message.chat.id, status_msg.message_id, parse_mode="Markdown", reply_markup=markup)
    except Exception: pass

# =====================================================================
# TEXT LOOKUP LISTENER
# =====================================================================
@bot.message_handler(func=lambda message: True, content_types=['text'])
def advanced_text_router(message):
    if message.text.startswith('/'): return
    
    text_clean = message.text.strip()
    
    ml_match = re.search(r'^(\d+)\s*[\(\[]\s*(\d+)\s*[\)\]]$', text_clean)
    if ml_match:
        process_and_build_ui(message, "mlbb", ml_match.group(1), ml_match.group(2))
        return

    coc_match = re.search(r'^#?([A-Z0-9]{7,14})$', text_clean, re.IGNORECASE)
    if coc_match and not text_clean.isdigit():
        process_and_build_ui(message, "coc", coc_match.group(1).upper())
        return

    if text_clean.isdigit():
        val_len = len(text_clean)
        if 8 <= val_len <= 10:
            process_and_build_ui(message, "ff", text_clean)
        elif 11 <= val_len <= 13:
            process_and_build_ui(message, "pubg", text_clean)
        else:
            bot.reply_to(message, "System Warning: Digit scope length anomaly. Verify input structures.")
        return

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
