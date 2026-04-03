import logging
import os
import http.server
import socketserver
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from duckduckgo_search import DDGS

# ၁။ Logging သတ်မှတ်ချက် (Bot အလုပ်လုပ်ပုံ စစ်ဆေးရန်)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ၂။ Render အတွက် Port အတု ဖွင့်ပေးမည့် Function
# ဒါမှ Render က Port မတွေ့ဘူးဆိုပြီး Error မပြတော့မှာပါ
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    # Port ကို အမြဲ နားထောင်နေအောင် လုပ်ပေးထားတယ်
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Server started on port {port}")
        httpd.serve_forever()

# ၃။ DuckDuckGo AI ဆီက အဖြေတောင်းတဲ့ Function
def get_ai_response(user_text):
    try:
        with DDGS() as ddgs:
            # model 'gpt-4o-mini' ကို သုံးထားပါတယ်
            response = ddgs.chat(user_text, model='gpt-4o-mini')
            return response
    except Exception as e:
        return "ခဏလေးနော် မောင်... DuckDuckGo ဘက်က အလုပ်မလုပ်လို့ပါ။ ခဏနေမှ ပြန်မေးကြည့်ပါ။"

# ၄။ User ဆီက စာရောက်လာရင် တုံ့ပြန်မယ့် Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_input = update.message.text
    
    # Bot က စဉ်းစားနေကြောင်း 'typing...' ပြပေးမယ်
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # AI ဆီက အဖြေယူမယ်
    ai_reply = get_ai_response(user_input)
    
    # User ဆီ အဖြေပြန်ပို့မယ်
    await update.message.reply_text(ai_reply)

# ၅။ Main Function (Bot စတင်နှိုးဆော်ခြင်း)
if __name__ == '__main__':
    # Render ရဲ့ Port Error ကို ကျော်ဖို့ Server ကို သီးသန့် Thread နဲ့ Run မယ်
    threading.Thread(target=run_dummy_server, daemon=True).start()

    # မောင့်ရဲ့ Bot Token
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI' 
    
    try:
        # Telegram Bot Application တည်ဆောက်မယ်
        app = ApplicationBuilder().token(TOKEN).build()
        
        # စာသား Message တွေအတွက် Handler ထည့်မယ်
        message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
        app.add_handler(message_handler)
        
        print("--- DuckDuckGo AI Bot is running with Port Fix ---")
        
        # Bot ကို စတင် Run မယ်
        # drop_pending_updates=True က Bot ပိတ်ထားတုန်းက စာတွေကို အကုန်ကျော်သွားဖို့ပါ
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"Bot Error: {e}")
