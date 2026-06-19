import os
import sys
import re
import time
import hashlib
import threading
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, jsonify

# =====================================================================
# FLASK WEB SERVER (CRON-JOB READY `200 OK` ENGINE)
# =====================================================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    # Cron-job.org က လာခေါက်တဲ့အခါ HTTP Status 200 OK တန်းပြန်ပေးမည့် စနစ်ဖြစ်ပါတယ်
    return "200 OK - PayX-MM Core Server Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host="0.0.0.0", port=port)

# =====================================================================
# CONFIGURATION, TOKENS & ADMIN CONFIG
# =====================================================================
BOT_TOKEN = "8761954371:AAE3NExXJOGJa1D3Lp1aN2t6F_yA8h2imOo"
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"
RAPIDAPI_HOST = "id-game-checker.p.rapidapi.com"

OWNER_ID = 8584422107
ADMINS = {OWNER_ID}

bot = telebot.TeleBot(BOT_TOKEN)
BRANDING = "PAYX-MM"
HASH_FILE = "processed_slips.txt"
MUTED_USERS = set()

def load_hashes():
    if not os.path.exists(HASH_FILE):
        return set()
    with open(HASH_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def save_hash(img_hash):
    PROCESSED_SLIPS.add(img_hash)
    with open(HASH_FILE, "a") as f:
        f.write(f"{img_hash}\n")

PROCESSED_SLIPS = load_hashes()

# =====================================================================
# DYNAMIC TYPEWRITER HEADER LOOP ENGINE
# =====================================================================
HEADER_FRAMES = [
    "P", "PA", "PAY", "PAYX", "PAYX-", "PAYX-M", "PAYX-MM",
    "PAYX-MM", "PAYX-M", "PAYX-", "PAYX", "PAY", "PA", "P", ""
]

def persistent_header_loop(chat_id, message_id, base_text, markup):
    frame_index = 0
    while True:
        try:
            time.sleep(0.3)
            current_frame = HEADER_FRAMES[frame_index]
            full_content = f"--- [{current_frame}] ---\n{base_text}"
            
            bot.edit_message_text(
                text=full_content,
                chat_id=chat_id,
                message_id=message_id,
                parse_mode="Markdown",
                reply_markup=markup
            )
            frame_index = (frame_index + 1) % len(HEADER_FRAMES)
        except Exception:
            break

# =====================================================================
# MUTED USER GUARD
# =====================================================================
@bot.message_handler(func=lambda msg: msg.from_user.id in MUTED_USERS)
def handle_muted_restrictions(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception: pass

# =====================================================================
# START COMMAND & CONTROL PANEL
# =====================================================================
def run_start_sequence(chat_id, message_id):
    try:
        frames = ["[P]", "[PA]", "[PAY]", "[PAYX]", "[PAYX-]", "[PAYX-M]", "[PAYX-MM]"]
        for f in frames:
            bot.edit_message_text(f, chat_id, message_id)
            time.sleep(0.15)
        time.sleep(0.3)
        bot.edit_message_text(".", chat_id, message_id)
    except Exception: pass

    guide = "====================\n  MAIN CONTROL PANEL\n====================\n\nSelect target option to verify data:"
    markup = InlineKeyboardMarkup()
    btn_ml = InlineKeyboardButton("Mobile Legends", callback_data="info_ml")
    btn_ff = InlineKeyboardButton("Free Fire", callback_data="info_ff")
    btn_pubg = InlineKeyboardButton("PUBG Mobile", callback_data="info_pubg")
    btn_coc = InlineKeyboardButton("Clash of Clans", callback_data="info_coc")
    btn_slip = InlineKeyboardButton("Verify Receipt Slip", callback_data="info_slip")
    
    markup.row(btn_ml, btn_ff)
    markup.row(btn_pubg, btn_coc)
    markup.row(btn_slip)

    try:
        bot.edit_message_text(text=f"[PAYX-MM]\n\n{guide}", chat_id=chat_id, message_id=message_id, reply_markup=markup)
        threading.Thread(target=persistent_header_loop, args=(chat_id, message_id, guide, markup), daemon=True).start()
    except Exception: pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
    sent_msg = bot.send_message(message.chat.id, ".")
    threading.Thread(target=run_start_sequence, args=(message.chat.id, sent_msg.message_id), daemon=True).start()

# =====================================================================
# CORE ADMIN & PROMOTION TOOLS
# =====================================================================
@bot.message_handler(commands=['addadmin'])
def add_admin_privilege(message):
    if message.from_user.id != OWNER_ID: return
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Usage: /addadmin [User_ID]")
    try:
        target_id = int(args[1])
        ADMINS.add(target_id)
        bot.reply_to(message, f"Success: User {target_id} promoted to Bot Admin.")
    except ValueError:
        bot.reply_to(message, "Error: Invalid User ID format.")

@bot.message_handler(commands=['userinfo'])
def get_user_profile_info(message):
    target_user = message.from_user
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        
    info_payload = (
        f"--- USER DATA PACK ---\n"
        f"Username: @{target_user.username or 'None'}\n"
        f"First Name: {target_user.first_name}\n"
        f"User ID: `{target_user.id}`\n"
        f"Admin Status: {target_user.id in ADMINS}"
    )
    bot.reply_to(message, info_payload, parse_mode="Markdown")

@bot.message_handler(commands=['mute'])
def action_mute_user(message):
    if message.from_user.id not in ADMINS: return
    if not message.reply_to_message: return bot.reply_to(message, "Error: Reply to target user to mute.")
    target_id = message.reply_to_message.from_user.id
    if target_id in ADMINS: return bot.reply_to(message, "Action Denied: Target is admin.")
    MUTED_USERS.add(target_id)
    bot.reply_to(message, f"Success: User {target_id} has been muted.")

@bot.message_handler(commands=['unmute'])
def action_unmute_user(message):
    if message.from_user.id not in ADMINS: return
    if not message.reply_to_message: return bot.reply_to(message, "Error: Reply to target user to unmute.")
    target_id = message.reply_to_message.from_user.id
    MUTED_USERS.discard(target_id)
    bot.reply_to(message, f"Success: User {target_id} has been unmuted.")

@bot.message_handler(commands=['ban'])
def action_ban_user(message):
    if message.from_user.id not in ADMINS: return
    if not message.reply_to_message: return bot.reply_to(message, "Error: Reply to target user to ban.")
    target_id = message.reply_to_message.from_user.id
    if target_id in ADMINS: return bot.reply_to(message, "Action Denied: Target is admin.")
    try:
        bot.ban_chat_member(message.chat.id, target_id)
        bot.reply_to(message, f"Success: User {target_id} has been banned.")
    except Exception as e:
        bot.reply_to(message, f"Execution Error: {str(e)}")

@bot.message_handler(commands=['unban'])
def action_unban_user(message):
    if message.from_user.id not in ADMINS: return
    if not message.reply_to_message: return bot.reply_to(message, "Error: Reply to target user to unban.")
    target_id = message.reply_to_message.from_user.id
    try:
        bot.unban_chat_member(message.chat.id, target_id)
        bot.reply_to(message, f"Success: User {target_id} has been unbanned.")
    except Exception as e:
        bot.reply_to(message, f"Execution Error: {str(e)}")

@bot.message_handler(commands=['kick', 'remove'])
def action_kick_user(message):
    if message.from_user.id not in ADMINS: return
    if not message.reply_to_message: return bot.reply_to(message, "Error: Reply to target user to kick.")
    target_id = message.reply_to_message.from_user.id
    if target_id in ADMINS: return bot.reply_to(message, "Action Denied: Target is admin.")
    try:
        bot.ban_chat_member(message.chat.id, target_id)
        bot.unban_chat_member(message.chat.id, target_id)
        bot.reply_to(message, f"Success: User {target_id} has been kicked.")
    except Exception as e:
        bot.reply_to(message, f"Execution Error: {str(e)}")

@bot.message_handler(commands=['purge', 'del'])
def delete_targeted_message(message):
    if message.from_user.id not in ADMINS: return
    if not message.reply_to_message: return bot.reply_to(message, "Error: Reply to text to delete.")
    try:
        bot.delete_message(message.chat.id, message.reply_to_message.message_id)
        bot.delete_message(message.chat.id, message.message_id)
    except Exception: pass

@bot.message_handler(commands=['broadcast'])
def action_broadcast_transmission(message):
    if message.from_user.id != OWNER_ID: return
    content = message.text.replace("/broadcast", "").strip()
    if not content: return bot.reply_to(message, "Usage: /broadcast [Content]")
    bot.send_message(message.chat.id, f"--- GLOBAL BROADCAST ---\n\n{content}")

# =====================================================================
# CALCULATOR UTILITY LOGIC
# =====================================================================
@bot.message_handler(commands=['calc'])
def processing_calculator_expression(message):
    expression = message.text.replace("/calc", "").strip()
    if not expression: return bot.reply_to(message, "Usage: /calc 500 * 2")
    expression = re.sub(r'[^0-9+\-*/().\s]', '', expression)
    if not expression.strip(): return bot.reply_to(message, "Error: Structural violation.")
    try:
        computation = eval(expression)
        bot.reply_to(message, f"--- CALCULATION MATRIX ---\n\nExpression: {expression}\nResult: `{computation}`", parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "Error: Failed to process calculation.")

# =====================================================================
# GROUP SCRUBBER & SPAM FILTER (CLEAN UNWANTED CHAT TRAFFIC)
# =====================================================================
UNWANTED_PATTERNS = [
    r't\.me/joinchat', r't\.me/\+', r'http[s]?://', r'crypto', r'casino', r'betting'
]

@bot.message_handler(func=lambda msg: msg.chat.type in ['group', 'supergroup'])
def group_spam_moderator(message):
    if message.from_user.id in ADMINS: return
    if not message.text: return
    for regex_item in UNWANTED_PATTERNS:
        if re.search(regex_item, message.text, re.IGNORECASE):
            try: bot.delete_message(message.chat.id, message.message_id)
            except Exception: pass
            break

# =====================================================================
# RAPIDAPI TERMINAL ROUTER
# =====================================================================
def call_game_api(game_type, target_id):
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY, 
        "Content-Type": "application/json",
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    if game_type == "mlbb":
        url = f"https://{RAPIDAPI_HOST}/mobile-legends/{target_id}"
    elif game_type == "ff":
        url = f"https://{RAPIDAPI_HOST}/ff-global/{target_id}"
    elif game_type == "pubg":
        url = f"https://{RAPIDAPI_HOST}/pubgm-global/{target_id}"
    elif game_type == "coc":
        url = f"https://{RAPIDAPI_HOST}/coc/{target_id}"
    try:
        r = requests.get(url, headers=headers, timeout=12)
        if r.status_code != 200: return None, f"Status {r.status_code}"
        return r.json(), None
    except Exception as e: 
        return None, str(e)

# =====================================================================
# CALLBACK QUERY SYSTEM & INFO ROUTING
# =====================================================================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "delete_msg":
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        return

    bot.answer_callback_query(call.id)
    
    if call.data == "info_ml":
        msg_text = "--- PAYX FORMAT ---\n  /ml [User_ID] ([Zone_ID])\n-------------------\n\nFormat Example:\n/ml `2112723799` (`19915`)"
        sent = bot.send_message(call.message.chat.id, f"[PAYX-MM]\n\n{msg_text}", parse_mode="Markdown")
        threading.Thread(target=persistent_header_loop, args=(call.message.chat.id, sent.message_id, msg_text, None), daemon=True).start()
        
    elif call.data == "info_ff":
        msg_text = "--- PAYX FORMAT ---\n  /ff [Player_UID]\n-------------------\n\nFormat Example:\n/ff `3108721457`"
        sent = bot.send_message(call.message.chat.id, f"[PAYX-MM]\n\n{msg_text}", parse_mode="Markdown")
        threading.Thread(target=persistent_header_loop, args=(call.message.chat.id, sent.message_id, msg_text, None), daemon=True).start()
        
    elif call.data == "info_pubg":
        msg_text = "--- PAYX FORMAT ---\n  /pubg [Character_ID]\n-------------------\n\nFormat Example:\n/pubg `5204837417`"
        sent = bot.send_message(call.message.chat.id, f"[PAYX-MM]\n\n{msg_text}", parse_mode="Markdown")
        threading.Thread(target=persistent_header_loop, args=(call.message.chat.id, sent.message_id, msg_text, None), daemon=True).start()
        
    elif call.data == "info_coc":
        msg_text = "--- PAYX FORMAT ---\n  /coc [Player_Tag]\n-------------------\n\nFormat Example:\n/coc `20C0RVGL`"
        sent = bot.send_message(call.message.chat.id, f"[PAYX-MM]\n\n{msg_text}", parse_mode="Markdown")
        threading.Thread(target=persistent_header_loop, args=(call.message.chat.id, sent.message_id, msg_text, None), daemon=True).start()
        
    elif call.data == "info_slip":
        msg_text = "Please upload or forward the receipt screenshot image here."
        sent = bot.send_message(call.message.chat.id, f"[PAYX-MM]\n\n{msg_text}", parse_mode="Markdown")
        threading.Thread(target=persistent_header_loop, args=(call.message.chat.id, sent.message_id, msg_text, None), daemon=True).start()

# =====================================================================
# RECEIPT DUPLICATE CHECKER SYSTEM
# =====================================================================
@bot.message_handler(content_types=['photo'])
def handle_slip_verification(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        img_hash = hashlib.md5(downloaded_file).hexdigest()
        
        if img_hash in PROCESSED_SLIPS:
            ui_response = "--- DUPLICATE DETECTED ---\n\nWarning: This receipt is already registered in database."
            sent = bot.reply_to(message, f"[PAYX-MM]\n\n{ui_response}")
            threading.Thread(target=persistent_header_loop, args=(message.chat.id, sent.message_id, ui_response, None), daemon=True).start()
        else:
            save_hash(img_hash)
            ui_response = f"--- VERIFICATION PASS ---\n\nClean transaction accepted.\n\nToken: `{img_hash[:12]}`"
            sent = bot.reply_to(message, f"[PAYX-MM]\n\n{ui_response}", parse_mode="Markdown")
            threading.Thread(target=persistent_header_loop, args=(message.chat.id, sent.message_id, ui_response, None), daemon=True).start()
    except Exception as e:
        bot.reply_to(message, f"System Error: {str(e)}")

# =====================================================================
# /COPY REPLY HANDLER WITH NATIVE INSTANT ONE-TAP CONFIG
# =====================================================================
@bot.message_handler(commands=['copy'])
def handle_reply_copy(message):
    if not message.reply_to_message or not message.reply_to_message.text:
        return bot.reply_to(message, "Format Warning: Reply to any context message with /copy")
    
    target_text = message.reply_to_message.text
    lines = [line.strip() for line in target_text.split('\n') if line.strip()]
    
    found_elements = []
    for raw_item in lines:
        if "/copy" in raw_item.lower() or "payx" in raw_item.lower():
            continue
        sub_items = [s.strip("(),. ") for s in raw_item.split() if s.strip("(),. ")]
        for item in sub_items:
            if item and item not in found_elements and len(item) >= 2:
                found_elements.append(item)
                
    if not found_elements:
        return bot.reply_to(message, "Error: No extractable structures identified.")

    combined_text = " ".join(found_elements)
    
    cool_ui = (
        f"**{BRANDING}**\n\n"
        f"Data Pack: `{combined_text}`\n\n"
        f"ℹ️ *Tap the data block above to copy instantly*"
    )
    
    copy_markup = InlineKeyboardMarkup()
    btn_delete = InlineKeyboardButton(text="Delete", callback_data="delete_msg")
    copy_markup.row(btn_delete)

    sent_msg = bot.reply_to(message.reply_to_message, cool_ui, parse_mode="Markdown", reply_markup=copy_markup)
    threading.Thread(target=persistent_header_loop, args=(message.chat.id, sent_msg.message_id, cool_ui, copy_markup), daemon=True).start()

# =====================================================================
# LOOKUP PARSER WITH ONE-TAP ENGINE + CUSTOM ADMIN ASSIGNED BUTTONS
# =====================================================================
def parse_and_send_result(message, game_type, target_id, extra_id=None):
    api_query_id = f"{target_id}/{extra_id}" if extra_id else target_id
    
    status_msg = bot.reply_to(message, "Scanning mainframe matrix...")
    result, error = call_game_api(game_type, api_query_id)
    
    if error:
        bot.edit_message_text(f"Connection Error: {error}", message.chat.id, status_msg.message_id)
        return
        
    if result:
        nickname = result.get("nickname") or result.get("username") or result.get("name")
        if not nickname:
            for key in ["data", "result"]:
                if key in result and isinstance(result[key], dict):
                    inner = result[key]
                    nickname = inner.get("nickname") or inner.get("username") or inner.get("name")
                    break
        nickname = nickname or "Verified Player"
        
        full_id_display = f"{target_id} ({extra_id})" if extra_id else f"{target_id}"
        payload_data = f"{nickname} {full_id_display}"
        
        cool_ui = (
            f"**{BRANDING}**\n\n"
            f"Result: `{payload_data}`\n\n"
            f"ℹ️ *Tap the results block above to copy instantly*"
        )
        
        copy_markup = InlineKeyboardMarkup()
        btn_owner = InlineKeyboardButton(text="⚡ Admin Panel ⚡", url="https://t.me/Dominic")
        btn_delete = InlineKeyboardButton(text="Delete", callback_data="delete_msg")
        
        copy_markup.row(btn_owner)
        copy_markup.row(btn_delete)
        
        bot.edit_message_text(cool_ui, message.chat.id, status_msg.message_id, parse_mode="Markdown", reply_markup=copy_markup)
        
        threading.Thread(
            target=persistent_header_loop, 
            args=(message.chat.id, status_msg.message_id, cool_ui, copy_markup), 
            daemon=True
        ).start()

# =====================================================================
# COMMANDS ROUTING
# =====================================================================
@bot.message_handler(commands=['ml'])
def handle_ml(message):
    match = re.search(r'/ml\s+(\d+)\s*\((.*?)\)', message.text)
    if not match: return bot.reply_to(message, "Format Warning: Use /ml 2112723799 (19915)")
    parse_and_send_result(message, "mlbb", match.group(1), match.group(2).strip())

@bot.message_handler(commands=['ff'])
def handle_ff(message):
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Format Warning: Use /ff [UID]")
    parse_and_send_result(message, "ff, args[1])

@bot.message_handler(commands=['pubg'])
def handle_pubg(message):
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Format Warning: Use /pubg [ID]")
    parse_and_send_result(message, "pubg", args[1])

@bot.message_handler(commands=['coc'])
def handle_coc(message):
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Format Warning: Use /coc [Tag]")
    player_tag = args[1].replace("#", "").strip()
    parse_and_send_result(message, "coc", player_tag)

if __name__ == "__main__":
    # Flask Server နှင့် Telegram Bot ကို ခွဲပြီး တစ်ပြိုင်နက် Run ပေးမည့် Main Engine
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
