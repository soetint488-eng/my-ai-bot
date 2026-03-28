import telebot
from telebot import types
import google.generativeai as genai
import edge_tts
import asyncio
import yt_dlp
import os
from flask import Flask
from threading import Thread

# --- SETUP ---
BOT_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
GEMINI_KEY = "AIzaSyAnOv8Pqe7W2dz84DIICEn11kNUrZdPKqU"
CHANNEL_USERNAME = "@aatomk"

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)

# Gemini Model Setup
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

# --- MUSIC SEARCH (/music နာမည်) ---
@bot.message_handler(commands=['music', 'song'])
def search_music(message):
    query = message.text.replace('/music', '').replace('/song', '').strip()
    if not query:
        bot.reply_to(message, "💡 သီချင်းရှာရန် နာမည်ရိုက်ပေးပါ။\nဥပမာ- /music လမင်းနားမှာ")
        return

    msg = bot.reply_to(message, f"🔍 '{query}' ကို YouTube မှာ ရှာနေပါတယ်...")
    
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch5',
        'extract_flat': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if not info or 'entries' not in info:
                bot.edit_message_text("❌ ရှာမတွေ့ပါဘူးဗျာ။", chat_id=message.chat.id, message_id=msg.message_id)
                return

            bot.delete_message(message.chat.id, msg.message_id)
            
            for entry in info['entries'][:5]:
                title = entry.get('title')
                vid_id = entry.get('id')
                
                markup = types.InlineKeyboardMarkup()
                # ပိုတည်ငြိမ်တဲ့ Download API (Vevioz)
                mp3_url = f"https://api.vevioz.com/api/button/mp3/{vid_id}"
                mp4_url = f"https://api.vevioz.com/api/button/videos/{vid_id}"
                
                markup.add(types.InlineKeyboardButton("🎵 MP3 Download", url=mp3_url))
                markup.add(types.InlineKeyboardButton("🎬 MP4 Download", url=mp4_url))
                
                bot.send_message(message.chat.id, f"🎧 **{title}**", reply_markup=markup, parse_mode="Markdown")
        except:
            bot.reply_to(message, "⚠️ သီချင်းရှာမရပါဘူးဗျာ။")

# --- GEMINI CHAT + VOICE (စာရိုက်ရင် အသံနဲ့ပြန်ဖြေရန်) ---
@bot.message_handler(func=lambda message: True)
def chat_with_gemini(message):
    # Channel Join စစ်ဆေးခြင်း
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, message.from_user.id).status
        if status in ['left', 'kicked']:
            bot.reply_to(message, f"❌ Bot သုံးရန် {CHANNEL_USERNAME} ကို Join ပါ။")
            return
    except: pass

    try:
        # Gemini စာသား ထုတ်ပေးခြင်း
        response = model.generate_content(message.text)
        reply_text = response.text
        
        # အသံပြောင်းခြင်း (edge-tts)
        voice_file = f"v_{message.chat.id}.mp3"
        
        async def make_voice():
            # မြန်မာသံ (ThihaNeural) ဖြင့် အသံထွက်ပေးခြင်း
            communicate = edge_tts.Communicate(reply_text[:300], "my-MM-ThihaNeural")
            await communicate.save(voice_file)

        asyncio.run(make_voice())
        
        with open(voice_file, "rb") as audio:
            bot.send_audio(message.chat.id, audio, caption=reply_text)
        
        if os.path.exists(voice_file):
            os.remove(voice_file)
            
    except Exception as e:
        # အသံဖိုင် Error တက်ရင်တောင် စာသားတော့ ပြန်ဖြေပေးမယ်
        try:
            response = model.generate_content(message.text)
            bot.reply_to(message, response.text)
        except:
            bot.reply_to(message, "🤖 Gemini API ခေတ္တအလုပ်မလုပ်ပါဘူးဗျ။")

# --- RUN WEB SERVER ---
def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
