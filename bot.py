import logging
import os
import http.server
import socketserver
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from duckduckgo_search import DDGS

# ၁။ Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Render Port Fix
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

# ၂။ DuckDuckGo AI Function (Version 6.3.2 Syntax)
def get_ai_response(user_text):
    try:
        # Version 6.3.2 မှာ DDGS().chat() က အလုပ်လုပ်ပါတယ်
        with DDGS() as ddgs:
            response = ddgs.chat(user_text, model='gpt-4o-mini')
            return response
    except Exception as e:
        # အကယ်၍ Error တက်နေသေးရင် နောက်တစ်နည်းနဲ့ စမ်းမယ်
        return f"ခဏလေးနော် မောင်... Error တက်နေလို့ပါ။ (Error: {str(e)})"

# ၃။ Message Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_input = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    ai_reply = get_ai_response(user_input)
    await update.message.reply_text(ai_reply)

# ၄။ Main
if __name__ == '__main__':
    # Port Server ကို အရင်နှိုးမယ်
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    # မောင့်ရဲ့ Bot Token
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI' 
    
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Bot is starting with DDGS Fixed Version...")
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"Start Error: {e}")
