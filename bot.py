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
BOT_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI" # သင့် Bot Token အစစ်ကို ဒီမှာထည့်ပါ
GEMINI_KEY = "AIzaSyA3BIZ1Rf-DLTmyOgfh9n7BNFuBE-8B46c"
CHANNEL_USERNAME = "@aatomk"

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)

# Gemini Model Setup
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

# --- MUSIC SEARCH ---
@bot.message_handler(commands=['music', 'song'])
def search_music(message):
    query = message.text.replace('/music', '').replace('/song', '').strip()
    if not query:
        bot.reply_to(message, "💡 သီချင်းရှာရန် နာမည်ရိုက်ပေးပါ။\nဥပမာ- /music လမင်းနားမှာ")
        return

    msg = bot.reply_to(message, f"🔍 '{query}' ကို ရှာနေပါတယ်...")
    
    # YouTube Search Options
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
            
            for entry in info['entries'][:5]: # သီချင်း ၅ ပုဒ်ပြမယ်
                title = entry.get('title')
                url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                
                markup = types.InlineKeyboardMarkup()
                # Download Links (External API သုံးထားလို့ Render မှာ FFmpeg မလိုဘဲ ဒေါင်းနိုင်ပါမယ်)
                mp3_link = f"https://api.vevioz.com/api/button/mp3/{entry.get('id')}"
                mp4_link = f"https://api.vevioz.com/api/button/videos/{entry.get('id')}"
                
                mp3_btn = types.InlineKeyboardButton("🎵 MP3 Download", url=mp3_link)
                mp4_btn = types.InlineKeyboardButton("🎬 MP4 Download", url=mp4_link)
                markup.add(mp3_btn, mp4_btn)
                
                bot.send_message(message.chat.id, f"🎧 **{title}**", reply_markup=markup, parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, f"⚠️ ရှာဖွေရာမှာ အမှားရှိသွားပါတယ်: {str(e)}")

# --- GEMINI CHAT + VOICE ---
@bot.message_handler(func=lambda message: True)
def chat_with_gemini(message):
    try:
        # Gemini Response
        response = model.generate_content(message.text)
        reply_text = response.text
        
        # Voice Conversion
        voice_file = f"v_{message.chat.id}.mp3"
        
        async def make_voice():
            # စာသားအရမ်းရှည်ရင် ဖြတ်မယ်
            txt = reply_text[:300]
            communicate = edge_tts.Communicate(txt, "my-MM-ThihaNeural")
            await communicate.save(voice_file)

        asyncio.run(make_voice())
        
        with open(voice_file, "rb") as audio:
            bot.send_audio(message.chat.id, audio, caption=reply_text)
        
        if os.path.exists(voice_file):
            os.remove(voice_file)
            
    except Exception as e:
        # Gemini စာသားပဲ အရင်ပို့ကြည့်မယ်
        try:
            response = model.generate_content(message.text)
            bot.reply_to(message, response.text)
        except:
            bot.reply_to(message, "🤖 Gemini ခေတ္တ အလုပ်မလုပ်ပါဘူးဗျ။")

# --- RUN SERVER ---
def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
