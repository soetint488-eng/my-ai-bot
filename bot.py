import logging
import os
import http.server
import socketserver
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from duckduckgo_search import DDGS

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

def get_ai_response(user_text):
    # နည်းလမ်း (၁) နဲ့ အရင်စမ်းမယ်
    try:
        with DDGS() as ddgs:
            return ddgs.chat(user_text, model='gpt-4o-mini')
    except:
        # နည်းလမ်း (၁) မရရင် နည်းလမ်း (၂) နဲ့ ထပ်စမ်းမယ်
        try:
            with DDGS() as ddgs:
                # model ပြောင်းစမ်းကြည့်တာပါ
                return ddgs.chat(user_text, model='llama-3.1-70b')
        except Exception as e:
            return f"Error: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_input = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    ai_reply = get_ai_response(user_input)
    await update.message.reply_text(ai_reply)

if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    # မောင့်ရဲ့ နောက်ဆုံး Token ကို ဒီမှာထည့်ပါ
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI' 
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is starting...")
    app.run_polling(drop_pending_updates=True)
