import requests
import urllib.parse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

TOKEN = "8428992244:AAErRzANg_HUlKnJkI-MclY9T_uV0B-p2O0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ! ကျွန်တော်က AI Bot ပါ။ ကြိုက်တာမေးလို့ရသလို၊ App တွေလည်း ထုတ်ခိုင်းလို့ရပါတယ်ခင်ဗျာ။")

async def chat_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    status_msg = await update.message.reply_text("⏳ စဉ်းစားနေပါတယ် ခဏလေးနော်...")
    
    try:
        # AI API ကို ခေါ်ယူခြင်း
        encoded_text = urllib.parse.quote(user_text)
        url = f"https://sandipbaruwal.onrender.com/gemini?prompt={encoded_text}"
        response = requests.get(url)
        result = response.json()
        ai_reply = result.get("answer", "")

        # Logic 1: အကယ်၍ ကုဒ်တွေ (HTML) ပါလာရင် ဖိုင်အနေနဲ့ ပို့ပေးမယ်
        if "```html" in ai_reply or "<!DOCTYPE html>" in ai_reply:
            await status_msg.edit_text("✅ App ကုဒ်တွေ ရပါပြီ၊ ဖိုင်ထုတ်ပေးနေပါတယ်...")
            
            # HTML ကုဒ်ကို သီးသန့်ထုတ်ယူခြင်း
            file_content = ai_reply
            with open("app.html", "w", encoding="utf-8") as f:
                f.write(file_content)
            
            with open("app.html", "rb") as f:
                await update.message.reply_document(document=f, filename="your_app.html", caption="အစ်ကို ခိုင်းထားတဲ့ App လေး ရပါပြီဗျာ!")
        
        # Logic 2: သာမန် စကားပြောဆိုရင် စာသားပဲ ပြန်ဖြေမယ်
        else:
            await status_msg.edit_text(ai_reply)

    except Exception as e:
        await status_msg.edit_text("တောင်းပန်ပါတယ်၊ အခုချိန်မှာ AI ခဏ နားနေလို့ပါ။ နောက်မှ ပြန်မေးပေးပါနော်။")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_ai))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
