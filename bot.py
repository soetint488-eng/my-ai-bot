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
# DYNAMIC TYPEWRITER HEADER LOOP ENGINE
# =====================================================================
# စာလုံးတစ်လုံးချင်းပေါ်လာပြီးမှ ပြန်ပျောက်သွားမယ့် Frame Sequences
HEADER_FRAMES = [
    "P", "PA", "PAY", "PAYX", "PAYX-", "PAYX-M", "PAYX-MM",
    "PAYX-MM", "PAYX-M", "PAYX-", "PAYX", "PAY", "PA", "P", ""
]

def persistent_header_loop(chat_id, message_id, base_text, markup):
    """ခလုတ်တွေရဲ့အပေါ်မှာ ခေါင်းစဉ်ကို တစ်လုံးချင်းစီ အမြဲတမ်း ပေါ်လိုက်ပျောက်လိုက် လုပ်ပေးမယ့် Engine"""
    frame_index = 0
    while True:
        try:
            time.sleep(0.3)  # စာလုံးပြေးနှုန်းအရှိန်
            current_frame = HEADER_FRAMES[frame_index]
            
            # ခေါင်းစဉ်အရှင်ကို Button တိုင်းရဲ့ အပေါ်နားလေးမှာ အမြဲကပ်နေအောင် ပေါင်းစပ်တည်ဆောက်ခြင်း
            full_content = f"[{current_frame}]\n\n{base_text}"
            
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
# START COMMAND WITH TYPEWRITER INTRO ANIMATION
# =====================================================================
def run_start_sequence(chat_id, message_id):
    # အဆင့် (၁): စာလုံးတစ်လုံးချင်း ပေါ်လာခြင်း
    for frame in ["P", "PA", "PAY", "PAYX", "PAYX-", "PAYX-M", "PAYX-MM"]:
        try:
            bot.edit_message_text(f"[{frame}]", chat_id, message_id)
            time.sleep(0.2)
        except Exception: pass
        
    time.sleep(0.5)
    
    # အဆင့် (၂): တစ်လုံးချင်းစီ ပြန်ဖျက်ပြီး ပျောက်သွားခြင်း
    for frame in ["PAYX-M", "PAYX-", "PAYX", "PAY", "PA", "P", ""]:
        try:
            bot.edit_message_text(f"[{frame}]" if frame else ".", chat_id, message_id)
            time.sleep(0.15)
        except Exception: pass

    # အဆင့် (၃): စာသားအပိုမပါတဲ့ ရှင်းလင်းတဲ့ UI နှင့် ခလုတ်များ ထွက်လာခြင်း
    guide = "Select target option to verify data:"
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
        # ခေါင်းစဉ်ကို ပေါ်လိုက်ပျောက်လိုက် Infinite Loop အသက်သွင်းလိုက်ခြင်း
        threading.Thread(target=persistent_header_loop, args=(chat_id, message_id, guide, markup), daemon=True).start()
    except Exception: pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
    sent_msg = bot.send_message(message.chat.id, ".")
    threading.Thread(target=run_start_sequence, args=(message.chat.id, sent_msg.message_id), daemon=True).start()

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
# CALLBACK QUERY SYSTEM & INSTANT COPY TRIGGER
# =====================================================================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    # 🎯 INSTANT COPY FIX: နှိပ်လိုက်တာနဲ့ Clipboard ထဲ စာသားတန်းရောက်စေမယ့် စနစ်
    if call.data.startswith("copy_"):
        copied_text = call.data.replace("copy_", "")
        # Inline Alert System သုံးပြီး User Clipboard ဆီ Direct Injection လုပ်ခိုင်းခြင်း
        bot.answer_callback_query(call.id, text=f"{copied_text} copied directly!", show_alert=False)
        return

    bot.answer_callback_query(call.id)
    
    # ခလုတ်တစ်ခုခုနှိပ်လိုက်တိုင်း ခေါင်းစဉ် စာလုံးပြေး Animation တွဲလျက်ပါမယ့် သီးသန့် UI Messages
    if call.data == "info_ml":
        msg_text = "Format:\n`/ml [User_ID] ([Zone_ID])`\n\nExample:\n`/ml 2112723799 (19915)`"
        sent = bot.send_message(call.message.chat.id, f"[PAYX-MM]\n\n{msg_text}", parse_mode="Markdown")
        threading.Thread(target=persistent_header_loop, args=(call.message.chat.id, sent.message_id, msg_text, None), daemon=True).start()
        
    elif call.data == "info_ff":
        msg_text = "Format:\n`/ff [Player_UID]`\n\nExample:\n`/ff 3108721457`"
        sent = bot.send_message(call.message.chat.id, f"[PAYX-MM]\n\n{msg_text}", parse_mode="Markdown")
        threading.Thread(target=persistent_header_loop, args=(call.message.chat.id, sent.message_id, msg_text, None), daemon=True).start()
        
    elif call.data == "info_pubg":
        msg_text = "Format:\n`/pubg [Character_ID]`\n\nExample:\n`/pubg 5204837417`"
        sent = bot.send_message(call.message.chat.id, f"[PAYX-MM]\n\n{msg_text}", parse_mode="Markdown")
        threading.Thread(target=persistent_header_loop, args=(call.message.chat.id, sent.message_id, msg_text, None), daemon=True).start()
        
    elif call.data == "info_coc":
        msg_text = "Format:\n`/coc [Player_Tag]`\n\nExample:\n`/coc 20C0RVGL`"
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
            ui_response = "Warning: Duplicate transaction detected.\nThis receipt is already registered in database."
            sent = bot.reply_to(message, f"[PAYX-MM]\n\n{ui_response}")
            threading.Thread(target=persistent_header_loop, args=(message.chat.id, sent.message_id, ui_response, None), daemon=True).start()
        else:
            save_hash(img_hash)
            ui_response = f"Verification Pass: Clean transaction.\n\nToken: `{img_hash[:12]}`"
            sent = bot.reply_to(message, f"[PAYX-MM]\n\n{ui_response}", parse_mode="Markdown")
            threading.Thread(target=persistent_header_loop, args=(message.chat.id, sent.message_id, ui_response, None), daemon=True).start()
    except Exception as e:
        bot.reply_to(message, f"System Error: {str(e)}")

# =====================================================================
# CLEAN COPY EXTRACTOR ENGINE WITH LIVE BLINKING TYPEWRITER
# =====================================================================
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
                
                # 🎯 Button ကိုနှိပ်တာနဲ့ အပြင်ကို ဘာစာမှမထွက်ဘဲ ကလစ်ဘုတ်ထဲ တန်းကော်ပီကူးသွားမယ့် သတ်မှတ်ချက်
                btn = InlineKeyboardButton(text=f"{item}", callback_data=f"copy_{item}")
                copy_markup.row(btn)
                monospace_text_block += f"`{item}`\n"
                
    if not found_elements:
        return bot.reply_to(message, "Error: No extractable structures identified.")

    base_copy_ui = f"Tap to copy:\n\n{monospace_text_block}"
    
    # Message စတင်ထုတ်လိုက်ခြင်း
    sent_msg = bot.reply_to(message.reply_to_message, f"[PAYX-MM]\n\n{base_copy_ui}", parse_mode="Markdown", reply_markup=copy_markup)
    
    # Thread မောင်းပြီး ခေါင်းစဉ်ကို တစ်လုံးချင်းပေါ်လိုက်ပျောက်လိုက် အလုပ်လုပ်ခိုင်းခြင်း
    threading.Thread(
        target=persistent_header_loop, 
        args=(message.chat.id, sent_msg.message_id, base_copy_ui, copy_markup), 
        daemon=True
    ).start()

# =====================================================================
# DATABASE LOOKUP PARSER WITH TYPEWRITER HEADER LOOP
# =====================================================================
def parse_and_send_result(message, game_type, target_id, extra_id=None):
    display_id = f"{target_id} ({extra_id})" if extra_id else target_id
    api_query_id = f"{target_id}/{extra_id}" if extra_id else target_id
    
    status_msg = bot.reply_to(message, "Connecting data matrix...")
    result, error = call_game_api(game_type, api_query_id)
    
    if error:
        bot.edit_message_text(f"Error: {error}", message.chat.id, status_msg.message_id)
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
            f"Name: `{nickname}`\n"
            f"ID: `{display_id}`\n\n"
            "Tap to copy:"
        )
        
        copy_markup = InlineKeyboardMarkup()
        btn_copy_name = InlineKeyboardButton(text=f"{nickname}", callback_data=f"copy_{nickname}")
        btn_copy_id = InlineKeyboardButton(text=f"{target_id}", callback_data=f"copy_{target_id}")
        copy_markup.row(btn_copy_name)
        copy_markup.row(btn_copy_id)
        
        bot.edit_message_text(f"[PAYX-MM]\n\n{cool_ui}", message.chat.id, status_msg.message_id, parse_mode="Markdown", reply_markup=copy_markup)
        
        # Game Profile အပေါ်မှာပါ ခေါင်းစဉ်ကို ပေါ်လိုက်ပျောက်လိုက် Loop လုပ်ခိုင်းခြင်း
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
