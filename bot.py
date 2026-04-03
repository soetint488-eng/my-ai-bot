import logging
import os
import http.server
import socketserver
import threading
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# ၁။ Logging သတ်မှတ်ချက်
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ၂။ Render Port Error မတက်အောင် Port အတု ဖွင့်ပေးခြင်း
def run_dummy_server():
    # Render က ပေးတဲ့ PORT (သို့မဟုတ်) 8080 ကို သုံးမယ်
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    
    # Port ကို အမြဲ နားထောင်နေအောင် လုပ်ပေးထားတယ်
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            logging.info(f"Dummy Server running on port {port}")
            httpd.serve_forever()
    except Exception as e:
        logging.error(f"Server Error: {e}")

# ၃။ AI ဆီက အဖြေတောင်းတဲ့ Function
def get_ai_response(user_text):
    try:
        # Prompt ထဲမှာ မြန်မာလိုပဲ ပြန်ဖြေခိုင်းထားတယ်
        encoded_text = requests.utils.quote(user_text)
        url = f"https://text.pollinations.ai/{encoded_text}?model=openai&system=You are a helpful assistant. Always reply in Myanmar language."
        
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.text
        else:
            return "ခဏလေးနော် မောင်... AI ဘက်က အလုပ်မလုပ်လို့ပါ။"
    except Exception as e:
        return f"Error: {str(e)}"

# ၄။ စာဝင်လာရင် တုံ့ပြန်မယ့် Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: 
        return
        
    user_input = update.message.text
    
    # Bot က စဉ်းစားနေတဲ့ 'typing...' ပုံစံပြမယ်
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # AI အဖြေယူမယ်
    ai_reply = get_ai_response(user_input)
    
    # User ဆီ အဖြေပြန်ပို့မယ်
    await update.message.reply_text(ai_reply)

# ၅။ Bot စတင်နှိုးဆော်ခြင်း
if __name__ == '__main__':
    # Render ရဲ့ Port Scan ကို ကျော်ဖို့ Background Thread နဲ့ Run မယ်
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    # မောင့်ရဲ့ Bot Token
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI' 
    
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        
        # Message Handler ထည့်သွင်းခြင်း
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        logging.info("--- Bot is starting with Pollinations AI ---")
        
        # Render ပေါ်မှာ အဆင်ပြေအောင် stop_signals=None ထည့်ထားတယ်
        app.run_polling(drop_pending_updates=True, stop_signals=None)
        
    except Exception as e:
        logging.error(f"Start Error: {e}")
