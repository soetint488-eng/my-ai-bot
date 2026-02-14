import telebot
from telebot import types
import edge_tts
import os
import sqlite3
import threading
import http.server
import socketserver
import asyncio

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
bot = telebot.TeleBot(API_TOKEN, threaded=True) # Threaded mode ဖွင့်ထားပါသည်

user_settings = {}

def get_settings(user_id):
    if user_id not in user_settings:
        user_settings[user_id] = {'speed': '+0%', 'pitch': '+0Hz', 'gender': 'girl'}
    return user_settings[user_id]

# --- UI Design ---
def get_ui_markup(user_id):
    s = get_settings(user_id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"🚀 Speed ({s['speed']})", callback_data="none"),
        types.InlineKeyboardButton(f"🎼 Pitch ({s['pitch']})", callback_data="none")
    )
    markup.add(
        types.InlineKeyboardButton("➕ Speed", callback_data="speed_up"),
        types.InlineKeyboardButton("➖ Speed", callback_data="speed_down"),
        types.InlineKeyboardButton("➕ Pitch", callback_data="pitch_up"),
        types.InlineKeyboardButton("➖ Pitch", callback_data="pitch_down")
    )
    markup.add(
        types.InlineKeyboardButton("🔄 Reset Default", callback_data="reset"),
        types.InlineKeyboardButton("📢 Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
    )
    return markup

@bot.message_handler(commands=['start', 'settings'])
def welcome(message):
    user_id = message.from_user.id
    s = get_settings(user_id)
    panel_text = (
        "┏━━━━━━ PREMIUM VOICE ━━━━━━┓\n"
        f"┃  👤 User ID: `{user_id}`\n"
        f"┃  🏃 Speed: *{s['speed']}*\n"
        f"┃  🎼 Pitch: *{s['pitch']}*\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "✨ *စာရိုက်ပြီး ပို့ပေးပါ။ အသံပြောင်းပေးပါမည်။*"
    )
    bot.send_message(message.chat.id, panel_text, reply_markup=get_ui_markup(user_id), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_ui(call):
    user_id = call.from_user.id
    s = get_settings(user_id)
    
    if call.data == "none":
        bot.answer_callback_query(call.id)
        return

    # Settings logic
    if "speed" in call.data:
        val = int(s['speed'].replace('%', '').replace('+', ''))
        s['speed'] = f"+{val+10}%" if "up" in call.data else f"{val-10}%"
    elif "pitch" in call.data:
        val = int(s['pitch'].replace('Hz', '').replace('+', ''))
        s['pitch'] = f"+{val+5}Hz" if "up" in call.data else f"{val-5}Hz"
    elif call.data == "reset":
        user_settings[user_id] = {'speed': '+0%', 'pitch': '+0Hz', 'gender': 'girl'}

    if call.data in ["boy", "girl"]:
        s['gender'] = call.data
        bot.answer_callback_query(call.id, "🎤 အသံဖိုင် ပြုလုပ်နေသည်...")
        # အသံထုတ်လုပ်ငန်းစဉ်ကို thread ခွဲမောင်းပါမည်
        threading.Thread(target=generate_voice_thread, args=(call.message, user_id)).start()
        return

    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_ui_markup(user_id))
    except: pass

@bot.message_handler(func=lambda m: True)
def text_input(message):
    user_id = message.from_user.id
    user_settings[f"text_{user_id}"] = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👦 Boy Voice", callback_data="boy"),
               types.InlineKeyboardButton("👧 Girl Voice", callback_data="girl"))
    bot.send_message(message.chat.id, "🎙 *ဘယ်သူ့အသံနဲ့ နားထောင်မလဲ?*", reply_markup=markup, parse_mode="Markdown")

# --- Voice Generation Logic ---
def generate_voice_thread(message, user_id):
    text = user_settings.get(f"text_{user_id}")
    s = get_settings(user_id)
    file_path = f"v_{user_id}.mp3"
    
    is_mm = any('\u1000' <= c <= '\u109F' for c in text)
    voice = ("my-MM-ThihaNeural" if is_mm else "en-US-GuyNeural") if s['gender'] == "boy" else \
            ("my-MM-NilarNeural" if is_mm else "en-US-AvaNeural")
            
    wait = bot.send_message(message.chat.id, "⌛ *Processing...*")
    
    async def make_file():
        communicate = edge_tts.Communicate(text, voice, rate=s['speed'], pitch=s['pitch'])
        await communicate.save(file_path)

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(make_file())
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                bot.send_voice(message.chat.id, f, caption=f"✨ *Voice Generated!*")
            os.remove(file_path)
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Error ဖြစ်သွားပါသည်။")
        
    bot.delete_message(message.chat.id, wait.message_id)

bot.polling(none_stop=True)
