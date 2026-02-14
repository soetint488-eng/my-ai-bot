import telebot
from telebot import types
import asyncio
import edge_tts
import os
import sqlite3
import threading
import http.server
import socketserver

# --- Render Port Binding (Error မတက်အောင် Dummy Server Run ခြင်း) ---
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

# Database Setup
def init_db():
    conn = sqlite3.connect('voice_bot.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    conn.commit()
    conn.close()

init_db()

user_settings = {}

async def save_voice(text, voice, speed, pitch, file_path):
    try:
        communicate = edge_tts.Communicate(text, voice, rate=speed, pitch=pitch)
        await communicate.save(file_path)
    except Exception as e:
        print(f"TTS Error: {e}")

def get_settings(user_id):
    if user_id not in user_settings:
        user_settings[user_id] = {'speed': '+0%', 'pitch': '+0Hz', 'gender': 'girl'}
    return user_settings[user_id]

def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

def get_user_count():
    try:
        conn = sqlite3.connect('voice_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0

# --- Start / Settings / Profile ---
@bot.message_handler(commands=['start', 'settings', 'profile'])
def start_and_settings(message):
    user_id = message.from_user.id
    
    conn = sqlite3.connect('voice_bot.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        btn_join = types.InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
        markup.add(btn_join)
        bot.send_message(user_id, f"❌ Bot ကို အသုံးပြုရန် {CHANNEL_USERNAME} ကို အရင် Join ပေးပါဦးဗျ။", reply_markup=markup)
        return

    s = get_settings(user_id)
    count = get_user_count()
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🚀 Speed +", callback_data="speed_up"),
               types.InlineKeyboardButton("🐌 Speed -", callback_data="speed_down"),
               types.InlineKeyboardButton("📢 Pitch +", callback_data="pitch_up"),
               types.InlineKeyboardButton("🔉 Pitch -", callback_data="pitch_down"))
    markup.add(types.InlineKeyboardButton("🔄 Reset", callback_data="reset"))
    
    msg = (f"👤 **Bot Profile & Settings**\n\n"
           f"👥 Total Bot Users: `{count}`\n"
           f"🆔 Your ID: `{user_id}`\n\n"
           f"🏃 Speed: `{s['speed']}`\n"
           f"🎼 Pitch: `{s['pitch']}`\n\n"
           f"စာရိုက်ပြီး အသံပြောင်းနိုင်ပါပြီဗျ။")
    
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

# --- Callback Handler (ခလုတ်များအတွက်) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    if not is_subscribed(user_id):
        bot.answer_callback_query(call.id, "Channel ကို အရင် Join ပါ!")
        return

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
        bot.answer_callback_query(call.id, f"Selected {call.data} voice!")
        process_voice_conversion(call.message, user_id)
        return

    bot.answer_callback_query(call.id) # ခလုတ်နှိပ်တာ အောင်မြင်ကြောင်း အသိပေးချက်
    
    count = get_user_count()
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🚀 Speed +", callback_data="speed_up"),
               types.InlineKeyboardButton("🐌 Speed -", callback_data="speed_down"),
               types.InlineKeyboardButton("📢 Pitch +", callback_data="pitch_up"),
               types.InlineKeyboardButton("🔉 Pitch -", callback_data="pitch_down"))
    markup.add(types.InlineKeyboardButton("🔄 Reset", callback_data="reset"))
    
    msg = (f"👤 **Bot Profile & Settings**\n\n"
           f"👥 Total Bot Users: `{count}`\n"
           f"🏃 Speed: `{s['speed']}`\n"
           f"🎼 Pitch: `{s['pitch']}`")
    
    try:
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    except: pass

@bot.message_handler(func=lambda m: True)
def on_message(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        start_and_settings(message)
        return

    user_settings[f"last_text_{user_id}"] = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👦 Boy", callback_data="boy"),
               types.InlineKeyboardButton("👧 Girl", callback_data="girl"))
    bot.send_message(message.chat.id, "ဘယ်သူ့အသံနဲ့ နားထောင်မလဲ?", reply_markup=markup)

def process_voice_conversion(message, user_id):
    text = user_settings.get(f"last_text_{user_id}")
    if not text: return
    
    s = get_settings(user_id)
    file_name = f"voice_{user_id}.mp3"
    is_myanmar = any('\u1000' <= char <= '\u109F' for char in text)
    
    if s['gender'] == "boy":
        voice = "my-MM-ThihaNeural" if is_myanmar else "en-US-GuyNeural"
    else:
        voice = "my-MM-NilarNeural" if is_myanmar else "en-US-AvaNeural"
        
    msg = bot.send_message(message.chat.id, "⏳ Generating voice...")
    
    try:
        asyncio.run(save_voice(text, voice, s['speed'], s['pitch'], file_name))
        if os.path.exists(file_name):
            with open(file_name, 'rb') as audio:
                bot.send_voice(message.chat.id, audio, caption=f"🔊 Voice: {s['gender']} | Speed: {s['speed']}")
            os.remove(file_name)
        else:
            bot.send_message(message.chat.id, "⚠️ Error: အသံထုတ်မရပါ")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Error: {str(e)}")
    
    try:
        bot.delete_message(message.chat.id, msg.message_id)
    except: pass

print("KCT Voice Bot is running safely...")
bot.polling(none_stop=True)
