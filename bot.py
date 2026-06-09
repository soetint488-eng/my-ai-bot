import telebot
import requests
import time
import os
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==================== [ CONFIGURATIONS ] ====================
BOT_TOKEN = "8702294693:AAHff0iYwzElcLNZzPhlXodImHePQuzYDl0"

# အစ်ကိုပေးထားသော cURL အချက်အလက်များအတိုင်း ထည့်သွင်းထားပါသည်
RAPIDAPI_URL = "https://cheapest-gpt-4-turbo-gpt-4-vision-chatgpt-openai-ai-api.p.rapidapi.com/v1/chat/completions"
RAPIDAPI_HOST = "cheapest-gpt-4-turbo-gpt-4-vision-chatgpt-openai-ai-api.p.rapidapi.com"
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"
# ============================================================

bot = telebot.TeleBot(BOT_TOKEN, num_threads=1)

# --- Render ရဲ့ Timed Out / Port Error ကို ကျော်ရန် Fake Web Server ---
class HealthCheckServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"AI Chatbot is Running Alive!")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckServer)
    print(f"🌍 Fake Web Server started on port {port}")
    server.serve_forever()

# --- Telegram Bot ရဲ့ လုပ်ဆောင်ချက်များ ---
@bot.message_handler(commands=['start', 'help'])
def start_cmd(message):
    welcome_text = (
        "🤖 **GPT-4o AI Chatbot မှ ကြိုဆိုပါတယ်ဗျာ** ✨\n\n"
        "ကျွန်တော့်ဆီကို သိလိုသမျှ မေးခွန်းတွေကို မြန်မာလိုဖြစ်စေ၊ အင်္ဂလိပ်လိုဖြစ်စေ "
        "အေးဆေး ရိုက်နှိပ်မေးမြန်းနိုင်ပါတယ်ဗျာ။"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    # User ပို့လိုက်တဲ့ မေးခွန်းကို ရယူခြင်း
    user_query = message.text
    
    # ⏳ စဉ်းစားနေဆဲ... Status ပြခြင်း
    status_msg = bot.reply_to(message, "⏳ AI က စဉ်းစားနေပါပြီ... ခေတ္တစောင့်ပါဗျာ။")
    
    try:
        # API သို့ ပို့မည့် JSON Header
        headers = {
            "Content-Type": "application/json",
            "x-rapidapi-host": RAPIDAPI_HOST,
            "x-rapidapi-key": RAPIDAPI_KEY
        }
        
        # အစ်ကိုပေးထားသော JSON Body ပုံစံအတိုင်း User ရိုက်လိုက်တဲ့စာကို ထည့်သွင်းခြင်း
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": user_query
                }
            ],
            "model": "gpt-4o",      # GPT-4o Model ကို အသုံးပြုထားပါသည်
            "max_tokens": 500,       # စာသားရှည်ရှည်ပြန်ဖြေနိုင်ရန် 500 ထားလိုက်ပါသည်
            "temperature": 0.7       # ပိုမိုသဘာဝကျကျ ဖြေဆိုနိုင်ရန် တန်ဖိုးညှိထားပါသည်
        }
        
        # API ထံသို့ လှမ်းပို့ခြင်း
        response = requests.post(RAPIDAPI_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # OpenAI Standard Format အတိုင်း AI ပြန်ဖြေတဲ့ စာသားကို ဆွဲထုတ်ခြင်း
            ai_reply = result['choices'][0]['message']['content']
            
            # စဉ်းစားနေပါသည် ဆိုတဲ့စာကို ဖျက်ပြီး AI အဖြေကို ပြန်ပို့ခြင်း
            bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
            bot.reply_to(message, ai_reply)
            
        elif response.status_code == 429:
            bot.edit_message_text(
                "⚠️ **ဤ API Key ၏ တစ်လစာ အခမဲ့ စမ်းသပ်မှု Quota ပြည့်သွားပါပြီဗျာ။**",
                chat_id=message.chat.id,
                message_id=status_msg.message_id
            )
        else:
            bot.edit_message_text(
                f"❌ API Error ဖြစ်သွားပါပြီ။\nStatus Code: {response.status_code}\nMessage: {response.text[:200]}",
                chat_id=message.chat.id,
                message_id=status_msg.message_id
            )
            
    except Exception as e:
        bot.edit_message_text(f"❌ Error ဖြစ်ပွားသွားသည် - {str(e)}", chat_id=message.chat.id, message_id=status_msg.message_id)

if __name__ == "__main__":
    # Fake Web Server ကို Thread ဖြင့် မောင်းနှင်ခြင်း
    server_thread = Thread(target=run_health_server)
    server_thread.daemon = True
    server_thread.start()

    # ရှင်းလင်းရေး လုပ်ဆောင်ခြင်း
    print("🧹 Cleaning old bot connections...")
    bot.remove_webhook()
    time.sleep(2)
    
    print("🤖 AI Chatbot စတင်ပွင့်နေပါပြီ...")
    bot.infinity_polling()
