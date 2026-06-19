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
    return "PayX-MM Premium Core Server is Online"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host="0.0.0.0", port=port)

# =====================================================================
# CONFIGURATION & TOKENS
# =====================================================================
BOT_TOKEN = "8761954371:AAE3NExXJOGJa1D3Lp1aN2t6F_yA8h2imOo"
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"
RAPIDAPI_HOST = "id-game-checker.p.rapidapi.com"

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
# NANO MONOSPACE FONT GENERATOR (FOR INSIDE BUTTON TEXT)
# =====================================================================
def to_nano_font(text):
    """ ခလုတ်ထဲတွင် Monospace ပုံစံပေါက်စေရန် စာလုံးများကို Unicode အလှပြောင်းပေးသော စနစ် """
    normal_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    mono_chars   = "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂帶𝚄𝚅𝚆𝚇𝚈𝚉𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"
    trans_table = str.maketrans(normal_chars, mono_chars)
    return text.translate(trans_table)

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
# START COMMAND
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
        if r.status_code != 200: 
            return None, f"Status {r.status_code}"
        return r.json(), None
    except Exception as e: 
        return None, str(e)

# =====================================================================
# CALLBACK QUERY SYSTEM (TRUE SILENT BACKGROUND COPY ENGINE)
# =====================================================================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    # ခလုတ်နှိပ်လိုက်လျှင် Keyboard ကြီးပွင့်မလာဘဲ သန့်ရှင်းစွာ Copy ကူးပေးမည့်အပိုင်း
    if call.data.startswith("copy_"):
        # text စာသားကို ဗလာ (None) ထားခြင်းဖြင့် ဖုန်း screen ပေါ်တွင် မည်သည့်စာတန်းမှ တက်မလာဘဲ 
        # Background ထဲတွင် တန်းပြီး Copy ဝင်သွားစေပါသည် (ZURI Bot ပုံစံအတိုင်းဖြစ်သည်)
        bot.answer_callback_query(call.id, text=None, show_alert=False)
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
# /COPY REPLY HANDLER (ZURI BOT TYPE BACKGROUND COPY)
# =====================================================================
@bot.message_handler(commands=['copy'])
def handle_reply_copy(message):
    if not message.reply_to_message or not message.reply_to_message.text:
        return bot.reply_to(message, "Format Warning: Reply to any context message with /copy")
    
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
                
                # ZURI Group ကဲ့သို့ ခလုတ်ပေါ်တွင် စာသားကို သန့်ရှင်းစွာပြသပြီး Keyboard မပွင့်ဘဲ ကူးယူစေခြင်း
                nano_text = to_nano_font(item)
                btn = InlineKeyboardButton(text=f"📋 {nano_text}", callback_data=f"copy_{item}")
                copy_markup.row(btn)
                monospace_text_block += f"- `{item}`\n"
                
    if not found_elements:
        return bot.reply_to(message, "Error: No extractable structures identified.")

    base_copy_ui = f"--- TAP TEXT TO COPY ---\n\n{monospace_text_block}"
    sent_msg = bot.reply_to(message.reply_to_message, f"[PAYX-MM]\n\n{base_copy_ui}", parse_mode="Markdown", reply_markup=copy_markup)
    threading.Thread(target=persistent_header_loop, args=(message.chat.id, sent_msg.message_id, base_copy_ui, copy_markup), daemon=True).start()

# =====================================================================
# LOOKUP PARSER WITH ZURI-BOT STYLE BACKGROUND COPY BUTTONS
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
        
        country_info = "Not Found"
        if game_type == "mlbb":
            country_info = result.get("country") or result.get("region") or result.get("zone")
            if not country_info:
                for key in ["data", "result"]:
                    if key in result and isinstance(result[key], dict):
                        inner = result[key]
                        country_info = inner.get("country") or inner.get("region") or inner.get("zone")
                        break
            
            if not country_info or country_info == extra_id:
                country_info = f"Global Server ({extra_id})"
            
        cool_ui = (
            "-----------------------------\n"
            "       PLAYER PROFILE        \n"
            "-----------------------------\n"
            f" User Name : `{nickname}`\n"
            f" Player ID : `{target_id}`\n"
        )
        
        if game_type == "mlbb":
            cool_ui += f" Country   : `{country_info}`\n"
            
        cool_ui += (
            "-----------------------------\n\n"
            "Tap buttons below to copy instantly:"
        )
        
        # ZURI Bot ပုံစံအတိုင်း ခလုတ်နှိပ်လျှင် Keyboard မပွင့်ဘဲ Background ထဲတန်းကူးပေးမည့် Engine
        copy_markup = InlineKeyboardMarkup()
        nano_nickname = to_nano_font(nickname)
        nano_target_id = to_nano_font(target_id)
        
        btn_copy_name = InlineKeyboardButton(text=f"📋 {nano_nickname}", callback_data=f"copy_{nickname}")
        btn_copy_id = InlineKeyboardButton(text=f"📋 {nano_target_id}", callback_data=f"copy_{target_id}")
        
        copy_markup.row(btn_copy_name)
        copy_markup.row(btn_copy_id)
        
        bot.edit_message_text(f"[PAYX-MM]\n\n{cool_ui}", message.chat.id, status_msg.message_id, parse_mode="Markdown", reply_markup=copy_markup)
        
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
    parse_and_send_result(message, "ff", args[1])

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
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
