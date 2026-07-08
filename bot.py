import os
import time
import asyncio
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client

# Config များ
BASE_URL = "https://a1-sgp.easecdn.com/1102190223222824/lit"
MY_USERNAME = "love143872087742769"
MY_PASSWORD_HASH = "c9bc87f4b03dcda196e0914af18f3fac"

BOT_TOKEN = "8702294693:AAFQUh4aT3Wh5ur4XFxO5ftB_evXD_5MrFM"
YOUR_TELEGRAM_CHAT_ID = 8584422107  # သင့်ရဲ့ Chat ID ထည့်သွင်းပေးထားပြီးသားဖြစ်သည်

current_token = None

# Render Free Web Service အတွက် Dummy Web Server ပြင်ဆင်ခြင်း
class DummyWebService(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"LitAtom Bridge Bot is running alive!")

def run_dummy_server():
    # Render က သတ်မှတ်ပေးမယ့် Port (သို့မဟုတ် Default 10000) ကို သုံးပြီး Port ဖွင့်ပေးခြင်း
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyWebService)
    print(f"🌍 Dummy Web Server started on port {port}")
    server.serve_forever()

def get_easemob_token():
    """Easemob ဆီကနေ Token တောင်းယူခြင်း"""
    url = f"{BASE_URL}/token"
    payload = {
        "grant_type": "password",
        "username": MY_USERNAME,
        "password": MY_PASSWORD_HASH
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
    """မဖတ်ရသေးသော စာအသစ်များကို လှမ်းစစ်ခြင်း"""
    url = f"{BASE_URL}/users/{MY_USERNAME}/offline_messages"
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

async def message_listener_loop(bot_client):
    """Background ကနေ စာအသစ်တွေကို ပတ်စစ်မယ့် ပတ်လမ်း (Loop)"""
    global current_token
    print("🚀 LitAtom App Chat Listener စတင်ပါပြီ...")
    
    current_token = get_easemob_token()
    
    while True:
        if not current_token:
            current_token = get_easemob_token()
            await asyncio.sleep(5)
            continue
            
        messages = check_new_messages(current_token)
        
        if messages == "EXPIRED":
            print("🔑 Token သက်တမ်းကုန်သွားသဖြင့် အသစ်ပြန်ယူနေပါသည်...")
            current_token = get_easemob_token()
            await asyncio.sleep(2)
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
                        await bot_client.send_message(chat_id=YOUR_TELEGRAM_CHAT_ID, text=alert_message)
                    except Exception as e:
                        print(f"Telegram Send Error: {e}")
                        
        # ၃ စက္ကန့်လျှင် တစ်ကြိမ် စစ်ဆေးရန်
        await asyncio.sleep(3)

# Pyrogram Client Configuration
bot = Client(
    "litatom_bridge_bot",
    api_id=2040, 
    api_hash="b18441a1d03e752e05a87c7e0932ad8e",
    bot_token=BOT_TOKEN
)

async def main():
    await bot.start()
    
    # Render အတွက် Dummy Web Port ဖွင့်လှစ်ပေးခြင်း (Exit Status 1 မဖြစ်စေရန်)
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    # စာစစ်မယ့် လုပ်ငန်းစဉ်ကို Background မှာ စတင်ခြင်း
    asyncio.create_task(message_listener_loop(bot))
    print("🤖 Telegram Bot အောင်မြင်စွာ ပွင့်သွားပါပြီ။")
    await asyncio.Event().wait()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
