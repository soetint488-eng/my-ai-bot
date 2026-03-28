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
BOT_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI" # သင့် Bot Token ကို ဒီမှာထည့်ပါ
GEMINI_KEY = "AIzaSyA3BIZ1Rf-DLTmyOgfh9n7BNFuBE-8B46c"
CHANNEL_USERNAME = "@aatomk"

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

# --- MUSIC SEARCH FUNCTION ---
@bot.message_handler(commands=['music', 'song'])
def search_music(message):
    query = message.text.replace('/music', '').replace('/song', '').strip()
    if not query:
        bot.reply_to(message, "သီချင်းနာမည် ရိုက်ပေးပါဗျ။\nဥပမာ- /music လမင်းနားမှာ")
        return

    bot.send_message(message.chat.id, f"🔍 '{query}' ကို ရှာဖွေနေပါတယ်...")
    
    ydl_opts = {'format': 'best', 'quiet': True, 'noplaylist': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            for entry in info['entries']:
                title = entry['title']
                url = entry['webpage_url']
                
                markup = types.InlineKeyboardMarkup()
                mp3_btn = types.InlineKeyboardButton("🎵 MP3 Download", url=f"https://yt-download.org/api/button/mp3?url={url}")
                mp4_btn = types.InlineKeyboardButton("🎬 MP4 Download", url=f"https://yt-download.org/api/button/videos?url={url}")
                markup.add(mp3_btn, mp4_btn)
                
                bot.send_message(message.chat.id, f"🎧 **{title}**", reply_markup=markup, parse_mode="Markdown")
        except:
            bot.reply_to(message, "ရှာမတွေ့ပါဘူးဗျာ။")

# --- GEMINI CHAT + VOICE ---
@bot.message_handler(func=lambda message: True)
def chat_with_gemini(message):
    # Channel Join စစ်ဆေးခြင်း (Optional)
    try:
        user_id = message.from_user.id
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        if status in ['left', 'kicked']:
            bot.reply_to(message, f"Bot သုံးရန် {CHANNEL_USERNAME} ကို အရင် Join ပေးပါဗျ။")
            return
    except:
        pass

    try:
        # Gemini စာသားထုတ်ခြင်း
        response = model.generate_content(message.text)
        reply_text = response.text
        
        # အသံပြောင်းခြင်း (edge-tts)
        voice_file = "reply.mp3"
        communicate = edge_tts.Communicate(reply_text[:200], "my-MM-ThihaNeural") # စာလုံး ၂၀၀ ထက်မပိုအောင် ဖြတ်ထားခြင်း
        asyncio.run(communicate.save(voice_file))
        
        with open(voice_file, "rb") as audio:
            bot.send_audio(message.chat.id, audio, caption=reply_text)
        os.remove(voice_file)
        
    except Exception as e:
        bot.reply_to(message, "Gemini အလုပ်မလုပ်သေးပါဘူးဗျ။")

# --- RUN SERVER ---
def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
