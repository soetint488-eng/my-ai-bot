import os
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import telebot
import requests

# Config parameters
BASE_URL = "https://a1-sgp.easecdn.com/1102190223222824/lit"
BOT_TOKEN = "8702294693:AAFQUh4aT3Wh5ur4XFxO5ftB_evXD_5MrFM"
YOUR_TELEGRAM_CHAT_ID = 8584422107

current_token = None

# Telebot Client initialization
bot = telebot.TeleBot(BOT_TOKEN)

# Dummy Server for Render Platform Compatibility
class DummyWebService(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"LitAtom Bridge Bot is running alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyWebService)
    print(f"🌍 Dummy Web Server started on port {port}")
    server.serve_forever()

def get_easemob_token():
    url = f"{BASE_URL}/token"
    # သင့်ရဲ့ Username နဲ့ Password ကို Payload ထဲမှာ တိုက်ရိုက် ထည့်သွင်းပေးထားပါသည်
    payload = {
        "grant_type": "password",
        "username": "love143872087742769",
        "password": "c9bc87f4b03dcda196e0914af18f3fac"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Easemob-SDK(Android) 4.5.3"
    }
    try:
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception as e:
        print(f"Token Error: {e}")
    return None

def check_new_messages(token):
    url = f"{BASE_URL}/users/love143872087742769/offline_messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Easemob-SDK(Android) 4.5.3"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("entities", [])
        elif response.status_code == 401:
            return "EXPIRED"
    except Exception as e:
        print(f"Check Message Error: {e}")
    return []

def message_listener_loop():
    global current_token
    print("🚀 LitAtom App Chat Listener စတင်ပါပြီ...")
    
    current_token = get_easemob_token()
    
    while True:
        if not current_token:
            current_token = get_easemob_token()
            time.sleep(5)
            continue
            
        messages = check_new_messages(current_token)
        
        if messages == "EXPIRED":
            print("🔑 Token သက်တမ်းကုန်သွားသဖြင့် အသစ်ပြန်ယူနေပါသည်...")
            current_token = get_easemob_token()
            time.sleep(2)
            continue
            
        if messages:
            for msg in messages:
                sender = msg.get("from", "Unknown User")
                msg_body = msg.get("payload", {}).get("bodies", [{}])[0]
                
                if msg_body.get("type") == "txt":
                    chat_text = msg_body.get("msg", "")
                    
                    alert_message = (
                        f"📩 **LitAtom အက်ပ်ထဲမှ စာအသစ်ရောက်လာပါသည်**\n\n"
                        f"👤 **From ID:** `{sender}`\n"
                        f"💬 **Message:** {chat_text}"
                    )
                    
                    try:
                        bot.send_message(chat_id=YOUR_TELEGRAM_CHAT_ID, text=alert_message, parse_mode="Markdown")
                    except Exception as e:
                        print(f"Telegram Send Error: {e}")
                        
        time.sleep(3)

if __name__ == "__main__":
    # 1. Start Render Web Service port binding
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    # 2. Start checking for background offline messages
    threading.Thread(target=message_listener_loop, daemon=True).start()
    
    print("🤖 Telegram Bot အောင်မြင်စွာ ပွင့်သွားပါပြီ။")
    
    # 3. Maintain bot execution via polling
    bot.infinity_polling()
