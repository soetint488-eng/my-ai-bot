import telebot
from telebot import types
import google.generativeai as genai
import edge_tts
import asyncio
import yt_dlp
import os
import requests
from flask import Flask
from threading import Thread

# --- SETUP ---
BOT_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
GEMINI_KEY = "AIzaSyAnOv8Pqe7W2dz84DIICEn11kNUrZdPKqU"
LEAKCHECK_KEY = "c961f5c177273840f4280335163ccbe37519b3df"
CHANNEL_USERNAME = "@aatomk"

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask('')

@app.route('/')
def home():
    return "Bot is Online!"

# --- OSINT: FIND PHONE BY USERNAME ---
@bot.message_handler(commands=['find'])
def find_user(message):
    query = message.text.replace('/find', '').strip().replace('@', '')
    if not query:
        bot.reply_to(message, "🔍 ရှာဖွေလိုတဲ့ Username ရိုက်ပေးပါဗျ။\nဥပမာ- /find shinethuyaaung")
        return

    bot.send_message(message.chat.id, f"🔎 '{query}' ကို Leak Database များတွင် ရှာဖွေနေပါသည်...")
    
    # LeakCheck API Call
    url = f"https://leakcheck.io/api/v2/query/{query}?type=username"
    headers = {"Authorization": f"Bearer {LEAKCHECK_KEY}"}
    
    try:
        response = requests.get(url, headers=headers).json()
        if response.get('success') and response.get('found', 0) > 0:
            result_text = f"✅ အချက်အလက် {response['found']} ခု တွေ့ရှိရပါသည်-\n\n"
            for source in response['result'][:3]: # ထိပ်ဆုံး ၃ ခုပဲပြမယ်
                line = source.get('line', 'N/A')
                result_text += f"🔹 Data: `{line}`\n"
            bot.send_message(message.chat.id, result_text, parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ ဒီ Username နဲ့ ပတ်သက်တဲ့ ဖုန်းနံပါတ်/Data ရှာမတွေ့ပါဘူးဗျာ။")
    except:
        bot.reply_to(message, "⚠️ API Error ဖြစ်သွားပါတယ်ဗျ။")

# --- MUSIC SEARCH ---
@bot.message_handler(commands=['music', 'song'])
def search_music(message):
    query = message.text.replace('/music', '').replace('/song', '').strip()
    if not query:
        bot.reply_to(message, "💡 သီချင်းနာမည် ရိုက်ပေးပါ။")
        return
    msg = bot.reply_to(message, "🔍 YouTube မှာ ရှာနေပါတယ်...")
    ydl_opts = {'format': 'best', 'quiet': True, 'default_search': 'ytsearch5', 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            bot.delete_message(message.chat.id, msg.message_id)
            for entry in info['entries'][:5]:
                title, vid_id = entry.get('title'), entry.get('id')
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🎵 MP3", url=f"https://api.vevioz.com/api/button/mp3/{vid_id}"))
                markup.add(types.InlineKeyboardButton("🎬 MP4", url=f"https://api.vevioz.com/api/button/videos/{vid_id}"))
                bot.send_message(message.chat.id, f"🎧 **{title}**", reply_markup=markup, parse_mode="Markdown")
        except: bot.reply_to(message, "⚠️ ရှာမရပါဘူးဗျ။")

# --- GEMINI CHAT + VOICE ---
@bot.message_handler(func=lambda message: True)
def chat_handler(message):
    try:
        res = model.generate_content(message.text)
        reply = res.text
        v_file = f"v_{message.chat.id}.mp3"
        async def make_v():
            await edge_tts.Communicate(reply[:300], "my-MM-ThihaNeural").save(v_file)
        asyncio.run(make_v())
        with open(v_file, "rb") as f:
            bot.send_audio(message.chat.id, f, caption=reply)
        if os.path.exists(v_file): os.remove(v_file)
    except:
        try: bot.reply_to(message, model.generate_content(message.text).text)
        except: bot.reply_to(message, "🤖 Gemini Error တက်နေပါတယ်ဗျ။")

# --- RUN ---
def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
