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
# သင့် Bot Token ကို အောက်ကနေရာမှာ အတိအကျ ထည့်ပါ
BOT_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI" 
GEMINI_KEY = "AIzaSyA3BIZ1Rf-DLTmyOgfh9n7BNFuBE-8B46c"
CHANNEL_USERNAME = "@aatomk"

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)

# Gemini Safety Settings (Block မဖြစ်အောင် အကုန်ဖွင့်ထားခြင်း)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]
model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)

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
    
    ydl_opts = {'format': 'best', 'quiet': True, 'noplaylist': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # အပုဒ် ၅၀ လောက်အထိ ရှာပေးနိုင်အောင် ytsearch5 သုံးထားပါတယ်
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            if not info['entries']:
                bot.edit_message_text("❌ ရှာမတွေ့ပါဘူးဗျာ။", chat_id=message.chat.id, message_id=msg.message_id)
                return

            bot.delete_message(message.chat.id, msg.message_id)
            
            for entry in info['entries']:
                title = entry['title']
                url = entry['webpage_url']
                duration = entry.get('duration_string', 'N/A')
                
                markup = types.InlineKeyboardMarkup()
                # Third-party download API ကို သုံးထားလို့ MP3/MP4 တိုက်ရိုက်ဒေါင်းနိုင်ပါမယ်
                mp3_btn = types.InlineKeyboardButton("🎵 MP3 Download", url=f"https://yt-download.org/api/button/mp3?url={url}")
                mp4_btn = types.InlineKeyboardButton("🎬 MP4 Download", url=f"https://yt-download.org/api/button/videos?url={url}")
                markup.add(mp3_btn, mp4_btn)
                
                bot.send_message(message.chat.id, f"🎧 **{title}**\n⏱ ကြာချိန်: {duration}", reply_markup=markup, parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, "⚠️ ရှာဖွေရာမှာ အမှားတစ်ခု ရှိသွားပါတယ်။")

# --- GEMINI CHAT + VOICE (စာရိုက်ရင် အသံနဲ့ပြန်ဖြေရန်) ---
@bot.message_handler(func=lambda message: True)
def chat_with_gemini(message):
    # Channel Join စစ်ဆေးခြင်း
    try:
        user_id = message.from_user.id
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        if status in ['left', 'kicked']:
            bot.reply_to(message, f"❌ Bot ကို အသုံးပြုရန် {CHANNEL_USERNAME} ကို အရင် Join ပေးပါဗျ။")
            return
    except:
        pass

    try:
        # Gemini စာသား ထုတ်ပေးခြင်း
        response = model.generate_content(message.text)
        reply_text = response.text
        
        # အသံပြောင်းခြင်း (edge-tts)
        voice_file = f"voice_{message.chat.id}.mp3"
        # စာသားအရမ်းရှည်ရင် Error တက်နိုင်လို့ ဖြတ်ထားပါတယ်
        short_text = reply_text[:500]
        
        async def generate_voice():
            communicate = edge_tts.Communicate(short_text, "my-MM-ThihaNeural")
            await communicate.save(voice_file)

        asyncio.run(generate_voice())
        
        # စာရော အသံဖိုင်ရော ပို့ပေးခြင်း
        with open(voice_file, "rb") as audio:
            bot.send_audio(message.chat.id, audio, caption=reply_text)
        
        if os.path.exists(voice_file):
            os.remove(voice_file)
            
    except Exception as e:
        # Error တက်ရင် ဘာလို့တက်လဲ သိရအောင် error message ပြခိုင်းထားပါတယ်
        bot.reply_to(message, f"🤖 Gemini Error: {str(e)}")

# --- RUN WEB SERVER ---
def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    # Bot ကို အမြဲ Run နေအောင် လုပ်ခြင်း
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
