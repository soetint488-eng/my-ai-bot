import telebot
from telebot import types
import asyncio
import edge_tts
import os
import sqlite3
import threading
import http.server
import socketserver

# --- Render Port Binding ---
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- Bot Setup ---
API_TOKEN = '8463257017:AAHQH_bFCF1ENzJtwy_zswp1VywkofI4nA0'
CHANNEL_USERNAME = '@KCTagain007'
bot = telebot.TeleBot(API_TOKEN)

# Database
def init_db():
    conn = sqlite3.connect('voice_bot.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    conn.commit()
    conn.close()

init_db()
user_settings = {}

def get_settings(user_id):
    if user_id not in user_settings:
        user_settings[user_id] = {'speed': '+0%', 'pitch': '+0Hz', 'gender': 'girl'}
    return user_settings[user_id]

# --- UI Design Components ---
def get_ui_markup(user_id):
    s = get_settings(user_id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Speed & Pitch Buttons
    markup.add(
        types.InlineKeyboardButton(f"🚀 Speed ({s['speed']})", callback_data="ui_speed"),
        types.InlineKeyboardButton(f"🎼 Pitch ({s['pitch']})", callback_data="ui_pitch")
    )
    
    # Control Buttons
    markup.add(
        types.InlineKeyboardButton("➕ Speed", callback_data="speed_up"),
        types.InlineKeyboardButton("➖ Speed", callback_data="speed_down"),
        types.InlineKeyboardButton("➕ Pitch", callback_data="pitch_up"),
        types.InlineKeyboardButton("➖ Pitch", callback_data="pitch_down")
    )
    
    # Reset & Support
    markup.add(
        types.InlineKeyboardButton("🔄 Reset Default", callback_data="reset"),
        types.InlineKeyboardButton("📢 Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
    )
    return markup

# --- Handlers ---
@bot.message_handler(commands=['start', 'settings'])
def welcome(message):
    user_id = message.from_user.id
    
    # Save User
    conn = sqlite3.connect('voice_bot.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

    s = get_settings(user_id)
    panel_text = (
        "┏━━━━━━ PREMIUM VOICE ━━━━━━┓\n"
        "┃\n"
        f"┃  👤 User ID: `{user_id}`\n"
        f"┃  🏃 Speed: *{s['speed']}*\n"
        f"┃  🎼 Pitch: *{s['pitch']}*\n"
        "┃\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "✨ *စာရိုက်ပြီး ပို့ပေးပါ။ အသံပြောင်းပေးပါမည်။*"
    )
    bot.send_message(message.chat.id, panel_text, reply_markup=get_ui_markup(user_id), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_ui(call):
    user_id = call.from_user.id
    s = get_settings(user_id)
    
    if call.data == "speed_up":
        val = int(s['speed'].replace('%', '').replace('+', '')) + 10
        s['speed'] = f"+{val}%" if val >= 0 else f"{val}%"
    elif call.data == "speed_down":
        val = int(s['speed'].replace('%', '').replace('+', '')) - 10
        s['speed'] = f"+{val}%" if val >= 0 else f"{val}%"
    elif call.data == "pitch_up":
        val = int(s['pitch'].replace('Hz', '').replace('+', '')) + 5
        s['pitch'] = f"+{val}Hz" if val >= 0 else f"{val}Hz"
    elif call.data == "pitch_down":
        val = int(s['pitch'].replace('Hz', '').replace('+', '')) - 5
        s['pitch'] = f"+{val}Hz" if val >= 0 else f"{val}Hz"
    elif call.data == "reset":
        user_settings[user_id] = {'speed': '+0%', 'pitch': '+0Hz', 'gender': 'girl'}
    
    if call.data in ["boy", "girl"]:
        s['gender'] = call.data
        bot.answer_callback_query(call.id, "🎤 အသံဖိုင် ပြုလုပ်နေသည်...")
        generate_voice_final(call.message, user_id)
        return

    bot.answer_callback_query(call.id)
    
    # Update UI Panel
    panel_text = (
        "┏━━━━━━ PREMIUM VOICE ━━━━━━┓\n"
        "┃\n"
        f"┃  👤 User ID: `{user_id}`\n"
        f"┃  🏃 Speed: *{s['speed']}*\n"
        f"┃  🎼 Pitch: *{s['pitch']}*\n"
        "┃\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
    )
    try:
        bot.edit_message_text(panel_text, call.message.chat.id, call.message.message_id, 
                              reply_markup=get_ui_markup(user_id), parse_mode="Markdown")
    except: pass

@bot.message_handler(func=lambda m: True)
def text_input(message):
    user_id = message.from_user.id
    user_settings[f"text_{user_id}"] = message.text
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("👦 Boy Voice", callback_data="boy"),
        types.InlineKeyboardButton("👧 Girl Voice", callback_data="girl")
    )
    bot.send_message(message.chat.id, "🎙 *ဘယ်သူ့အသံနဲ့ နားထောင်မလဲ?*", reply_markup=markup, parse_mode="Markdown")

def generate_voice_final(message, user_id):
    text = user_settings.get(f"text_{user_id}")
    s = get_settings(user_id)
    file_path = f"voice_{user_id}.mp3"
    
    is_mm = any('\u1000' <= c <= '\u109F' for c in text)
    voice = ("my-MM-ThihaNeural" if is_mm else "en-US-GuyNeural") if s['gender'] == "boy" else \
            ("my-MM-NilarNeural" if is_mm else "en-US-AvaNeural")
            
    wait = bot.send_message(message.chat.id, "⌛ *Processing...*")
    try:
        asyncio.run(edge_tts.Communicate(text, voice, rate=s['speed'], pitch=s['pitch']).save(file_path))
        with open(file_path, 'rb') as f:
            bot.send_voice(message.chat.id, f, caption=f"✨ *Voice Generated!*\n👤 Role: {s['gender'].capitalize()}\n🚀 Speed: {s['speed']}", parse_mode="Markdown")
        os.remove(file_path)
    except:
        bot.send_message(message.chat.id, "❌ အမှားတစ်ခု ဖြစ်သွားသည်။")
    bot.delete_message(message.chat.id, wait.message_id)

bot.polling(none_stop=True)
