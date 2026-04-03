import logging
import os
import http.server
import socketserver
import threading
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# ၁။ Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Render Port Fix
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

# ၂။ Pollinations AI Function (DuckDuckGo အစားထိုး)
def get_ai_response(user_text):
    try:
        # Pollinations AI က API Key မလိုဘဲ အခမဲ့ သုံးလို့ရပါတယ်
        prompt = requests.utils.quote(user_text)
        url = f"https://text.pollinations.ai/{prompt}?model=openai&system=မင်းကအမြဲတမ်းမြန်မာလိုပဲဖြေပေးရမယ်"
        
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return "ခဏလေးနော် မောင်... AI ဘက်က အလုပ်မလုပ်လို့ပါ။"
    except Exception as e:
        return f"Error: {str(e)}"

# ၃။ Message Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_input = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    ai_reply = get_ai_response(user_input)
    await update.message.reply_text(ai_reply)

# ၄။ Main
if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI' 
    
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Bot is starting with Pollinations AI...")
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"Start Error: {e}")
