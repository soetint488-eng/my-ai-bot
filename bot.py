import os
import sys
import re
import time
import hashlib
import threading
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# =====================================================================
# RENDER PORT BINDING (FLASK WEB SERVER)
# =====================================================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "PayX-MM Multi-Game & Slip Duplicate Checker is Online"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host="0.0.0.0", port=port)

# =====================================================================
# CONFIGURATION & TOKENS
# =====================================================================
BOT_TOKEN = "8761954371:AAE3NExXJOGJa1D3Lp1aN2t6F_yA8h2imOo"
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"

bot = telebot.TeleBot(BOT_TOKEN)
BRANDING = "PAYX-MM"
HASH_FILE = "processed_slips.txt"

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
# LIVE BLINKING ENGINE (MAIN MENU)
# =====================================================================
BLINK_FRAMES = [
    "[ PAYX-MM ]", "[         ]", "[ PAYX-MM ]", "[         ]"
]

def animate_start_menu(chat_id, message_id):
    frame_index = 0
    while True:
        try:
            time.sleep(2.0)
            current_text = BLINK_FRAMES[frame_index]
            
            markup = InlineKeyboardMarkup()
            btn_ml = InlineKeyboardButton("Mobile Legends", callback_data="info_ml")
            btn_ff = InlineKeyboardButton("Free Fire", callback_data="info_ff")
            btn_pubg = InlineKeyboardButton("PUBG Mobile", callback_data="info_pubg")
            btn_coc = InlineKeyboardButton("Clash of Clans", callback_data="info_coc")
            btn_slip = InlineKeyboardButton("Verify Receipt Slip", callback_data="info_slip")
            btn_brand = InlineKeyboardButton(current_text, callback_data="brand_click")
            
            markup.row(btn_ml, btn_ff)
            markup.row(btn_pubg, btn_coc)
            markup.row(btn_slip)
            markup.row(btn_brand)
            
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)
            frame_index = (frame_index + 1) % len(BLINK_FRAMES)
        except Exception: 
            break

# =====================================================================
# START COMMAND
# =====================================================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    guide = (
        "PAYX-MM SYSTEM CONTROL\n"
        "----------------------------------\n\n"
        "Select target option to verify data:\n\n"
        "Tip: Reply any credentials with /copy for instant extraction."
    )
    markup = InlineKeyboardMarkup()
    btn_ml = InlineKeyboardButton("Mobile Legends", callback_data="info_ml")
    btn_ff = InlineKeyboardButton("Free Fire", callback_data="info_ff")
    btn_pubg = InlineKeyboardButton("PUBG Mobile", callback_data="info_pubg")
    btn_coc = InlineKeyboardButton("Clash of Clans", callback_data="info_coc")
    btn_slip = InlineKeyboardButton("Verify Receipt Slip", callback_data="info_slip")
    btn_brand = InlineKeyboardButton("[ PAYX-MM ]", callback_data="brand_click")
    
    markup.row(btn_ml, btn_ff)
    markup.row(btn_pubg, btn_coc)
    markup.row(btn_slip)
    markup.row(btn_brand)
    
    sent_msg = bot.send_message(message.chat.id, guide, reply_markup=markup)
    threading.Thread(target=animate_start_menu, args=(message.chat.id, sent_msg.message_id), daemon=True).start()

# =====================================================================
# RAPIDAPI TERMINAL ROUTER (GLOBAL ENDPOINTS)
# =====================================================================
def call_game_api(game_type, target_id):
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY, 
        "Content-Type": "application/json",
        "x-rapidapi-host": "id-game-checker.p.rapidapi.com"
    }
    
    if game_type == "mlbb":
        url = f"https://id-game-checker.p.rapidapi.com/mobile-legends/{target_id}"
    elif game_type == "ff":
        url = f"https://id-game-checker.p.rapidapi.com/ff-global/{target_id}"
    elif game_type == "pubg":
        url = f"https://id-game-checker.p.rapidapi.com/pubgm-global/{target_id}"
    elif game_type == "coc":
        url = f"https://id-game-checker.p.rapidapi.com/coc/{target_id}"
        
    try:
        r = requests.get(url, headers=headers, timeout=12)
        if r.status_code != 200: 
            return None, f"Status {r.status_code}"
        return r.json(), None
    except Exception as e: 
        return None, str(e)

# =====================================================================
# CALLBACK QUERY SYSTEM
# =====================================================================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data.startswith("copy_"):
        return bot.answer_callback_query(call.id, text="Copied to system context", show_alert=False)

    bot.answer_callback_query(call.id)
    if call.data == "info_ml":
        bot.send_message(call.message.chat.id, "MOBILE LEGENDS\n\nFormat:\n`/ml [User_ID] ([Zone_ID])`\n\nExample:\n`/ml 2112723799 (19915)`", parse_mode="Markdown")
    elif call.data == "info_ff":
        bot.send_message(call.message.chat.id, "FREE FIRE\n\nFormat:\n`/ff [Player_UID]`\n\nExample:\n`/ff 3108721457`", parse_mode="Markdown")
    elif call.data == "info_pubg":
        bot.send_message(call.message.chat.id, "PUBG MOBILE\n\nFormat:\n`/pubg [Character_ID]`\n\nExample:\n`/pubg 5204837417`", parse_mode="Markdown")
    elif call.data == "info_coc":
        bot.send_message(call.message.chat.id, "CLASH OF CLANS\n\nFormat:\n`/coc [Player_Tag]`\n\nExample:\n`/coc 20C0RVGL`", parse_mode="Markdown")
    elif call.data == "info_slip":
        bot.send_message(call.message.chat.id, "RECEIPT CHECKER\n\nPlease upload or forward the receipt screenshot image here.", parse_mode="Markdown")
    elif call.data == "brand_click":
        bot.send_message(call.message.chat.id, f"{BRANDING} Core Engine v7.8")

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
            ui_response = (
                f"{BRANDING} SECURITY ALERT\n"
                "----------------------------------\n\n"
                "Warning: Duplicate transaction detected.\n"
                "This receipt is already registered in database."
            )
            bot.reply_to(message, ui_response)
        else:
            save_hash(img_hash)
            ui_response = (
                f"{BRANDING} STATUS SUCCESS\n"
                "----------------------------------\n\n"
                "Verification Pass: Clean transaction.\n\n"
                f"Token: `{img_hash[:12]}`"
            )
            bot.reply_to(message, ui_response, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"System Error: {str(e)}")

# =====================================================================
# CLEAN COPY EXTRACTOR ENGINE (LIVE BLINKING HEADER & MONOSPACE)
# =====================================================================
COPY_BLINK_FRAMES = [
    "[ PAYX-MM ]", "[         ]", "[ PAYX-MM ]", "[         ]"
]

def animate_copy_header(chat_id, message_id, final_text, markup):
    frame_index = 0
    while True:
        try:
            time.sleep(2.0)
            current_title = COPY_BLINK_FRAMES[frame_index]
            updated_ui = f"{current_title}\nTap to copy:\n\n{final_text}"
            
            bot.edit_message_text(
                text=updated_ui,
                chat_id=chat_id,
                message_id=message_id,
                parse_mode="Markdown",
                reply_markup=markup
            )
            frame_index = (frame_index + 1) % len(COPY_BLINK_FRAMES)
        except Exception: 
            break

@bot.message_handler(commands=['copy'])
def handle_reply_copy(message):
    if not message.reply_to_message or not message.reply_to_message.text:
        return bot.reply_to(message, "Usage: Reply to any context message with /copy")
    
    target_text = message.reply_to_message.text
    lines = [line.strip() for line in target_text.split('\n') if line.strip()]
    
    copy_markup = InlineKeyboardMarkup()
    found_elements = []
    monospace_text_block = ""

    for raw_item in lines:
        if "/copy" in raw_item.lower() or "payx" in raw_item.lower():
            continue
        sub_items = [s.strip("(),. ") for s in raw_item.split() if s.strip("(),. ")]
        for item in sub_items:
            if item and item not in found_elements and len(item) >= 2:
                found_elements.append(item)
                btn = InlineKeyboardButton(text=f"{item}", callback_data=f"copy_{item[:15]}")
                copy_markup.row(btn)
                monospace_text_block += f"`{item}`\n"
                
    if not found_elements:
        return bot.reply_to(message, "Error: No extractable structures identified.")

    initial_ui = f"[ PAYX-MM ]\nTap to copy:\n\n{monospace_text_block}"
    sent_msg = bot.reply_to(message.reply_to_message, initial_ui, parse_mode="Markdown", reply_markup=copy_markup)
    
    threading.Thread(
        target=animate_copy_header, 
        args=(message.chat.id, sent_msg.message_id, monospace_text_block, copy_markup), 
        daemon=True
    ).start()

# =====================================================================
# DATABASE LOOKUP PARSER
# =====================================================================
def parse_and_send_result(message, game_type, target_id, extra_id=None):
    display_id = f"{target_id} ({extra_id})" if extra_id else target_id
    api_query_id = f"{target_id}/{extra_id}" if extra_id else target_id
    
    status_msg = bot.reply_to(message, "Connecting data matrix...")
    result, error = call_game_api(game_type, api_query_id)
    
    if error:
        bot.edit_message_text(f"Error: {error}\n\nSystem: {BRANDING}", message.chat.id, status_msg.message_id)
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
        
        cool_ui = (
            f"{game_type.upper()} DATA PROFILE\n"
            "----------------------------------\n\n"
            f"Name: `{nickname}`\n"
            f"ID: `{display_id}`\n\n"
            "----------------------------------\n"
            "Tap to copy:"
        )
        
        copy_markup = InlineKeyboardMarkup()
        btn_copy_name = InlineKeyboardButton(text=f"{nickname}", callback_data=f"copy_{nickname[:15]}")
        btn_copy_id = InlineKeyboardButton(text=f"{target_id}", callback_data=f"copy_{target_id}")
        copy_markup.row(btn_copy_name)
        copy_markup.row(btn_copy_id)
        
        bot.edit_message_text(cool_ui, message.chat.id, status_msg.message_id, parse_mode="Markdown", reply_markup=copy_markup)

# =====================================================================
# REVENUE & INBOUND ROUTING COMMANDS
# =====================================================================
@bot.message_handler(commands=['ml'])
def handle_ml(message):
    match = re.search(r'/ml\s+(\d+)\s*\((.*?)\)', message.text)
    if not match: return bot.reply_to(message, "Invalid Format. Use: /ml 2112723799 (19915)")
    parse_and_send_result(message, "mlbb", match.group(1), match.group(2).strip())

@bot.message_handler(commands=['ff'])
def handle_ff(message):
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Invalid Format. Use: /ff [UID]")
    parse_and_send_result(message, "ff", args[1])

@bot.message_handler(commands=['pubg'])
def handle_pubg(message):
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Invalid Format. Use: /pubg [ID]")
    parse_and_send_result(message, "pubg", args[1])

@bot.message_handler(commands=['coc'])
def handle_coc(message):
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Invalid Format. Use: /coc [Tag]")
    player_tag = args[1].replace("#", "").strip()
    parse_and_send_result(message, "coc", player_tag)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
