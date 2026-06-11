import os
import sys
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# =====================================================================
# 🛠️ RENDER PORT BINDING ERROR အတွက် FLASK SERVER တည်ဆောက်ခြင်း
# =====================================================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_flask():
    # Render က ပေးမည့် Port (သို့မဟုတ်) ပုံမှန် 8000 ပေါ်တွင် ပတ်မည်
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

# =====================================================================
# Telegram Bot Token နှင့် ယာယီ Session မှတ်သားရန် နေရာ
# =====================================================================
TOKEN = "8702294693:AAHzhhFSuogotRM4US1SSlnb2sogss6FUPA"
user_photos = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "🎭 **AI Face Swap Bot မှ ကြိုဆိုပါတယ်** 🎭\n\n"
        "ဓာတ်ပုံတစ်ပုံထဲက မျက်နှာကို နောက်ဓာတ်ပုံတစ်ပုံရဲ့ ကိုယ်ထည်ပေါ်သို့ AI သုံးပြီး အစားထိုးပေးမည့် စနစ်ဖြစ်ပါသည်။\n\n"
        "📸 **အသုံးပြုနည်းလမ်းညွှန်-**\n"
        "၁။ ပထမဦးစွာ **မျက်နှာယူမည့်သူ၏ ဓာတ်ပုံ (Source Face)** ကို ပို့ပေးပါ။\n"
        "၂။ ပြီးနောက် သွားရောက်ထည့်သွင်းမည့် **နောက်ခံခန္ဓာကိုယ် ဓာတ်ပုံ (Target Body)** ကို ဒုတိယပုံအနေဖြင့် ပို့ပေးရပါမည်။"
    )
    await update.message.reply_text(text=welcome_text, parse_mode="Markdown")

async def handle_face_swap(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    photo_file = await update.message.photo[-1].get_file()
    telegram_image_url = photo_file.file_path

    # ပထမပုံ ဝင်လာခြင်း
    if user_id not in user_photos:
        user_photos[user_id] = {
            "source_url": telegram_image_url
        }
        await update.message.reply_text(
            "✅ **ပထမပုံ (မျက်နှာ) ကို မှတ်သားပြီးပါပြီ။**\n\n"
            "ယခု အဆိုပါမျက်နှာကို သွားထည့်မည့် **ဒုတိယပုံ (Target Body Image)** ကို ပို့ပေးပါဗျာ။"
        )
        return

    # ဒုတိယပုံ ဝင်လာခြင်း
    source_url = user_photos[user_id]["source_url"]
    target_url = telegram_image_url
    del user_photos[user_id] # Session ဖျက်ရန်

    status_msg = await update.message.reply_text("⏳ AI က မျက်နှာချင်း အစားထိုးလဲလှယ်ပေးနေပါပြီ။ ခဏစောင့်ပေးပါ...")

    API_URL = "https://face-swap-video-image-multiface.p.rapidapi.com/runsync"
    headers = {
        'Content-Type': 'application/json',
        'x-rapidapi-host': 'face-swap-video-image-multiface.p.rapidapi.com',
        'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
    }

    payload = {
        "input": {
            "enhanceState": True,
            "mode": "swap-face",
            "url": source_url,
            "targetUrl": target_url
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            swapped_photo_url = result.get("output_url") or result.get("image") or result.get("url") or result.get("result")
            
            if not swapped_photo_url and "data" in result and isinstance(result["data"], dict):
                swapped_photo_url = result["data"].get("url") or result["data"].get("image")
            
            if not swapped_photo_url and isinstance(result.get("output"), list):
                swapped_photo_url = result["output"][0]

            if swapped_photo_url:
                await status_msg.delete()
                await update.message.reply_photo(
                    photo=swapped_photo_url, 
                    caption="🎭 **AI Face Swap ဖြင့် မျက်နှာလဲလှယ်ခြင်း အောင်မြင်ပါသည်!** 🎭", 
                    parse_mode="Markdown"
                )
            else:
                await status_msg.edit_text(f"⚠️ မျက်နှာလဲထားသည့် ပုံထွက်မလာပါ။\nAPI Response: {str(result)}")
        else:
            await status_msg.edit_text(f"❌ API Error တက်သွားသည်။ Code: {response.status_code}\nအသေးစိတ်: {response.text}")
            
    except Exception as e:
        await status_msg.edit_text(f"❌ ဆာဗာချက်ဆက်မှု အဆင်မပြေပါ- {str(e)}")

def main() -> None:
    # 🔄 ၁။ Background Thread အနေဖြင့် Flask Web Server ကို အရင်ပတ်ထားခြင်း (Render Port ကြောင့်ဖြစ်သည်)
    threading.Thread(target=run_flask, daemon=True).start()

    # 🤖 ၂။ Telegram Bot အား စတင် Run ခြင်း
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_face_swap))

    print("AI Face Swap Bot with Web Port Running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
