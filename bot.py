import telebot
import requests
import time
import os
import random
import string
from threading import Thread
from flask import Flask, request, jsonify

# ==================== [ CONFIGURATIONS ] ====================
BOT_TOKEN = "8702294693:AAHff0iYwzElcLNZzPhlXodImHePQuzYDl0"

RAPIDAPI_URL = "https://undress-ai-api.p.rapidapi.com/api/videoGenerations/animate"
RAPIDAPI_HOST = "undress-ai-api.p.rapidapi.com"
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"

# Render App URL (ဥပမာ- https://my-ai-bot-xkv8.onrender.com)
# ⚠️ မိမိ၏ Render Web Service URL ကို အောက်တွင် အမှန်အတိုင်း ပြောင်းလဲပေးပါရန်
RENDER_WEB_URL = "https://my-ai-bot-xkv8.onrender.com"
# ============================================================

bot = telebot.TeleBot(BOT_TOKEN, num_threads=1)
app = Flask(__name__)

# Random Name နှင့် ID ထုတ်ပေးရန် Function
def generate_random_string(length=15):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_id():
    return str(random.randint(100000000, 999999999))

# --- Flask Webhook Receiver (API မှ ဗီဒီယိုပြီးပါက လှမ်းပို့မည့် နေရာ) ---
@app.route('/')
def home():
    return "Bot Server is Alive!", 200

@app.route('/webhook/<chat_id>', methods=['POST'])
def api_webhook(chat_id):
    try:
        data = request.json or request.form
        print(f"📩 Webhook Received for Chat ID {chat_id}: {data}")
        
        # API မှ ပြန်ပေးလေ့ရှိသော key နာမည်များအတိုင်း ဗီဒီယိုလင့်ခ်ကို ဆွဲထုတ်ခြင်း
        video_url = data.get("video_url") or data.get("url") or data.get("output") or data.get("data", {}).get("url")
        
        if video_url:
            # ဗီဒီယိုလင့်ခ်ကို User ဆီ တိုက်ရိုက် လှမ်းပို့ပေးခြင်း
            bot.send_video(
                chat_id=chat_id, 
                video=video_url, 
                caption="✨ **AI မှ သင့်ဗီဒီယိုကို ဖန်တီးပေးပြီးပါပြီဗျာ။**"
            )
        else:
            bot.send_message(chat_id=chat_id, text=f"⚠️ ဗီဒီယို အောင်မြင်စွာ ပြီးဆုံးသော်လည်း လင့်ခ်ရှာမတွေ့ပါ။\n**Data:** `{str(data)}`")
            
    except Exception as e:
        print(f"Error in Webhook: {str(e)}")
        
    return jsonify({"status": "success"}), 200

# --- Telegram Bot ရဲ့ လုပ်ဆောင်ချက်များ ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_text = (
        "🤖 **Undress AI Video Bot မှ ကြိုဆိုပါတယ်**\n\n"
        "ကျွန်တော့်ဆီကို ပြုပြင်လိုတဲ့ ဓာတ်ပုံတစ်ပုံ ပို့ပေးလိုက်ပါဗျာ။"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    status_msg = bot.reply_to(message, "⏳ ဓာတ်ပုံဒေတာကို စစ်ဆေးနေပါပြီ... ခေတ္တစောင့်ပါဗျာ။")
    
    try:
        # ၁။ Telegram Server မှ ဓာတ်ပုံ Link ကို ရယူခြင်း
        file_info = bot.get_file(message.photo[-1].file_id)
        telegram_img_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        
        bot.edit_message_text("🪄 API ဆာဗာသို့ တောင်းဆိုချက် ပို့နေပါပြီ... (ဗီဒီယိုလုပ်ရန် စောင့်ဆိုင်းရပါမည်)", chat_id=message.chat.id, message_id=status_msg.message_id)
        
        # ၂။ Headers နှင့် Payload ပြင်ဆင်ခြင်း
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "x-rapidapi-host": RAPIDAPI_HOST,
            "x-rapidapi-key": RAPIDAPI_KEY
        }
        
        # User တစ်ယောက်ချင်းစီအတွက် Webhook Link ကို ခွဲပေးခြင်း
        user_webhook = f"{RENDER_WEB_URL}/webhook/{message.chat.id}"
        
        # အစ်ကိုပေးထားသော cURL အတိုင်း form-data တည်ဆောက်ခြင်း
        payload = {
            "image": telegram_img_url,
            "name": generate_random_string(),
            "id_gen": generate_random_id(),
            "webhook": user_webhook
        }
        
        # ၃။ API ထံ လှမ်းပို့ခြင်း
        response = requests.post(RAPIDAPI_URL, headers=headers, data=payload)
        
        if response.status_code in [200, 201, 202]:
            bot.edit_message_text(
                "🚀 **API သို့ တင်သွင်းခြင်း အောင်မြင်ပါသည်။**\n\n"
                "AI မှ ဗီဒီယိုဖန်တီးခြင်းကို နောက်ကွယ်တွင် လုပ်ဆောင်နေပါသည်။ "
                "ပြီးစီးပါက ဗီဒီယိုဖိုင်ကို ဤနေရာသို့ အလိုအလျောက် လှမ်းပို့ပေးပါလိမ့်မည်ဗျာ။", 
                chat_id=message.chat.id, 
                message_id=status_msg.message_id,
                parse_mode="Markdown"
            )
        else:
            bot.edit_message_text(
                f"❌ API Error ဖြစ်သွားပါပြီ။\nStatus Code: {response.status_code}\nMessage: {response.text}", 
                chat_id=message.chat.id, 
                message_id=status_msg.message_id
            )
            
    except Exception as e:
        bot.edit_message_text(f"❌ Error ဖြစ်ပွားသွားသည် - {str(e)}", chat_id=message.chat.id, message_id=status_msg.message_id)

# --- Flask Server နှင့် Bot ပူးတွဲမောင်းနှင်ရန် Thread ခွဲခြင်း ---
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # ၁။ Flask Server မောင်းနှင်ခြင်း (Render Port Error ကျော်ရန်နှင့် Webhook လက်ခံရန်)
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # ၂။ Bot Connection ရှင်းလင်းခြင်း
    print("🧹 Cleaning old bot connections...")
    bot.remove_webhook()
    time.sleep(2)
    
    print("🤖 Undress AI Video Bot & Webhook Starter Active...")
    bot.infinity_polling()
