import os
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests

# Config parameters
BASE_URL = "https://a1-sgp.easecdn.com/1102190223222824/lit"
BOT_TOKEN = "8702294693:AAFQUh4aT3Wh5ur4XFxO5ftB_evXD_5MrFM"
YOUR_TELEGRAM_CHAT_ID = 8584422107

current_token = None

# စကားပြောဖူးသူများနှင့် ၎င်းတို့၏ စာများကို သိမ်းဆည်းရန် Memory Database
# { "sender_id": ["msg1", "msg2"] } ပုံစံဖြင့် သိမ်းမည်
chat_history = {}

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
    
    try:
        bot.send_message(chat_id=YOUR_TELEGRAM_CHAT_ID, text="🤖 Bot စတင်ပွင့်ပါပြီ။ စကားပြောဖူးသူများကို ကြည့်ရန် /users ဟု ရိုက်နှိပ်ပါ။")
    except Exception as e:
        print(f"Telegram Initial Send Error: {e}")

    while True:
        if not current_token:
            current_token = get_easemob_token()
            time.sleep(5)
            continue
            
        messages = check_new_messages(current_token)
        
        if messages == "EXPIRED":
            current_token = get_easemob_token()
            time.sleep(2)
            continue
            
        if isinstance(messages, list) and messages:
            for msg in messages:
                sender = msg.get("from", "Unknown User")
                
                payload = msg.get("payload", {})
                bodies = payload.get("bodies", [{}])
                msg_body = bodies[0] if bodies else {}
                chat_text = msg_body.get("msg", "")
                
                if not chat_text:
                    chat_text = msg.get("msg", "Media/Unknown Message")

                # စကားပြောဖူးသူစာရင်းထဲ ထည့်ပြီး စာကိုပါ သိမ်းဆည်းခြင်း
                if sender not in chat_history:
                    chat_history[sender] = []
                chat_history[sender].append(chat_text)
                
                # Notification အသစ်တက်လာတိုင်းလည်း အသိပေးမည်
                alert_message = f"📩 **စာအသစ်ရောက်သည်**\n👤 `{sender}`: {chat_text}"
                try:
                    bot.send_message(chat_id=YOUR_TELEGRAM_CHAT_ID, text=alert_message)
                except Exception as e:
                    print(f"Telegram Send Error: {e}")
                        
        time.sleep(3)

# --- Telegram Bot Commands & Buttons Handling ---

# /users ရိုက်ရင် ပြပေးမယ့် Button စနစ်
@bot.message_handler(commands=['users'])
def send_users_buttons(message):
    if message.chat.id != YOUR_TELEGRAM_CHAT_ID:
        return

    if not chat_history:
        bot.reply_to(message, "📭 သင့်ထံ စာပို့ဖူးသည့် User မရှိသေးပါခင်ဗျာ။")
        return

    markup = InlineKeyboardMarkup()
    # စကားပြောဖူးသူ တစ်ယောက်ချင်းစီအတွက် Button တစ်ခုစီ ဆောက်ခြင်း
    for user_id in chat_history.keys():
        btn = InlineKeyboardButton(text=f"👤 {user_id}", callback_data=f"view_{user_id}")
        markup.add(btn)

    bot.send_message(message.chat.id, "👇 စကားပြောဖူးသူများစာရင်း ဖြစ်ပါသည်။ စာများဖတ်ရန် နာမည်ကို နှိပ်ပါ -", reply_markup=markup)

# Button နှိပ်လိုက်ရင် အလုပ်လုပ်မယ့် စနစ်
@bot.callback_query_handler(func=lambda call: call.data.startswith('view_'))
def view_user_chat(call):
    user_id = call.data.split('_')[1]
    
    if user_id in chat_history and chat_history[user_id]:
        all_msgs = "\n".join([f"- {m}" for m in chat_history[user_id]])
        response_text = f"💬 **User `{user_id}` မှ ပေးပို့ထားသော စာများ:**\n\n{all_msgs}"
    else:
        response_text = f"📭 User `{user_id}` ထံမှ စာမှတ်တမ်း မရှိသေးပါ။"

    bot.send_message(call.message.chat.id, response_text)
    bot.answer_callback_query(call.id) # Button loading ပျောက်အောင် လုပ်ခြင်း

if __name__ == "__main__":
    threading.Thread(target=run_dummy_server, daemon=True).start()
    threading.Thread(target=message_listener_loop, daemon=True).start()
    print("🤖 Telegram Bot အောင်မြင်စွာ ပွင့်သွားပါပြီ။")
    bot.infinity_polling()
