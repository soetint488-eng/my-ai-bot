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
# RENDER PORT BINDING FIX (FLASK WEB SERVER)
# =====================================================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "PayX-MM Multi-Game & Slip Duplicate Checker is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host="0.0.0.0", port=port)

# =====================================================================
# Configuration (Tokens & API Keys)
# =====================================================================
BOT_TOKEN = "8761954371:AAE3NExXJOGJa1D3Lp1aN2t6F_yA8h2imOo"
RAPIDAPI_KEY = "06b1562a59msh39810b847e9d0e2p151fd6jsn3a9d60ae50a9"

bot = telebot.TeleBot(BOT_TOKEN)
BRANDING = "𝑷𝒂𝒚𝑿-𝑴𝑴"

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

# Country/Region Mapping
COUNTRY_MAP = {
    "mm": "Myanmar", "myanmar": "Myanmar", "burma": "Myanmar",
    "id": "Indonesia", "indonesia": "Indonesia",
    "ph": "Philippines", "philippines": "Philippines",
    "sg": "Singapore", "singapore": "Singapore",
    "my": "Malaysia", "malaysia": "Malaysia",
    "th": "Thailand", "thailand": "Thailand",
    "kh": "Cambodia", "cambodia": "Cambodia",
    "vn": "Vietnam", "vietnam": "Vietnam",
    "la": "Laos", "laos": "Laos"
}

def get_pretty_country(raw_region):
    if not raw_region:
        return "International / Global"
    clean_region = str(raw_region).strip().lower()
    return COUNTRY_MAP.get(clean_region, str(raw_region).title())

# =====================================================================
# LIVE BLINKING BUTTON ANIMATION (MAIN MENU)
# =====================================================================
BLINK_FRAMES = [
    "[  𝑷𝒂𝒚𝑿-𝑴𝑴  ]", "[             ]", "[  𝑷𝒂𝒚𝑿-𝑴𝑴  ]", "[             ]"
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
            btn_slip = InlineKeyboardButton("Verify Any Slip (KPay/Wave)", callback_data="info_slip")
            btn_brand = InlineKeyboardButton(current_text, callback_data="brand_click")
            
            markup.row(btn_ml, btn_ff)
            markup.row(btn_pubg, btn_coc)
            markup.row(btn_slip)
            markup.row(btn_brand)
            
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)
            frame_index = (frame_index + 1) % len(BLINK_FRAMES)
        except Exception: break

# =====================================================================
# INTRO TYPEWRITER ANIMATION (START COMMAND)
# =====================================================================
def run_start_intro_animation(chat_id, initial_msg_id):
    typing_steps = ["𝑷...", "𝑷𝒂...", "𝑷𝒂𝒚...", "𝑷𝒂𝒚𝑿...", "𝑷𝒂𝒚𝑿-...", "𝑷𝒂𝒚𝑿-𝑴...", "𝑷𝒂𝒚𝑿-𝑴𝑴"]
    for step in typing_steps:
        try:
            bot.edit_message_text(f"`{step}`", chat_id, initial_msg_id, parse_mode="Markdown")
            time.sleep(0.25)
        except Exception: pass
    time.sleep(0.5)
    
    guide = (
        "PREMIUM AUTOMATION ID & SLIP DUPLICATE CHECKER\n"
        "----------------------------------------\n\n"
        "Welcome! Select your target platform to check ID or upload your receipt:\n\n"
        "Tip: Reply to any text message containing credentials with /copy to generate rapid copy text instantly!"
    )
    markup = InlineKeyboardMarkup()
    btn_ml = InlineKeyboardButton("Mobile Legends", callback_data="info_ml")
    btn_ff = InlineKeyboardButton("Free Fire", callback_data="info_ff")
    btn_pubg = InlineKeyboardButton("PUBG Mobile", callback_data="info_pubg")
    btn_coc = InlineKeyboardButton("Clash of Clans", callback_data="info_coc")
    btn_slip = InlineKeyboardButton("Check Duplicate Slip", callback_data="info_slip")
    btn_brand = InlineKeyboardButton("[  𝑷𝒂𝒚𝑿-𝑴𝑴  ]", callback_data="brand_click")
    
    markup.row(btn_ml, btn_ff)
    markup.row(btn_pubg, btn_coc)
    markup.row(btn_slip)
    markup.row(btn_brand)
    
    try:
        bot.edit_message_text(guide, chat_id, initial_msg_id, parse_mode="Markdown", reply_markup=markup)
        threading.Thread(target=animate_start_menu, args=(chat_id, initial_msg_id), daemon=True).start()
    except Exception: pass

# =====================================================================
# GAME ID CHECKER API ROUTER
# =====================================================================
def call_game_api(game_type, target_id):
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "Content-Type": "application/json"}
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
# Telegram Message Handlers & Callbacks
# =====================================================================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    sent_msg = bot.send_message(message.chat.id, "`Connecting to PayX Core...`", parse_mode="Markdown")
    threading.Thread(target=run_start_intro_animation, args=(message.chat.id, sent_msg.message_id), daemon=True).start()

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    # Clipboard Alert / Copy Alert System
    if call.data.startswith("copy_"):
        copied_text = call.data.replace("copy_", "")
        bot.answer_callback_query(call.id, text=f"Text Ready! Just long press to copy if needed.", show_alert=False)
        return

    bot.answer_callback_query(call.id)
    if call.data == "info_ml":
        bot.send_message(call.message.chat.id, "MOBILE LEGENDS QUERY\n\nFormat:\n`/ml [User_ID] ([Zone_ID])`\n\nExample:\n`/ml 2112723799 (19915)`", parse_mode="Markdown")
    elif call.data == "info_ff":
        bot.send_message(call.message.chat.id, "FREE FIRE QUERY\n\nFormat:\n`/ff [Player_UID]`\n\nExample:\n`/ff 11944852314`", parse_mode="Markdown")
    elif call.data == "info_pubg":
        bot.send_message(call.message.chat.id, "PUBG MOBILE QUERY\n\nFormat:\n`/pubg [Character_ID]`\n\nExample:\n`/pubg 5930748140`", parse_mode="Markdown")
    elif call.data == "info_coc":
        bot.send_message(call.message.chat.id, "CLASH OF CLANS QUERY\n\nFormat:\n`/coc [Player_Tag]`\n\nExample:\n`/coc 20C0RVGL`", parse_mode="Markdown")
    elif call.data == "info_slip":
        bot.send_message(call.message.chat.id, "DUPLICATE SLIP DETECTOR\n\nPlease send any receipt image here. The engine will check and block if it is used before.", parse_mode="Markdown")
    elif call.data == "brand_click":
        bot.send_message(call.message.chat.id, f"{BRANDING} Identity & Slip Persistent Core v7.2")

@bot.message_handler(content_types=['photo'])
def handle_slip_verification(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        img_hash = hashlib.md5(downloaded_file).hexdigest()
        
        if img_hash in PROCESSED_SLIPS:
            ui_response = (
                f"{BRANDING} SLIP SECURITY ALERT\n"
                "----------------------------------------\n\n"
                "This receipt image has already been used in our system!\n"
                "Warning: Duplicate submission detected! Please upload a newly generated transaction slip."
                "\n----------------------------------------\n"
                f"Security Engine: {BRANDING}"
            )
            bot.reply_to(message, ui_response)
        else:
            save_hash(img_hash)
            ui_response = (
                f"{BRANDING} SLIP CHECK SUCCESS\n"
                "----------------------------------------\n\n"
                "Transaction receipt verified successfully.\n"
                "This is a fresh transaction and safe to process."
                "\n----------------------------------------\n"
                f"Slip Token: `{img_hash[:12]}`"
            )
            bot.reply_to(message, ui_response, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"System Error: `{str(e)}`", parse_mode="Markdown")

# =====================================================================
# 📋 NO USERNAME FIX - ANIMATED HEADERS & MONOSPACE INSTANT COPY
# =====================================================================
def animate_copy_header(chat_id, message_id, final_text, markup):
    animation_steps = ["𝑷", "𝑷𝒂", "𝑷𝒂𝒚", "𝑷𝒂𝒚𝑿", "𝑷𝒂𝒚𝑿- Richmond", "𝑷𝒂𝒚𝑿-𝑴", "𝑷𝒂𝒚𝑿-𝑴𝑴"]
    for step in animation_steps:
        try:
            time.sleep(0.15)
            # အပေါ်ဆုံးခေါင်းစဉ် တစ်လုံးချင်းစီ ပြေးသွားမယ့် ပုံစံ
            bot.edit_message_text(
                text=f"{step}\n{final_text}",
                chat_id=chat_id,
                message_id=message_id,
                parse_mode="Markdown",
                reply_markup=markup
            )
        except Exception: pass

@bot.message_handler(commands=['copy'])
def handle_reply_copy(message):
    if not message.reply_to_message or not message.reply_to_message.text:
        return bot.reply_to(message, "Usage: Reply to any credential text with /copy command.")
    
    target_text = message.reply_to_message.text
    lines = [line.strip() for line in target_text.split('\n') if line.strip()]
    
    copy_markup = InlineKeyboardMarkup()
    found_elements = []
    monospace_text_block = ""

    # Elements များကို အသန့်ရှင်းဆုံး ခွဲထုတ်ခြင်း
    for raw_item in lines:
        if "/copy" in raw_item.lower() or "payx" in raw_item.lower():
            continue
            
        sub_items = [s.strip("(),. ") for s in raw_item.split() if s.strip("(),. ")]
        for item in sub_items:
            if item and item not in found_elements and len(item) >= 2:
                found_elements.append(item)
                
                # Inline Query စနစ်အစား Callback System ကို သုံးထားလို့ Username ကြီး လုံးဝထွက်မလာတော့ပါဘူး
                btn = InlineKeyboardButton(
                    text=f"{item}",
                    callback_data=f"copy_{item[:15]}"
                )
                copy_markup.row(btn)
                
                # 🎯 လူကြိုက်အများဆုံးဖြစ်တဲ့ စာသားကို ထိလိုက်တာနဲ့ တန်းပြီး Copy ဖြစ်သွားစေမယ့် Monospace Layout ပါ ပေါင်းထည့်ပေးခြင်း
                monospace_text_block += f"`{item}`\n"
                
    if not found_elements:
        return bot.reply_to(message, "Error: No extractable details found.")

    # ခေါင်းစဉ်နှင့် စာသား တွဲဖက်တည်ဆောက်ခြင်း
    final_body_text = f"Tap to copy:\n\n{monospace_text_block}"
    
    # ပထမဆုံး အမြန်ဆုံး အနေနဲ့ Message ထုတ်ပေးလိုက်မယ်
    sent_msg = bot.reply_to(message.reply_to_message, f".\n{final_body_text}", parse_mode="Markdown", reply_markup=copy_markup)
    
    # Thread ကို သုံးပြီး ခေါင်းစဉ်ကို တစ်လုံးချင်းစီ Animated အသက်သွင်းမယ်
    threading.Thread(
        target=animate_copy_header, 
        args=(message.chat.id, sent_msg.message_id, final_body_text, copy_markup), 
        daemon=True
    ).start()

# =====================================================================
# Game ID Verification Results Core (English Layout Only)
# =====================================================================
def parse_and_send_result(message, game_type, target_id, extra_id=None):
    display_id = f"{target_id} ({extra_id})" if extra_id else target_id
    api_query_id = f"{target_id}/{extra_id}" if extra_id else target_id
    
    status_msg = bot.reply_to(message, "Infiltrating central server database...")
    result, error = call_game_api(game_type, api_query_id)
    
    if error:
        bot.edit_message_text(f"Error: `{error}`\n\nDeveloper: {BRANDING}", message.chat.id, status_msg.message_id, parse_mode="Markdown")
        return
        
    if result:
        nickname = result.get("nickname") or result.get("username") or result.get("name") or "Hidden Account"
        
        cool_ui = (
            f"{game_type.upper()} PROFILE\n"
            "----------------------------------------\n\n"
            f"Name: `{nickname}`\n"
            f"ID: `{display_id}`\n\n"
            "----------------------------------------\n"
            f"Tap to copy:"
        )
        
        copy_markup = InlineKeyboardMarkup()
        btn_copy_name = InlineKeyboardButton(text=f"{nickname}", callback_data=f"copy_{nickname[:15]}")
        btn_copy_id = InlineKeyboardButton(text=f"{target_id}", callback_data=f"copy_{target_id}")
        
        copy_markup.row(btn_copy_name)
        copy_markup.row(btn_copy_id)
        
        bot.edit_message_text(cool_ui, message.chat.id, status_msg.message_id, parse_mode="Markdown", reply_markup=copy_markup)

# Commands routing
@bot.message_handler(commands=['ml'])
def handle_ml(message):
    match = re.search(r'/ml\s+(\d+)\s*\((.*?)\)', message.text)
    if not match: return bot.reply_to(message, "Invalid MLBB Format! Use: /ml 2112723799 (19915)")
    parse_and_send_result(message, "mlbb", match.group(1), match.group(2).strip())

@bot.message_handler(commands=['ff'])
def handle_ff(message):
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Invalid FF Format! Use: /ff [UID]")
    parse_and_send_result(message, "ff", args[1])

@bot.message_handler(commands=['pubg'])
def handle_pubg(message):
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Invalid PUBG Format! Use: /pubg [ID]")
    parse_and_send_result(message, "pubg", args[1])

@bot.message_handler(commands=['coc'])
def handle_coc(message):
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Invalid COC Format! Use: /coc [Player_Tag]")
    player_tag = args[1].replace("#", "").strip()
    parse_and_send_result(message, "coc", player_tag)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
