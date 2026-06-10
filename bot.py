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

RENDER_WEB_URL = "https://my-ai-bot-xkv8.onrender.com"
# ============================================================

bot = telebot.TeleBot(BOT_TOKEN, num_threads=1)
app = Flask(__name__)

def generate_random_string(length=15):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_id():
    return str(random.randint(100000000, 999999999))

# --- Flask Webhook Receiver ---
@app.route('/')
def home():
    return "Bot Server is Alive!", 200

@app.route('/webhook/<chat_id>', methods=['POST'])
def api_webhook(chat_id):
    try:
        data = request.json or request.form
        print(f"📩 Webhook Received for Chat ID {chat_id}: {data}")
        
        video_url = data.get("video_url") or data.get("url") or data.get("output") or data.get("data", {}).get("url")
        
        if video_url:
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
    status_msg = bot.reply_to(message, "⏳ ဓာတ်ပုံကို ရယူနေပါပြီ... ခေတ္တစောင့်ပါဗျာ။")
    
    try:
        # ၁။ Telegram Server မှ ဓာတ်ပုံဖိုင်ကို ဒေါင်းလုဒ်ဆွဲခြင်း
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        bot.edit_message_text("🌐 ဓာတ်ပုံကို Cloud Server သို့ လွှဲပြောင်းနေပါပြီ...", chat_id=message.chat.id, message_id=status_msg.message_id)
        
        # ၂။ Telegra.ph (Telegram Image Hosting) ပေါ်သို့ အလကား တိုက်ရိုက်တင်ခြင်း
        # ⚠️ မည်သည့် API Key မှ မလိုဘဲ အများသုံး Direct Link အဖြစ် ပြောင်းပေးပါသည်
        try:
            telegraph_res = requests.post(
                "https://telegra.ph/upload", 
                files={"file": ("image.jpg", downloaded_file, "image/jpeg")}
            ).json()
            
            # ထွက်လာသော path ကို အများသုံး link အဖြစ် ပြောင်းလဲခြင်း
            public_img_url = "https://telegra.ph" + telegraph_res[0]["src"]
            
        except Exception:
            bot.edit_message_text("❌ ဓာတ်ပုံကို လင့်ခ်ပြောင်းရတာ အဆင်မပြေဖြစ်သွားပါသည်။ တစ်ချက်ပြန်ပို့ကြည့်ပါဗျာ။", chat_id=message.chat.id, message_id=status_msg.message_id)
            return

        bot.edit_message_text("🪄 API ဆာဗာသို့ တောင်းဆိုချက် ပို့နေပါပြီ... (ဗီဒီယိုလုပ်ရန် စောင့်ဆိုင်းရပါမည်)", chat_id=message.chat.id, message_id=status_msg.message_id)
        
        # ၃။ Headers နှင့် Payload ပြင်ဆင်ခြင်း
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "x-rapidapi-host": RAPIDAPI_HOST,
            "x-rapidapi-key": RAPIDAPI_KEY
        }
        
        user_webhook = f"{RENDER_WEB_URL}/webhook/{message.chat.id}"
        
        payload = {
            "image": public_img_url,  # Telegra.ph လင့်ခ် (API တိုက်ရိုက် ဝင်ဆွဲနိုင်ပါသည်)
            "name": generate_random_string(),
            "id_gen": generate_random_id(),
            "webhook": user_webhook
        }
        
        # ၄။ API ထံ လှမ်းပို့ခြင်း
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

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("🧹 Cleaning old bot connections...")
    bot.remove_webhook()
    time.sleep(2)
    
    print("🤖 Undress AI Video Bot Active with Telegra.ph Bypass...")
    bot.infinity_polling()
