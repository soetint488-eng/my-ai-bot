import requests
import urllib.parse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import threading
import http.server
import socketserver

# --- Render Port Error ကျော်ရန် (Dummy Server) ---
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

# Port scan error မတက်အောင် server ကို background မှာ run ထားမယ်
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- Bot ရဲ့ အချက်အလက်များ ---
TOKEN = "8428992244:AAErRzANg_HUlKnJkI-MclY9T_uV0B-p2O0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ အစ်ကို! ကျွန်တော်က AI Bot ပါ။ ကြိုက်တာမေးလို့ရသလို၊ App တွေလည်း ထုတ်ခိုင်းလို့ရပါတယ်ခင်ဗျာ။")

async def chat_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    status_msg = await update.message.reply_text("⏳ ခဏလေး စဉ်းစားနေပါတယ်...")
    
    try:
        # AI API ကို ခေါ်ယူခြင်း
        encoded_text = urllib.parse.quote(user_text)
        url = f"https://sandipbaruwal.onrender.com/gemini?prompt={encoded_text}"
        response = requests.get(url)
        result = response.json()
        ai_reply = result.get("answer", "တောင်းပန်ပါတယ်၊ နားမလည်လို့ ထပ်မေးပေးပါဦး။")

        # Logic: အကယ်၍ HTML ကုဒ်တွေ ပါလာရင် ဖိုင်အနေနဲ့ ပို့ပေးမယ်
        if "```html" in ai_reply or "<!DOCTYPE html>" in ai_reply:
            await status_msg.edit_text("✅ App ကုဒ်တွေ ရပါပြီ၊ ဖိုင်ထုတ်ပေးနေပါတယ်...")
            
            file_name = "your_app.html"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(ai_reply)
            
            with open(file_name, "rb") as f:
                await update.message.reply_document(document=f, filename=file_name, caption="အစ်ကို ခိုင်းထားတဲ့ App လေး ရပါပြီဗျာ!")
        
        # သာမန် စကားပြောဆိုရင် စာသားပဲ ပြန်ဖြေမယ်
        else:
            await status_msg.edit_text(ai_reply)

    except Exception as e:
        await status_msg.edit_text("တောင်းပန်ပါတယ်၊ AI ဘက်မှာ အမှားတစ်ခု ရှိနေလို့ပါ။ နောက်မှ ပြန်စမ်းကြည့်ပါနော်။")

def main():
    # Bot ကို စတင်ခြင်း
    app = Application.builder().token(TOKEN).build()
    
    # Handler များ ထည့်သွင်းခြင်း
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_ai))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
