import os, sys, re, time, hashlib, threading, requests, telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# =====================================================================
# FLASK WEB SERVER (CRON-JOB READY `200 OK` ENGINE)
# =====================================================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "200 OK - PayX-MM Core Server Online", 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

# =====================================================================
# CONFIGURATION, TOKENS & ADMIN CONFIG
# =====================================================================
BOT_TOKEN = "8761954371:AAEwo75dbsAWpvxavxqWr3UbhjeRwknlWnI"
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"
RAPIDAPI_HOST = "id-game-checker.p.rapidapi.com"

OWNER_ID = 8584422107
ADMINS = {OWNER_ID}

bot = telebot.TeleBot(BOT_TOKEN)
BRANDING = "PAYX-MM"
HASH_FILE = "processed_slips.txt"

MUTED_USERS = set()
BANNED_USERS = set()
BOT_USERS = set()

def load_hashes():
    if not os.path.exists(HASH_FILE): return set()
    with open(HASH_FILE, "r") as f: return set(l.strip() for l in f if l.strip())

def save_hash(img_hash):
    PROCESSED_SLIPS.add(img_hash)
    with open(HASH_FILE, "a") as f: f.write(f"{img_hash}\n")

PROCESSED_SLIPS = load_hashes()

# =====================================================================
# DYNAMIC TYPEWRITER HEADER LOOP ENGINE
# =====================================================================
HEADER_FRAMES = ["P", "PA", "PAY", "PAYX", "PAYX-", "PAYX-M", "PAYX-MM", "PAYX-MM", "PAYX-M", "PAYX-", "PAYX", "PAY", "PA", "P", ""]

def persistent_header_loop(chat_id, message_id, base_text, markup):
    frame_index = 0
    while True:
        try:
            time.sleep(0.3)
            full_content = f"--- [{HEADER_FRAMES[frame_index]}] ---\n{base_text}"
            bot.edit_message_text(text=full_content, chat_id=chat_id, message_id=message_id, parse_mode="Markdown", reply_markup=markup)
            frame_index = (frame_index + 1) % len(HEADER_FRAMES)
        except Exception: break

# =====================================================================
# SECURITY GUARD (ADMIN ONLY GATEWAY)
# =====================================================================
def is_authorized(message):
    u_id = message.from_user.id
    if u_id in BANNED_USERS:
        return False
    BOT_USERS.add(u_id)
    return u_id in ADMINS

def send_restricted_access(chat_id):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Bot Admin Request", url="https://t.me/PayX_MM"))
    bot.send_message(chat_id, f"--- [{BRANDING} SECURITY] ---\n\nAccess Denied. You are not authorized to use this bot. Please request permission from the administrator.", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.from_user.id in MUTED_USERS)
def handle_muted_restrictions(message):
    try: bot.delete_message(message.chat.id, message.message_id)
    except Exception: pass

UNWANTED_PATTERNS = [r't\.me/joinchat', r't\.me/\+', r'http[s]?://', r'crypto', r'casino', r'betting']

@bot.message_handler(func=lambda msg: msg.chat.type in ['group', 'supergroup'])
def group_spam_moderator(message):
    if message.from_user.id in ADMINS or not message.text: return
    for regex_item in UNWANTED_PATTERNS:
        if re.search(regex_item, message.text, re.IGNORECASE):
            try: bot.delete_message(message.chat.id, message.message_id)
            except Exception: pass
            break

# =====================================================================
# NATIVE TEXT GROUP MODERATION (NO BUTTONS + AUTO DELETE)
# =====================================================================
@bot.message_handler(commands=['mute'])
def action_group_mute(message):
    if not is_authorized(message): return
    if message.chat.type not in ['group', 'supergroup']: return
    if not message.reply_to_message: return
    
    target_id = message.reply_to_message.from_user.id
    if target_id in ADMINS: return
    
    MUTED_USERS.add(target_id)
    try:
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(message.chat.id, message.reply_to_message.message_id)
    except Exception: pass

@bot.message_handler(commands=['kick'])
def action_group_kick(message):
    if not is_authorized(message): return
    if message.chat.type not in ['group', 'supergroup']: return
    if not message.reply_to_message: return
    
    target_id = message.reply_to_message.from_user.id
    if target_id in ADMINS: return
    
    try:
        bot.ban_chat_member(message.chat.id, target_id)
        bot.unban_chat_member(message.chat.id, target_id)
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(message.chat.id, message.reply_to_message.message_id)
    except Exception: pass

# =====================================================================
# PRIVATE CHAT BOT ADMIN PANEL (BUTTONS INTERFACE)
# =====================================================================
@bot.message_handler(commands=['admin'])
def show_private_admin_panel(message):
    if not is_authorized(message): 
        send_restricted_access(message.chat.id)
        return
    if message.chat.type != 'private':
        return bot.reply_to(message, "Info: Admin Panel can only be accessed in Private Chat.")

    panel_text = f"--- {BRANDING} ADMIN PLAN CENTRAL ---\n\nSelect an option to manage the system:"
    
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("View Bot Users", callback_data="adm_view_users"), InlineKeyboardButton("View Banned Users", callback_data="adm_view_banned"))
    markup.row(InlineKeyboardButton("Unban User", callback_data="adm_trigger_unban"), InlineKeyboardButton("Add New Admin", callback_data="adm_trigger_add"))
    markup.row(InlineKeyboardButton("Close Panel", callback_data="delete_msg"))

    sent = bot.send_message(message.chat.id, panel_text, reply_markup=markup)
    threading.Thread(target=persistent_header_loop, args=(message.chat.id, sent.message_id, panel_text, markup), daemon=True).start()

# =====================================================================
# RAPIDAPI GAME CONNECTOR ROUTER
# =====================================================================
def call_game_api(game_type, target_id):
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "Content-Type": "application/json", "x-rapidapi-host": RAPIDAPI_HOST}
    endpoints = {"mlbb": f"mobile-legends/{target_id}", "ff": f"ff-global/{target_id}", "pubg": f"pubgm-global/{target_id}", "coc": f"coc/{target_id}"}
    try:
        r = requests.get(f"https://{RAPIDAPI_HOST}/{endpoints[game_type]}", headers=headers, timeout=12)
        return (r.json(), None) if r.status_code == 200 else (None, f"Status {r.status_code}")
    except Exception as e: return None, str(e)

# =====================================================================
# CALLBACK QUERY ROUTER (ADMIN PANEL ACTIONS & BUTTON RESPONSES)
# =====================================================================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "delete_msg":
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        return

    bot.answer_callback_query(call.id)

    if call.data.startswith("adm_"):
        if call.from_user.id not in ADMINS: return
        
        if call.data == "adm_view_users":
            users_list = f"--- ACTIVE BOT USERS ({len(BOT_USERS)}) ---\n\n"
            users_list += "\n".join([f"User ID: `{u}`" for u in BOT_USERS]) if BOT_USERS else "No users registered yet."
            bot.send_message(call.message.chat.id, users_list, parse_mode="Markdown")
            
        elif call.data == "adm_view_banned":
            banned_list = f"--- BANNED USERS ({len(BANNED_USERS)}) ---\n\n"
            banned_list += "\n".join([f"User ID: `{b}`" for b in BANNED_USERS]) if BANNED_USERS else "No banned users found."
            bot.send_message(call.message.chat.id, banned_list, parse_mode="Markdown")
            
        elif call.data == "adm_trigger_unban":
            bot.send_message(call.message.chat.id, "Use command format: /unban [User_ID]")
            
        elif call.data == "adm_trigger_add":
            bot.send_message(call.message.chat.id, "Use command format: /addadmin [User_ID]")
        return

    menus = {
        "info_ml": "--- PAYX FORMAT ---\n  /ml [User_ID] ([Zone_ID])\n-------------------\n\nExample:\n/ml `2112723799` (`19915`)",
        "info_ff": "--- PAYX FORMAT ---\n  /ff [Player_UID]\n-------------------\n\nExample:\n/ff `3108721457`",
        "info_pubg": "--- PAYX FORMAT ---\n  /pubg [Character_ID]\n-------------------\n\nExample:\n/pubg `5204837417`",
        "info_coc": "--- PAYX FORMAT ---\n  /coc [Player_Tag]\n-------------------\n\nExample:\n/coc `20C0RVGL`",
        "info_slip": "Please upload or forward the receipt screenshot image here."
    }
    if call.data in menus:
        if call.from_user.id not in ADMINS: return
        sent = bot.send_message(call.message.chat.id, f"[{BRANDING}]\n\n{menus[call.data]}", parse_mode="Markdown")
        threading.Thread(target=persistent_header_loop, args=(call.message.chat.id, sent.message_id, menus[call.data], None), daemon=True).start()

# =====================================================================
# REPLIES TEXT COMMAND HANDLING (ADMIN EXCLUSIVES)
# =====================================================================
@bot.message_handler(commands=['addadmin'])
def add_admin_privilege(message):
    if message.from_user.id != OWNER_ID: return
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Usage: /addadmin [User_ID]")
    try:
        target_id = int(args[1])
        ADMINS.add(target_id)
        bot.reply_to(message, f"Success: User `{target_id}` promoted to Bot Admin.", parse_mode="Markdown")
    except ValueError: bot.reply_to(message, "Error: Invalid ID format.")

@bot.message_handler(commands=['ban'])
def action_direct_ban(message):
    if not is_authorized(message): return
    args = message.text.split()
    target_id = None
    if len(args) >= 2: target_id = int(args[1])
    elif message.reply_to_message: target_id = message.reply_to_message.from_user.id
    
    if not target_id or target_id in ADMINS: return bot.reply_to(message, "Error: Target missing or target is admin.")
    BANNED_USERS.add(target_id)
    bot.reply_to(message, f"Success: User `{target_id}` has been permanently banned from the Bot.", parse_mode="Markdown")

@bot.message_handler(commands=['unban'])
def action_direct_unban(message):
    if not is_authorized(message): return
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Usage: /unban [User_ID]")
    try:
        target_id = int(args[1])
        BANNED_USERS.discard(target_id)
        bot.reply_to(message, f"Success: User `{target_id}` has been unbanned successfully.", parse_mode="Markdown")
    except ValueError: bot.reply_to(message, "Error: Invalid ID format.")

@bot.message_handler(commands=['userinfo'])
def get_user_profile_info(message):
    if not is_authorized(message): return
    t_user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    info = f"--- USER DATA PACK ---\nUsername: @{t_user.username or 'None'}\nFirst Name: {t_user.first_name}\nUser ID: `{t_user.id}`\nAdmin Status: {t_user.id in ADMINS}"
    bot.reply_to(message, info, parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def action_broadcast_transmission(message):
    if message.from_user.id != OWNER_ID: return
    content = message.text.replace("/broadcast", "").strip()
    if content: bot.send_message(message.chat.id, f"--- GLOBAL BROADCAST ---\n\n{content}")

@bot.message_handler(commands=['calc'])
def processing_calculator_expression(message):
    if not is_authorized(message): return
    expr = message.text.replace("/calc", "").strip()
    if not expr: return bot.reply_to(message, "Usage: /calc 500 * 2")
    clean_expr = re.sub(r'[^0-9+\-*/().\s]', '', expr)
    try: bot.reply_to(message, f"--- CALCULATION MATRIX ---\n\nResult: `{eval(clean_expr)}`", parse_mode="Markdown")
    except Exception: bot.reply_to(message, "Error: Process Failed.")

# =====================================================================
# RECEIPT SYSTEM & /COPY HANDLER & LOOKUP PARSER
# =====================================================================
@bot.message_handler(content_types=['photo'])
def handle_slip_verification(message):
    if not is_authorized(message): return
    try:
        img_hash = hashlib.md5(bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)).hexdigest()
        if img_hash in PROCESSED_SLIPS:
            ui = "--- DUPLICATE DETECTED ---\n\nWarning: Registered in database."
            sent = bot.reply_to(message, f"[{BRANDING}]\n\n{ui}")
        else:
            save_hash(img_hash)
            ui = f"--- VERIFICATION PASS ---\n\nClean transaction accepted.\n\nToken: `{img_hash[:12]}`"
            sent = bot.reply_to(message, f"[{BRANDING}]\n\n{ui}", parse_mode="Markdown")
        threading.Thread(target=persistent_header_loop, args=(message.chat.id, sent.message_id, ui, None), daemon=True).start()
    except Exception as e: bot.reply_to(message, f"System Error: {str(e)}")

@bot.message_handler(commands=['copy'])
def handle_reply_copy(message):
    if not is_authorized(message): return
    if not message.reply_to_message or not message.reply_to_message.text: return bot.reply_to(message, "Error: Reply with /copy")
    found = []
    for line in message.reply_to_message.text.split('\n'):
        if "/copy" in line.lower() or "payx" in line.lower(): continue
        for item in [s.strip("(),. ") for s in line.split()]:
            if item and item not in found and len(item) >= 2: found.append(item)
    if not found: return bot.reply_to(message, "Error: No data identified.")
    
    ui = f"**{BRANDING}**\n\nData Pack: `{' '.join(found)}`\n\nInfo: Tap to copy instantly"
    markup = InlineKeyboardMarkup(); markup.row(InlineKeyboardButton("Delete", callback_data="delete_msg"))
    sent = bot.reply_to(message.reply_to_message, ui, parse_mode="Markdown", reply_markup=markup)
    threading.Thread(target=persistent_header_loop, args=(message.chat.id, sent.message_id, ui, markup), daemon=True).start()

def parse_and_send_result(message, game_type, target_id, extra_id=None):
    status_msg = bot.reply_to(message, "Scanning mainframe matrix...")
    result, error = call_game_api(game_type, f"{target_id}/{extra_id}" if extra_id else target_id)
    if error: return bot.edit_message_text(f"Connection Error: {error}", message.chat.id, status_msg.message_id)
    
    nickname = None
    if result:
        nickname = result.get("nickname") or result.get("username") or result.get("name")
        if not nickname and "data" in result and isinstance(result["data"], dict):
            nickname = result["data"].get("nickname") or result["data"].get("username")
    nickname = nickname or "Verified Player"
    
    payload = f"{nickname} {f'{target_id} ({extra_id})' if extra_id else target_id}"
    ui = f"**{BRANDING}**\n\nResult: `{payload}`\n\nInfo: Tap block above to copy"
    
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Admin Panel", url="https://t.me/Dominic"))
    markup.row(InlineKeyboardButton("Delete", callback_data="delete_msg"))
    
    bot.edit_message_text(ui, message.chat.id, status_msg.message_id, parse_mode="Markdown", reply_markup=markup)
    threading.Thread(target=persistent_header_loop, args=(message.chat.id, status_msg.message_id, ui, markup), daemon=True).start()

# =====================================================================
# CHAT/GROUP START SEQUENCE ROUTER
# =====================================================================
def run_start_sequence(chat_id, message_id):
    try:
        for f in ["[P]", "[PA]", "[PAY]", "[PAYX]", "[PAYX-]", "[PAYX-M]", "[PAYX-MM]"]:
            bot.edit_message_text(f, chat_id, message_id); time.sleep(0.12)
    except Exception: pass

    guide = "====================\n  MAIN CONTROL PANEL\n====================\n\nSelect target option to verify data:"
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Mobile Legends", callback_data="info_ml"), InlineKeyboardButton("Free Fire", callback_data="info_ff"))
    markup.row(InlineKeyboardButton("PUBG Mobile", callback_data="info_pubg"), InlineKeyboardButton("Clash of Clans", callback_data="info_coc"))
    markup.row(InlineKeyboardButton("Verify Receipt Slip", callback_data="info_slip"))

    try:
        bot.edit_message_text(text=f"[{BRANDING}]\n\n{guide}", chat_id=chat_id, message_id=message_id, reply_markup=markup)
        threading.Thread(target=persistent_header_loop, args=(chat_id, message_id, guide, markup), daemon=True).start()
    except Exception: pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_authorized(message):
        send_restricted_access(message.chat.id)
        return
        
    sent = bot.send_message(message.chat.id, ".")
    threading.Thread(target=run_start_sequence, args=(message.chat.id, sent.message_id), daemon=True).start()

# =====================================================================
# GAME LOOKUP HANDLERS
# =====================================================================
@bot.message_handler(commands=['ml'])
def handle_ml(message):
    if not is_authorized(message): return
    match = re.search(r'/ml\s+(\d+)\s*\((.*?)\)', message.text)
    if not match: return bot.reply_to(message, "Format Warning: Use /ml 2112723799 (19915)")
    parse_and_send_result(message, "mlbb", match.group(1), match.group(2).strip())

@bot.message_handler(commands=['ff'])
def handle_ff(message):
    if not is_authorized(message): return
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Format: Use /ff [UID]")
    parse_and_send_result(message, "ff", args[1])

@bot.message_handler(commands=['pubg'])
def handle_pubg(message):
    if not is_authorized(message): return
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Format: Use /pubg [ID]")
    parse_and_send_result(message, "pubg", args[1])

@bot.message_handler(commands=['coc'])
def handle_coc(message):
    if not is_authorized(message): return
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Format: Use /coc [Tag]")
    parse_and_send_result(message, "coc", args[1].replace("#", "").strip())

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
