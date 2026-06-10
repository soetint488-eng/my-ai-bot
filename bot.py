import os
import sys
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Telegram Bot Token
TOKEN = "8702294693:AAHzhhFSuogotRM4US1SSlnb2sogss6FUPA"

# =====================================================================
# ၁။ /start ခေါ်လျှင် နှုတ်ခွန်းဆက်စကား ပြောခြင်း
# =====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "🎨 **AI Anime Filter Bot မှ ကြိုဆိုပါတယ်** 🎨\n\n"
        "သင့်ရဲ့ ရိုးရိုးဓာတ်ပုံတွေကို လှပတဲ့ ဂျပန် Anime စတိုင်လ်အဖြစ် ပြောင်းလဲပေးမည့် Bot ဖြစ်ပါတယ်။\n\n"
        "📸 **အသုံးပြုနည်း-**\n"
        "ကျွန်တော့်ဆီကို သင်ပြောင်းလဲချင်တဲ့ **ဓာတ်ပုံ (Photo)** တစ်ပုံ ပို့ပေးလိုက်ရုံပါပဲဗျာ။"
    )
    await update.message.reply_text(text=welcome_text, parse_mode="Markdown")

# =====================================================================
# ၂။ User ပို့လာသော ဓာတ်ပုံကို ဖမ်းယူပြီး Anime ပြောင်းပေးမည့်အပိုင်း
# =====================================================================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # User ပို့လိုက်တဲ့ ဓာတ်ပုံထဲက အကြည်ဆုံး Size ကို ယူခြင်း
    photo_file = await update.message.photo[-1].get_file()
    
    # Telegram ဆာဗာပေါ်က ဓာတ်ပုံရဲ့ Direct URL လင့်ခ်ကို လှမ်းယူခြင်း
    # (API က image_url တောင်းတာမို့ ဒီလင့်ခ်ကို တိုက်ရိုက် သုံးပါမည်)
    telegram_image_url = photo_file.file_path

    await update.message.reply_text("⏳ AI က သင့်ဓာတ်ပုံကို အန်နီမေးစတိုင်လ် ပြောင်းလဲနေပါပြီ။ ခဏစောင့်ပေးပါ...")

    # ပေးထားသော curl specification အတိုင်း တည်ဆောက်ခြင်း
    API_URL = "https://phototoanime1.p.rapidapi.com/cartoonize"
    
    headers = {
        'Content-Type': 'application/json',
        'x-rapidapi-host': 'phototoanime1.p.rapidapi.com',
        'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
    }

    # curl ထဲက --data အတိုင်း JSON Payload တည်ဆောက်ခြင်း
    payload = {
        "image_url": telegram_image_url, # Telegram က ရလာတဲ့ ပုံလင့်ခ်ကို ထည့်သွင်းခြင်း
        "style": "anime"                 # ပေးထားသည့်အတိုင်း anime style သုံးထားသည်
    }

    try:
        # POST Request ဖြင့် ဒေတာလှမ်းပို့ခြင်း
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # API မှ ပြန်ကျလာမည့် အသွင်ပြောင်းပြီးသား ပုံလင့်ခ်ကို ရှာဖွေခြင်း
            # API အလိုက် key နာမည် ကွဲပြားနိုင်သဖြင့် အတွေ့အများဆုံး key များကို စစ်ဆေးပါသည်
            anime_photo_url = result.get("anime_url") or result.get("image_url") or result.get("url") or result.get("output")
            
            # အကယ်၍ JSON ထဲမှာ တိုက်ရိုက်မပါဘဲ result['data']['url'] ပုံစံမျိုး ဖြစ်နေလျှင်
            if not anime_photo_url and "data" in result and isinstance(result["data"], dict):
                anime_photo_url = result["data"].get("url") or result["data"].get("image")

            if anime_photo_url:
                # ရလာတဲ့ Anime ပုံကို User ဆီ ဓာတ်ပုံအဖြစ် ပြန်ပို့ပေးခြင်း
                await update.message.reply_photo(
                    photo=anime_photo_url, 
                    caption="✨ **AI Anime Filter ဖြင့် ဖန်တီးပြီးစီးပါပြီ!** ✨", 
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(f"⚠️ အန်နီမေးပုံလင့်ခ်ကို ရှာမတွေ့ပါ။\nAPI Response: {str(result)}")
        else:
            await update.message.reply_text(f"❌ API Error တက်သွားသည်။ Code: {response.status_code}\nအသေးစိတ်: {response.text}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ ဆာဗာချိတ်ဆက်မှု အဆင်မပြေပါ- {str(e)}")

# =====================================================================
# ၃။ ပရိုဂရမ် စတင်ပတ်မည့်နေရာ
# =====================================================================
def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    
    # စာသားမဟုတ်ဘဲ User ပို့လိုက်တဲ့ ဓာတ်ပုံ (Photo) တွေကိုပဲ ဖမ်းယူပြီး處理ခိုင်းခြင်း
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Anime Filter Bot စတင်ပတ်နေပါပြီ...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
