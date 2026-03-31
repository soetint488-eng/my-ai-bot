import telebot
from telebot import types
import requests
import os
from flask import Flask
from threading import Thread

# --- SETUP ---
BOT_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "MLBB Checker Bot is Online!"

# --- ID CHECKER FUNCTION ---
@bot.message_handler(func=lambda message: "(" in message.text and ")" in message.text)
def check_ml_id(message):
    text = message.text.strip()
    try:
        # ID နဲ့ Zone ID ကို ခွဲထုတ်ခြင်း
        user_id = text.split("(")[0].strip()
        zone_id = text.split("(")[1].replace(")", "").strip()
        
        msg = bot.reply_to(message, "🔍 Server မှာ Name ကို ရှာဖွေနေပါတယ်၊ ခဏစောင့်ပေးပါ...")

        # MLBB API (ဒီ API က ID နဲ့ Zone ကို စစ်ပြီး Name ပြပေးပါတယ်)
        api_url = f"https://api.mobilelegends.com/v1/user/info?id={user_id}&zone={zone_id}"
        
        # ပိုတည်ငြိမ်တဲ့ တခြား API တစ်ခုကိုပါ အရံအနေနဲ့ သုံးပါမယ်
        backup_api = f"https://smile-one.me/api/checkrole?user_id={user_id}&zone_id={zone_id}&pid=26"

        try:
            # API ကို လှမ်းခေါ်ခြင်း
            response = requests.get(backup_api, timeout=10).json()
            
            if response.get('status') == 200:
                username = response.get('username') # User Name ရပြီ
                
                result_text = (
                    "✅ **ID စစ်ဆေးမှု ရလဒ်**\n\n"
                    f"👤 **Name:** `{username}`\n"
                    f"🆔 **ID:** `{user_id}`\n"
                    f"🌐 **Zone:** `{zone_id}`\n\n"
                    "💡 နာမည်နဲ့ ID မှန်ကန်တယ်ဆိုရင် Admin ဆီမှာ စိန်ဝယ်ယူနိုင်ပါပြီဗျ။"
                )
                
                # အောင်မြင်ရင် ပြန်ပို့မယ်
                bot.edit_message_text(result_text, chat_id=message.chat.id, message_id=msg.message_id, parse_mode="Markdown")
            else:
                bot.edit_message_text("❌ ID ရှာမတွေ့ပါဘူးဗျာ။ ID နဲ့ Zone မှန်အောင် ပြန်ရိုက်ပေးပါဦး။", chat_id=message.chat.id, message_id=msg.message_id)
                
        except:
            bot.edit_message_text("⚠️ API Server ခေတ္တ အလုပ်မလုပ်ပါဘူးဗျ။ နောက်မှ ပြန်စမ်းကြည့်ပါဦး။", chat_id=message.chat.id, message_id=msg.message_id)

    except Exception as e:
        bot.reply_to(message, "⚠️ ID Format မှားယွင်းနေပါတယ်ဗျ။ `ID(Zone)` ပုံစံအတိုင်း ပို့ပေးပါ။\nဥပမာ - `701906179(8798)`")

# --- START MENU ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 မင်္ဂလာပါ! MLBB ID စစ်ဖို့အတွက် `ID(Zone)` ပုံစံအတိုင်း ပို့ပေးပါဗျ။\n\nဥပမာ - `701906179(8798)`")

# --- RUN SERVER ---
def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
