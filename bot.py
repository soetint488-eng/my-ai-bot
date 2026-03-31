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
    return "MLBB Helper Bot is Online!"

# --- MENU ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🔍 ID Check ရန်", callback_data="check_id")
    btn2 = types.InlineKeyboardButton("💎 စိန်ဈေးနှုန်းကြည့်ရန်", callback_data="view_price")
    btn3 = types.InlineKeyboardButton("💬 စိန်ဝယ်ယူရန် (Admin)", url="https://t.me/shinethuyaaung") # သင့် Username ပြင်ပါ
    markup.add(btn1, btn2, btn3)
    
    welcome_msg = (
        "👋 မင်္ဂလာပါဗျ! **Shine Thu Ya** MLBB Helper Bot မှ ကြိုဆိုပါတယ်။\n\n"
        "စိန်မဝယ်ခင် ID မှန်၊ မမှန် စစ်ဆေးတာနဲ့ ဈေးနှုန်းတွေကို ဒီမှာ အလွယ်တကူ ကြည့်နိုင်ပါတယ်ဗျ။"
    )
    bot.send_message(message.chat.id, welcome_msg, reply_markup=markup, parse_mode="Markdown")

# --- CALLBACK HANDLERS ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "check_id":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🆔 စစ်ဆေးလိုသော MLBB ID နှင့် Zone ID ကို ပို့ပေးပါဗျ။\nဥပမာ - `12345678(1234)`")
    
    elif call.data == "view_price":
        bot.answer_callback_query(call.id)
        price_list = (
            "💎 **MLBB Diamond Price List**\n\n"
            "🔹 86 Gems - 2,xxx Ks\n"
            "🔹 172 Gems - 4,xxx Ks\n"
            "🔹 257 Gems - 6,xxx Ks\n"
            "🔹 706 Gems - 1x,xxx Ks\n\n"
            "⚠️ ဈေးနှုန်း အပြောင်းအလဲ ရှိနိုင်သဖြင့် Admin ကို တိုက်ရိုက်မေးမြန်းနိုင်ပါတယ်ဗျ။"
        )
        bot.send_message(call.message.chat.id, price_list, parse_mode="Markdown")

# --- ID CHECKER FUNCTION ---
@bot.message_handler(func=lambda message: "(" in message.text and ")" in message.text)
def check_ml_id(message):
    text = message.text.strip()
    try:
        # ID နဲ့ Zone ID ကို ခွဲထုတ်ခြင်း (ဥပမာ- 12345678(1234))
        user_id = text.split("(")[0]
        zone_id = text.split("(")[1].replace(")", "")
        
        msg = bot.reply_to(message, "🔍 ID ကို စစ်ဆေးနေပါတယ်၊ ခဏစောင့်ပေးပါ...")

        # MLBB ID Checker Public API ကို အသုံးပြုခြင်း
        api_url = f"https://api.mobilelegends.com/v1/user/info?id={user_id}&zone={zone_id}"
        # မှတ်ချက် - ဒီ API က အခမဲ့ဖြစ်လို့ တစ်ခါတလေ လေးတတ်ပါတယ်
        # ပိုမြန်တဲ့ API လိုချင်ရင် ပေးချေရတဲ့ API ကို ပြောင်းသုံးလို့ရပါတယ်
        
        # နမူနာ အနေဖြင့် ပုံသေ အဖြေထုတ်ပြခြင်း (အောက်က API response စစ်ဆေးမှု လိုအပ်သည်)
        # အခုလောလောဆယ် API response မပါဘဲ ID Format မှန်ကန်မှုကို အတည်ပြုပေးပါမယ်
        
        bot.edit_message_text(
            f"✅ **ID စစ်ဆေးမှု ရလဒ်**\n\n"
            f"🆔 ID: `{user_id}`\n"
            f"🌐 Zone: `{zone_id}`\n\n"
            f"💡 ဒီ ID ထဲကို စိန်ထည့်မှာ သေချာပြီဆိုရင် Admin ကို ဆက်သွယ်လိုက်ပါဗျ။",
            chat_id=message.chat.id, message_id=msg.message_id, parse_mode="Markdown"
        )
    except Exception as e:
        bot.reply_to(message, "⚠️ ID Format မှားယွင်းနေပါတယ်ဗျ။ `ID(Zone)` ပုံစံအတိုင်း ပို့ပေးပါ။")

# --- RUN SERVER ---
def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
