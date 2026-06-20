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
    return "200 OK - PayX-MM Core Engine Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host="0.0.0.0", port=port)

# =====================================================================
# CORE CONFIGURATION & CREDENTIALS
# =====================================================================
BOT_TOKEN = "8761954371:AAE3NExXJOGJa1D3Lp1aN2t6F_yA8h2imOo"
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"
RAPIDAPI_HOST = "id-game-checker.p.rapidapi.com"

# 👥 DUAL OWNERS HARDCODED SETUP
OWNERS = {8584422107, 8033904689}

# In-Memory Databases
ADMINS = set()       
USER_LANG = {}       
USER_KEYS = {}       
BANNED_USERS = set() 
COOLDOWN_LIMIT = 3 * 60 * 60

bot = telebot.TeleBot(BOT_TOKEN)
BRANDING = "PAYX-MM NITRO"

# =====================================================================
# MULTI-LANGUAGE TRANSLATION MATRIX
# =====================================================================
STRINGS = {
    "EN": {
        "welcome": "━━━━━━━━━━━━━━━━━━━━━━\n🤖 *WELCOME TO PAYX-MM*\n━━━━━━━━━━━━━━━━━━━━━━\nHi {name},\nI am ready to fetch your game profiles instantly!\n\n💡 *Available Commands:* \n🔹 `/ml`, `/Go`, `/ff`, `/cc`, `/Pg`, `/Hok`, `/Bl`",
        "processing": "⚡ PROCESSING MATRIX FRAME...",
        "api_error": "❌ API Transmission Interrupted or Account Invalid.",
        "premium_locked": "🔒 PREMIUM FEATURE:\nThis game structure is reserved for Premium/Admins only.",
        "banned": "🚫 Access Denied: Suspended by system administration.",
        "cooldown": "🎁 *Cooldown Active*: Next free key available in `{hours}h {minutes}m`.",
        "key_success": "🎁 *SUCCESSFULLY GENERATED KEY*\n━━━━━━━━━━━━━━━━━━━━━━\nKey: `{key}`\nStatus: Active for 3 Hours\n━━━━━━━━━━━━━━━━━━━━━━\nTap to copy. Select action below:",
        "access_blocked": "❌ Access Blocked: You need an active key or premium subscription.",
        "admin_only": "❌ Access Denied: Executive clearance required."
    },
    "MM": {
        "welcome": "━━━━━━━━━━━━━━━━━━━━━━\n🤖 *PAYX-MM MM မှ ကြိုဆိုပါတယ်ဗျာ*\n━━━━━━━━━━━━━━━━━━━━━━\nမင်္ဂလာပါ {name},\nဂိမ်း ID များကို အချိန်မဆိုင်းဘဲ ချက်ချင်း ရှာဖွေပေးနိုင်ပါပြီခင်ဗျာ!\n\n💡 *အသုံးပြုနိုင်သော Commands များ:* \n🔹 `/ml`, `/Go`, `/ff`, `/cc`, `/Pg`, `/Hok`, `/Bl`",
        "processing": "⚡ ဒေတာများကို ရှာဖွေစစ်ဆေးနေပါသည်...",
        "api_error": "❌ API ချိတ်ဆက်မှုပြတ်တောက်သွားခြင်း သို့မဟုတ် ID မှားယွင်းနေပါသည်။",
        "premium_locked": "🔒 ပရီမီယမ်လုပ်ဆောင်ချက်:\nဤဂိမ်းအား စစ်ဆေးရန် ပရီမီယမ် သို့မဟုတ် Admin အဆင့်ရှိရန် လိုအပ်ပါသည်။",
        "banned": "🚫 အသုံးပြုခွင့်ပိတ်ပင်ခံထားရပါသည်: စနစ်ထိန်းချုပ်သူမှ သင့်အား ပိတ်ထားပါသည်။",
        "cooldown": "🎁 *စောင့်ဆိုင်းရန်လိုအပ်သည်*: နောက်ထပ် Key အခမဲ့ရယူရန် `{hours}နာရီ {minutes}မိနစ်` စောင့်ဆိုင်းပေးပါ။",
        "key_success": "🎁 *အခမဲ့ဝင်ရောက်ခွင့် Key ထုတ်ယူမှု အောင်မြင်သည်*\n━━━━━━━━━━━━━━━━━━━━━━\nသော့ချက်ကုဒ်: `{key}`\nသက်တမ်း: လာမည့် ၃ နာရီအထိ အသုံးပြုနိုင်သည်\n━━━━━━━━━━━━━━━━━━━━━━\nစာသားကိုနှိပ်၍ Copy ယူပါ။ အောက်ပါ Dashboard ကိုအသုံးပြုပါ-",
        "access_blocked": "❌ ဝင်ရောက်ခွင့်ပိတ်ထားပါသည်: အသုံးပြုရန် Key မရှိပါ သို့မဟုတ် ပရီမီယမ်ဝယ်ယူပါ။",
        "admin_only": "❌ လုပ်ဆောင်ခွင့်မရှိပါ: ဤလုပ်ဆောင်ချက်သည် စနစ်ပိုင်ရှင်များသာ ဖြစ်သည်။"
    }
}

def get_txt(user_id, key):
    lang = USER_LANG.get(user_id, "EN")
    return STRINGS[lang].get(key, STRINGS["EN"][key])

# =====================================================================
# FAST UI ANIMATION ENGINE
# =====================================================================
FAST_FRAMES = ["[ P ]", "[ PA ]", "[ PAY ]", "[ PAYX ]", "[ PAYX-MM ]"]

def run_fast_loading(chat_id, message_id, stop_event):
    try:
        for frame in FAST_FRAMES:
            if stop_event.is_set(): break
            bot.edit_message_text(frame, chat_id, message_id)
            time.sleep(0.08)
    except Exception: pass

# =====================================================================
# DYNAMIC KEYBOARD UI
# =====================================================================
def get_dynamic_keyboard(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    lang_text = "🌐 Language: MM" if USER_LANG.get(user_id, "EN") == "EN" else "🌐 Language: EN"
    btn_lang = KeyboardButton(lang_text)
    
    if user_id in OWNERS:
        btn_adm_panel = KeyboardButton("👑 RED MATRIX PANEL")
        markup.add(btn_adm_panel, btn_lang)
    else:
        btn_free_key = KeyboardButton("🎁 Get Free Key (3 Hours)")
        markup.add(btn_free_key, btn_lang)
    return markup

def get_game_check_panel(user_id):
    markup = InlineKeyboardMarkup()
    lang = USER_LANG.get(user_id, "EN")
    is_authorized = (user_id in OWNERS or user_id in ADMINS)

    if is_authorized:
        markup.row(InlineKeyboardButton("🟢 Mobile Legends", callback_data="chk_mlbb"), InlineKeyboardButton("🟢 Magic Chess Go", callback_data="chk_mcgg"))
        markup.row(InlineKeyboardButton("🟢 Honor of Kings", callback_data="chk_hok"), InlineKeyboardButton("🟢 Blood Strike", callback_data="chk_bs"))
        markup.row(InlineKeyboardButton("🟢 Clash of Clans", callback_data="chk_coc"))
        markup.row(InlineKeyboardButton("🟢 Free Fire", callback_data="chk_ff"), InlineKeyboardButton("🟢 PUBG Mobile", callback_data="chk_pubg"))
    else:
        markup.row(InlineKeyboardButton("🟢 Mobile Legends", callback_data="chk_mlbb"), InlineKeyboardButton("🟢 Magic Chess Go", callback_data="chk_mcgg"))
        markup.row(InlineKeyboardButton(f"🔒 HOK ({'Locked' if lang=='EN' else 'သော့ခတ်ထား'})", callback_data="game_locked"))
        markup.row(InlineKeyboardButton(f"🔒 Blood Strike ({'Locked' if lang=='EN' else 'သော့ခတ်ထား'})", callback_data="game_locked"))
        markup.row(InlineKeyboardButton(f"🔒 Clash of Clans ({'Locked' if lang=='EN' else 'သော့ခတ်ထား'})", callback_data="game_locked"))
        markup.row(InlineKeyboardButton(f"🔒 Free Fire ({'Locked' if lang=='EN' else 'သော့ခတ်ထား'})", callback_data="game_locked"), InlineKeyboardButton(f"🔒 PUBG Mobile ({'Locked' if lang=='EN' else 'သော့ခတ်ထား'})", callback_data="game_locked"))
    
    return markup

@bot.message_handler(commands=['start'])
def handle_start_command(message):
    user_id = message.from_user.id
    if user_id not in USER_LANG: USER_LANG[user_id] = "EN"
    welcome_text = get_txt(user_id, "welcome").format(name=message.from_user.first_name or 'User')
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_dynamic_keyboard(user_id))

@bot.message_handler(func=lambda msg: msg.text in ["🌐 Language: MM", "🌐 Language: EN"])
def toggle_language_swap(message):
    user_id = message.from_user.id
    current_lang = USER_LANG.get(user_id, "EN")
    USER_LANG[user_id] = "MM" if current_lang == "EN" else "EN"
    
    confirm_txt = "🌐 Language changed to English!" if USER_LANG[user_id] == "EN" else "🌐 ဘာသာစကားအား မြန်မာလို ပြောင်းလဲလိုက်ပါပြီ။"
    bot.send_message(message.chat.id, confirm_txt, reply_markup=get_dynamic_keyboard(user_id))

@bot.message_handler(func=lambda msg: msg.text == "🎁 Get Free Key (3 Hours)")
def generate_free_access_key(message):
    user_id = message.from_user.id
    current_time = time.time()
    
    if user_id in BANNED_USERS:
        return bot.reply_to(message, get_txt(user_id, "banned"), parse_mode="Markdown")
        
    if user_id in USER_KEYS:
        last_generated = USER_KEYS[user_id]["generated_at"]
        elapsed_time = current_time - last_generated
        
        if elapsed_time < COOLDOWN_LIMIT:
            remaining_seconds = int(COOLDOWN_LIMIT - elapsed_time)
            hours = remaining_seconds // 3600
            minutes = (remaining_seconds % 3600) // 60
            
            return bot.send_message(
                message.chat.id, 
                get_txt(user_id, "cooldown").format(hours=hours, minutes=minutes), 
                parse_mode="Markdown", 
                reply_markup=get_game_check_panel(user_id)
            )

    raw_token = f"PAYX-{user_id}-{current_time}"
    generated_key = "PX-" + hashlib.md5(raw_token.encode()).hexdigest()[:12].upper()
    
    USER_KEYS[user_id] = {"key": generated_key, "generated_at": current_time}
    success_msg = get_txt(user_id, "key_success").format(key=generated_key)
    bot.reply_to(message, success_msg, parse_mode="Markdown", reply_markup=get_game_check_panel(user_id))
    
    for owner in OWNERS:
        try: bot.send_message(owner, f"🔔 *New Key Issued*\nUser: `{message.from_user.first_name}`\nID: `{user_id}`\nToken: `{generated_key}`", parse_mode="Markdown")
        except Exception: pass

# =====================================================================
# OWNER CONTROL PANEL
# =====================================================================
@bot.message_handler(func=lambda msg: msg.text == "👑 RED MATRIX PANEL")
def trigger_owner_dashboard(message):
    if message.from_user.id not in OWNERS: return
    
    admin_text = (
        f"⚡ *PAYX-MM SUPREME COMMAND DASHBOARD* ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Welcome Master Owner. Manage infrastructure, promote sub-admins, and monitor active key frameworks:"
    )
    
    markup = InlineKeyboardMarkup()
    btn_add = InlineKeyboardButton("➕ Add Admin (Unlock Full Access)", callback_data="own_add_admin_prompt")
    btn_list = InlineKeyboardButton("📋 View Active Admins", callback_data="own_list_admins")
    btn_remove = InlineKeyboardButton("➖ Remove / Ban Admin", callback_data="own_remove_admin_prompt")
    btn_close = InlineKeyboardButton("Dismiss Panel", callback_data="delete_msg")
    
    markup.row(btn_add)
    markup.row(btn_list, btn_remove)
    markup.row(btn_close)
    
    bot.send_message(message.chat.id, admin_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("own_") or call.data in ["delete_msg", "game_locked", "chk_mlbb", "chk_coc", "chk_ff", "chk_pubg", "chk_hok", "chk_bs", "chk_mcgg"])
def callback_processor(call):
    user_id = call.from_user.id
    if call.data == "delete_msg":
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        return

    if call.data == "game_locked":
        alert_msg = "❌ Premium Subscription or Admin Status Needed to Unlock!" if USER_LANG.get(user_id, "EN") == "EN" else "❌ ဝင်ရောက်ရန် ပရီမီယမ် သို့မဟုတ် Admin အဆင့်ရှိရန် လိုအပ်ပါသည်!"
        bot.answer_callback_query(call.id, alert_msg, show_alert=True)
        return

    if call.data.startswith("chk_"):
        game_map = {
            "chk_mlbb": ("MOBILE LEGENDS", "/ml 2112723799 (19915)"),
            "chk_mcgg": ("MAGIC CHESS GO GO", "/Go 9108333 (4075)"),
            "chk_coc": ("CLASH OF CLANS", "/cc #20C0RVGL"),
            "chk_ff": ("FREE FIRE", "/ff 3108721457"),
            "chk_pubg": ("PUBG MOBILE", "/Pg 5204837417"),
            "chk_hok": ("HONOR OF KINGS", "/Hok 17960996468644334037"),
            "chk_bs": ("BLOOD STRIKE", "/Bl 586016075134")
        }
        name, fmt = game_map.get(call.data, ("GAME", ""))
        bot.answer_callback_query(call.id, f"📝 {name}\nFormat: {fmt}", show_alert=True)
        return

    if user_id not in OWNERS: return
    bot.answer_callback_query(call.id)
    
    if call.data == "own_list_admins":
        if not ADMINS:
            bot.send_message(call.message.chat.id, "ℹ️ No sub-admins are registered currently.")
            return
        report = "📋 *CURRENT REGISTERED ADMINS:* \n━━━━━━━━━━━━━━━━━━━━━━\n"
        for idx, adm_id in enumerate(ADMINS, 1):
            report += f"{idx}. User ID: `{adm_id}`\n"
        bot.send_message(call.message.chat.id, report, parse_mode="Markdown")
        
    elif call.data == "own_add_admin_prompt":
        msg = bot.send_message(call.message.chat.id, "⌨️ *Please type or forward the User ID to promote as Admin:*")
        bot.register_next_step_handler(msg, process_add_admin)
        
    elif call.data == "own_remove_admin_prompt":
        if not ADMINS:
            bot.send_message(call.message.chat.id, "❌ Admin database is empty.")
            return
        markup = InlineKeyboardMarkup()
        for adm_id in ADMINS:
            markup.row(InlineKeyboardButton(f"❌ Remove: {adm_id}", callback_data=f"rev_adm_{adm_id}"))
        markup.row(InlineKeyboardButton("Back", callback_data="delete_msg"))
        bot.send_message(call.message.chat.id, "🎯 *Select an Admin below to revoke/ban privileges instantly:*", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("rev_adm_"))
def handle_inline_revocation(call):
    if call.from_user.id not in OWNERS: return
    target_id = int(call.data.replace("rev_adm_", ""))
    ADMINS.discard(target_id)
    BANNED_USERS.add(target_id)
    bot.answer_callback_query(call.id, f"User {target_id} Revoked & Banned!", show_alert=True)
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception: pass

def process_add_admin(message):
    try:
        target_id = int(message.text.strip())
        ADMINS.add(target_id)
        BANNED_USERS.discard(target_id)
        bot.reply_to(message, f"🎉 *Success*: User `{target_id}` promoted to Bot Admin!", parse_mode="Markdown")
    except ValueError:
        bot.reply_to(message, "⚠️ Invalid syntax. Numerical Chat IDs only.")

# =====================================================================
# MULTI-GAME ROUTER & API CONNECTOR (FIXED FOR PROPER PARSING)
# =====================================================================
def call_game_api(game_type, main_id, extra_id=None):
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY, 
        "Content-Type": "application/json",
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    if game_type == "mlbb": url = f"https://{RAPIDAPI_HOST}/mobile-legends/{main_id}/{extra_id}"
    elif game_type == "mcgg": url = f"https://{RAPIDAPI_HOST}/mcgg/{main_id}/{extra_id}"
    elif game_type == "ff": url = f"https://{RAPIDAPI_HOST}/ff-global/{main_id}"
    elif game_type == "pubg": url = f"https://{RAPIDAPI_HOST}/pubgm-global/{main_id}"
    elif game_type == "coc": url = f"https://{RAPIDAPI_HOST}/coc/{main_id.replace('#', '')}"
    elif game_type == "honor-of-kings": url = f"https://{RAPIDAPI_HOST}/honor-of-kings/{main_id}"
    elif game_type == "blood-strike": url = f"https://{RAPIDAPI_HOST}/blood-strike/{main_id}"
    else: return None
        
    try:
        r = requests.get(url, headers=headers, timeout=12)
        return r.json() if r.status_code == 200 else None
    except Exception: return None

def check_user_clearance(user_id):
    if user_id in OWNERS or user_id in ADMINS: return True
    if user_id not in USER_KEYS: return False
    if time.time() - USER_KEYS[user_id]["generated_at"] > COOLDOWN_LIMIT:
        USER_KEYS.pop(user_id, None)
        return False
    return True

def process_and_build_ui(message, game_type, main_id, extra_id=None):
    user_id = message.from_user.id
    
    if not check_user_clearance(user_id):
        buy_markup = InlineKeyboardMarkup()
        buy_markup.add(InlineKeyboardButton(text="Contact Owner (Premium)", url="https://t.me/PayX_MM"))
        return bot.reply_to(message, get_txt(user_id, "access_blocked"), parse_mode="Markdown", reply_markup=buy_markup)

    FREE_GAMES = ["mlbb", "mcgg"]
    if user_id not in OWNERS and user_id not in ADMINS and game_type not in FREE_GAMES:
        buy_markup = InlineKeyboardMarkup()
        buy_markup.add(InlineKeyboardButton(text="Contact Owner to Unlock", url="https://t.me/PayX_MM"))
        return bot.reply_to(message, get_txt(user_id, "premium_locked"), parse_mode="Markdown", reply_markup=buy_markup)

    status_msg = bot.reply_to(message, get_txt(user_id, "processing"))
    
    stop_loading = threading.Event()
    loading_thread = threading.Thread(target=run_fast_loading, args=(message.chat.id, status_msg.message_id, stop_loading), daemon=True)
    loading_thread.start()
    
    raw_data = call_game_api(game_type, main_id, extra_id)
    stop_loading.set()
    loading_thread.join(timeout=0.5)
    
    if not raw_data:
        try: bot.edit_message_text(get_txt(user_id, "api_error"), message.chat.id, status_msg.message_id)
        except Exception: pass
        return
        
    # 🔍 INTELLIGENT DEEP MULTI-LAYER KEY PARSER (FIX FOR UNKNOWN PLAYER / REGION)
    nickname = None
    region = None
    
    # Check directly from Root Level
    nickname = raw_data.get("nickname") or raw_data.get("username") or raw_data.get("name")
    region = raw_data.get("region") or raw_data.get("country") or raw_data.get("zone")
    
    # Check inside nested objects if root level keys are missing
    for nested_key in ["data", "result", "meta"]:
        if not nickname or not region:
            if nested_key in raw_data and isinstance(raw_data[nested_key], dict):
                inner = raw_data[nested_key]
                if not nickname:
                    nickname = inner.get("nickname") or inner.get("username") or inner.get("name")
                if not region:
                    region = inner.get("region") or inner.get("country") or inner.get("area") or inner.get("zone_id")

    # Final Fallbacks if still not found
    nickname = nickname or "Unknown Player"
    region = region or "Global Server"

    payload_data = f"GAME  : {game_type.upper()}\nNAME  : {nickname}\nID    : {main_id}"
    if extra_id: payload_data += f" ({extra_id})"
    payload_data += f"\nREGION: {region}"

    cool_neon_ui = (
        f"**PAYX-MM RESULT**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"```\n"
        f"{payload_data}\n"
        f"```\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{'ℹ️ Tap dark code block area above to auto copy instantly' if USER_LANG.get(user_id, 'EN') == 'EN' else 'ℹ️ ကူးယူရန် အပေါ်က အမည်းရောင်ကွက်ကို နှိပ်ပါ'}"
    )
    
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(text="Delete Result", callback_data="delete_msg"))
    
    try: bot.edit_message_text(cool_neon_ui, message.chat.id, status_msg.message_id, parse_mode="Markdown", reply_markup=markup)
    except Exception: pass

# =====================================================================
# COMMANDS ROUTING
# =====================================================================
@bot.message_handler(commands=['ml', 'Go', 'ff', 'cc', 'Pg', 'Hok', 'Bl'])
def explicit_commands_router(message):
    cmd = message.text.split()[0][1:]
    args_text = message.text[len(cmd)+2:].strip()
    
    if not args_text:
        return bot.reply_to(message, f"Usage format missing. Send data after /{cmd}")

    if cmd == 'ml':
        match = re.search(r'^(\d+)\s*[\(\[]\s*(\d+)\s*[\)\]]$', args_text)
        if match: process_and_build_ui(message, "mlbb", match.group(1), match.group(2))
        else: bot.reply_to(message, "Format: `/ml 2112723799 (19915)`")
    elif cmd == 'Go':
        match = re.search(r'^(\d+)\s*[\(\[]\s*(\d+)\s*[\)\]]$', args_text)
        if match: process_and_build_ui(message, "mcgg", match.group(1), match.group(2))
        else: bot.reply_to(message, "Format: `/Go 9108333 (4075)`")
    elif cmd == 'ff':
        process_and_build_ui(message, "ff", args_text)
    elif cmd == 'cc':
        process_and_build_ui(message, "coc", args_text.upper())
    elif cmd == 'Pg':
        process_and_build_ui(message, "pubg", args_text)
    elif cmd == 'Hok':
        process_and_build_ui(message, "honor-of-kings", args_text)
        elif cmd == 'Bl':
        process_and_build_ui(message, "blood-strike", args_text)

# =====================================================================
# DIRECT TEXT LISTENERS
# =====================================================================
@bot.message_handler(func=lambda message: True, content_types=['text'])
def advanced_text_router(message):
    if message.text.startswith('/'): return
    text_clean = message.text.strip()
    
    ml_match = re.search(r'^(\d+)\s*[\(\[]\s*(\d+)\s*[\)\]]$', text_clean)
    if ml_match:
        if "mcgg" in text_clean.lower() or "chess" in text_clean.lower():
            process_and_build_ui(message, "mcgg", ml_match.group(1), ml_match.group(2))
        else:
            process_and_build_ui(message, "mlbb", ml_match.group(1), ml_match.group(2))
        return

    coc_match = re.search(r'^#?([A-Z0-9]{7,14})$', text_clean, re.IGNORECASE)
    if coc_match and not text_clean.isdigit():
        process_and_build_ui(message, "coc", coc_match.group(1).upper())
        return

    if text_clean.isdigit():
        val_len = len(text_clean)
        if 8 <= val_len <= 10: process_and_build_ui(message, "ff", text_clean)
        elif 11 <= val_len <= 12: process_and_build_ui(message, "blood-strike", text_clean)
        elif val_len == 13: process_and_build_ui(message, "pubg", text_clean)
        elif 17 <= val_len <= 20: process_and_build_ui(message, "honor-of-kings", text_clean)
        return

if name == "main":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
