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

# Render အတွက် Port အတု
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

# ၂။ DuckDuckGo AI Function (Syntax အသစ်)
def get_ai_response(user_text):
    try:
        # Version 7.x မှာ chat function ကို ဒီလို ခေါ်ရပါတယ်
        with DDGS() as ddgs:
            # model ကို 'gpt-4o-mini' သို့မဟုတ် 'llama-3-70b' သုံးနိုင်ပါတယ်
            response = ddgs.chat(user_text, model='gpt-4o-mini')
            return response
    except Exception as e:
        # အပေါ်ကနည်းနဲ့ မရရင် နောက်တစ်နည်း (Older way fallback)
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = ddgs.chat(user_text)
                return results
        except Exception as e2:
            return f"Error: {str(e2)}"

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
    
    # မောင့်ရဲ့ Bot Token
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI' 
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is starting with DDGS v7+ Support...")
    app.run_polling(drop_pending_updates=True)
