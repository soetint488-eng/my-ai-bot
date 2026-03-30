import telebot
from telebot import types
import requests
import os
from flask import Flask
from threading import Thread

# --- SETUP ---
# သင့် Bot Token နှင့် LeakCheck API Key
BOT_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
LEAKCHECK_KEY = "c961f5c177273840f4280335163ccbe37519b3df"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Phone Finder Bot is Online!"

# --- FIND FUNCTION ---
@bot.message_handler(func=lambda message: True)
def find_user(message):
    # Username ကို @ ပါပါ မပါပါ ဖယ်ထုတ်ခြင်း
    query = message.text.strip().replace('@', '')
    
    if not query:
        bot.reply_to(message, "🔍 ရှာဖွေလိုတဲ့ Telegram Username ကို ရိုက်ထည့်ပေးပါဗျ။")
        return

    msg = bot.reply_to(message, f"🔎 '@{query}' ရဲ့ ဖုန်းနံပါတ်ကို Leak Database များတွင် ရှာဖွေနေပါသည်...")
    
    # LeakCheck API သို့ လှမ်းမေးခြင်း
    lc_url = f"https://leakcheck.io/api/v2/query/{query}?type=username"
    headers = {"Authorization": f"Bearer {LEAKCHECK_KEY}"}
    
    try:
        response = requests.get(lc_url, headers=headers).json()
        
        result_text = f"👤 **Username:** @{query}\n\n"
        
        # Database ထဲမှာ အချက်အလက် ရှိ၊ မရှိ စစ်ဆေးခြင်း
        if response.get('success') and response.get('found', 0) > 0:
            result_text += f"✅ Database တွင် {response['found']} ခု တွေ့ရှိရပါသည်-\n"
            result_text += "--------------------------\n"
            
            # ရလာတဲ့ Result အားလုံးကို ပြပေးခြင်း
            for source in response.get('result', []):
                line = source.get('line', 'N/A')
                last_seen = source.get('last_seen', 'N/A')
                result_text += f"🔹 **Data:** `{line}`\n"
                
            result_text += "\n⚠️ မှတ်ချက် - ဖုန်းနံပါတ် အပြည့်အစုံ မမြင်ရလျှင် LeakCheck Premium ဝယ်ယူရန် လိုအပ်ပါသည်ဗျ။"
        else:
            result_text += "❌ ဒီ Username နဲ့ ပတ်သက်တဲ့ ဖုန်းနံပါတ်/Data ကို Leak Database များတွင် ရှာမတွေ့ပါဘူးဗျာ။\n\n💡 User က Privacy အလွန်လုံခြုံအောင် ပိတ်ထားခြင်း သို့မဟုတ် Data မပေါက်ကြားဖူးခြင်းကြောင့် ဖြစ်နိုင်ပါသည်။"

        # User ရဲ့ Profile သို့ တိုက်ရိုက်သွားရန် ခလုတ်
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("👤 View Telegram Profile", url=f"https://t.me/{query}")
        markup.add(btn)
        
        bot.edit_message_text(result_text, chat_id=message.chat.id, message_id=msg.message_id, reply_markup=markup, parse_mode="Markdown")
        
    except Exception as e:
        bot.edit_message_text(f"⚠️ ရှာဖွေရာမှာ အမှားတစ်ခု ရှိသွားပါတယ်ဗျ။\nError: {str(e)}", chat_id=message.chat.id, message_id=msg.message_id)

# --- RUN SERVER (၂၄ နာရီ Run ရန်) ---
def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
