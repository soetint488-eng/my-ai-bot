import telebot
import requests
import time
import os
import base64
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from telebot import types

# ==================== [ CONFIGURATIONS ] ====================
BOT_TOKEN = "8702294693:AAHff0iYwzElcLNZzPhlXodImHePQuzYDl0"

RAPIDAPI_URL = "https://undress-strip-person.p.rapidapi.com/UndressImage"
RAPIDAPI_HOST = "undress-strip-person.p.rapidapi.com"
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"
# ============================================================

bot = telebot.TeleBot(BOT_TOKEN, num_threads=1)

# --- Render ရဲ့ Timed Out / Port Error ကို ကျော်ရန် Fake Web Server ---
class HealthCheckServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is Running Alive!")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckServer)
    print(f"🌍 Fake Web Server started on port {port}")
    server.serve_forever()

# --- Telegram Bot ရဲ့ လုပ်ဆောင်ချက်များ ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_text = (
        "🤖 **Undress AI Bot မှ ကြိုဆိုပါတယ်**\n\n"
        "ကျွန်တော့်ဆီကို ပြုပြင်လိုတဲ့ ဓာတ်ပုံတစ်ပုံ ပို့ပေးလိုက်ပါဗျာ။"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    status_msg = bot.reply_to(message, "⏳ ဓာတ်ပုံဒေတာကို ရယူနေပါပြီ... ခေတ္တစောင့်ပါဗျာ။")
    
    try:
        # ၁။ Telegram Server မှ ဓာတ်ပုံဖိုင်ကို ဒေါင်းလုဒ်ဆွဲခြင်း
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        bot.edit_message_text("🪄 AI စနစ်ဖြင့် ပုံကို ပြုပြင်နေပါပြီ... (စက္ကန့်အနည်းငယ် ကြာနိုင်ပါသည်)", chat_id=message.chat.id, message_id=status_msg.message_id)
        
        # ၂။ ဓာတ်ပုံဖိုင်ကို Base64 String သို့ ပြောင်းလဲခြင်း
        base64_image = base64.b64encode(downloaded_file).decode('utf-8')
        
        # ၃။ API သို့ ပို့ရန် အချက်အလက်များ ပြင်ဆင်ခြင်း
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "x-rapidapi-host": RAPIDAPI_HOST,
            "x-rapidapi-key": RAPIDAPI_KEY
        }
        
        # image parameter ထဲသို့ base64 string ကို ထည့်သွင်းခြင်း
        payload = {
            "image": base64_image
        }
        
        # ၄။ API ထံ POST Request ဖြင့် ပို့ခြင်း
        response = requests.post(RAPIDAPI_URL, headers=headers, data=payload)

        if response.status_code == 200:
            result = response.json()
            
            # API မှ ပြန်ပေးလေ့ရှိသော key နာမည်များအတိုင်း ရှာဖွေခြင်း
            ai_img_url = result.get("url") or result.get("image_url") or result.get("data", {}).get("url") or result.get("output")
            
            if ai_img_url:
                bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
                bot.send_photo(
                    chat_id=message.chat.id, 
                    photo=ai_img_url, 
                    caption="✨ **AI ပြုပြင်ပြီးသားပုံ ရပါပြီဗျာ။**", 
                    reply_to_message_id=message.message_id
                )
            else:
                bot.edit_message_text(f"⚠️ API အလုပ်လုပ်သော်လည်း ပုံလင့်ခ် ရှာမတွေ့ပါ။\n**Response:** `{response.text[:300]}`", chat_id=message.chat.id, message_id=status_msg.message_id)
        else:
            bot.edit_message_text(f"❌ API Error ဖြစ်သွားပါပြီ။\nStatus Code: {response.status_code}\nMessage: {response.text}", chat_id=message.chat.id, message_id=status_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ Error ဖြစ်ပွားသွားသည် - {str(e)}", chat_id=message.chat.id, message_id=status_msg.message_id)

if __name__ == "__main__":
    # Fake Web Server မောင်းနှင်ခြင်း
    server_thread = Thread(target=run_health_server)
    server_thread.daemon = True
    server_thread.start()

    # ရှင်းလင်းရေး လုပ်ဆောင်ခြင်း
    print("🧹 Cleaning old bot connections...")
    bot.remove_webhook()
    time.sleep(2)
    
    print("🤖 Undress AI Bot စတင်ပွင့်နေပါပြီ...")
    bot.infinity_polling()
