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

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- Bot Token အသစ် ---
TOKEN = "8428992244:AAERrZANg_HUlKnJkDhcFRK0tVSdqvQDwV8"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ အစ်ကို! အခု Bot က အသစ်စက်စက် Token နဲ့ အလုပ်လုပ်နေပါပြီ။ ကြိုက်တာမေးလို့ရပါပြီခင်ဗျာ။")

async def chat_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    status_msg = await update.message.reply_text("⏳ ခဏလေး စဉ်းစားနေပါတယ်...")
    
    try:
        encoded_text = urllib.parse.quote(user_text)
        url = f"https://sandipbaruwal.onrender.com/gemini?prompt={encoded_text}"
        response = requests.get(url)
        result = response.json()
        ai_reply = result.get("answer", "တောင်းပန်ပါတယ်၊ နားမလည်လို့ ထပ်မေးပေးပါဦး။")

        if "```html" in ai_reply or "<!DOCTYPE html>" in ai_reply:
            await status_msg.edit_text("✅ App ကုဒ်တွေ ရပါပြီ၊ ဖိုင်ထုတ်ပေးနေပါတယ်...")
            file_name = "your_app.html"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(ai_reply)
            with open(file_name, "rb") as f:
                await update.message.reply_document(document=f, filename=file_name, caption="အစ်ကို ခိုင်းထားတဲ့ App လေး ရပါပြီဗျာ!")
        else:
            await status_msg.edit_text(ai_reply)

    except Exception as e:
        await status_msg.edit_text("AI ဘက်မှာ အမှားတစ်ခု ရှိနေလို့ပါ။ ခဏနေမှ ပြန်စမ်းကြည့်ပါနော်။")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_ai))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
