import requests
import urllib.parse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import threading
import http.server
import socketserver

# --- Render Port Binding ---
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- Bot Token ---
TOKEN = "8428992244:AAERrZANg_HUlKnJkDhcFRK0tVSdqvQDwV8"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ အစ်ကို! အခု AI က အဆင်သင့်ဖြစ်ပါပြီ။ ကြိုက်တာမေးလို့ရပါပြီခင်ဗျာ။")

async def chat_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    status_msg = await update.message.reply_text("⏳ ခဏလေး စဉ်းစားနေပါတယ်...")
    
    try:
        # ပိုစိတ်ချရတဲ့ AI API တစ်ခုကို ပြောင်းသုံးထားပါတယ်
        encoded_text = urllib.parse.quote(user_text)
        url = f"https://kaiz-api.vercel.app/api/gemini?question={encoded_text}"
        response = requests.get(url)
        result = response.json()
        
        # API ရဲ့ အဖြေကို ထုတ်ယူပုံ ပြောင်းလဲထားပါတယ်
        ai_reply = result.get("reply") or result.get("response") or result.get("answer") or "နားမလည်လို့ ထပ်မေးပေးပါဦး။"

        # App (HTML) ထုတ်ပေးမည့် Logic
        if "```html" in ai_reply or "<!DOCTYPE html>" in ai_reply:
            await status_msg.edit_text("✅ App ကုဒ်တွေ ရပါပြီ၊ ဖိုင်ထုတ်ပေးနေပါတယ်...")
            file_name = "your_app.html"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(ai_reply)
            with open(file_name, "rb") as f:
                await update.message.reply_document(document=f, filename=file_name, caption="အစ်ကို ခိုင်းထားတဲ့ App လေး ရပါပြီ!")
        else:
            await status_msg.edit_text(ai_reply)

    except Exception as e:
        await status_msg.edit_text("တောင်းပန်ပါတယ်၊ AI နဲ့ ချိတ်ဆက်လို့မရဖြစ်နေပါတယ်။ ခဏနေမှ ပြန်စမ်းကြည့်ပါနော်။")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_ai))
    app.run_polling()

if __name__ == "__main__":
    main()
