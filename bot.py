import requests
import urllib.parse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

# --- Settings ---
TOKEN = "8428992244:AAERrZANg_HUlKnJkDhcFRK0tVSdqvQDwV8"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ! Cloud ပေါ်ကနေ အလုပ်လုပ်နေပါပြီ။ လိုချင်တဲ့ App အကြောင်း ပြောပြပါ။")

async def generate_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    status_msg = await update.message.reply_text("⏳ AI က ကုဒ်တွေ ရေးနေပါပြီ...")

    try:
        encoded_prompt = urllib.parse.quote(f"Write a full single-file HTML/CSS/JS mobile app for: {user_prompt}. Use Burmese.")
        api_url = f"https://api.siputzx.my.id/api/ai/llama3?prompt={encoded_prompt}"
        
        response = requests.get(api_url, timeout=60)
        app_code = response.json().get("data") or response.json().get("result")

        if app_code:
            if "```html" in app_code:
                app_code = app_code.split("```html")[1].split("```")[0]
            elif "```" in app_code:
                 app_code = app_code.split("```")[1].split("```")[0]
            
            file_name = "index.html"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(app_code.strip())

            await update.message.reply_document(document=open(file_name, 'rb'), caption="✅ App ရပါပြီ!")
            await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_app))
    
    print("Bot is starting on Cloud...")
    app.run_polling()

if __name__ == '__main__':
    main()
