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
        "👋 မင်္ဂလာပါဗျာ။ ကျွန်တော်ကတော့ **Gemini AI Text-to-Image Bot** ဖြစ်ပါတယ်။\n\n"
        "သင် စိတ်ကူးထဲရှိတဲ့အတိုင်း ပုံဖော်ချင်တဲ့ စာသား (Prompt) တွေကို **အင်္ဂလိပ်လို** ရိုက်ပို့ပေးပါ။\n"
        "ဥပမာ - `A majestic dragon on a mountain` စသဖြင့် ရိုက်ပို့နိုင်ပါတယ်ခင်ဗျာ။"
    )
    await update.message.reply_text(text=welcome_text, parse_mode="Markdown")

# =====================================================================
# ၂။ User က စာသားပို့လာလျှင် Gemini AI ဖြင့် ပုံဖော်ပေးမည့်အပိုင်း
# =====================================================================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_prompt = update.message.text  # User ရိုက်ပို့လိုက်သော စာသား

    await update.message.reply_text("⏳ AI ဖြင့် ဓာတ်ပုံ စတင်ဖန်တီးနေပါပြီ။ ခဏစောင့်ဆိုင်းပေးပါ...")

    # ပေးထားသော curl specification အတိုင်း URL နှင့် Parameter များ သတ်မှတ်ခြင်း
    API_URL = "https://nano-banana-gemini-fast-text-to-image-api.p.rapidapi.com/api/gemini/text-image"
    
    query_params = {
        'prompt': user_prompt,  # User ပို့လိုက်သော စာသားကို ဤနေရာတွင် ထည့်သွင်းပါသည်
        'width': '512',
        'height': '512',
        'seed': '50'
    }
    
    headers = {
        'Content-Type': 'application/json',
        'x-rapidapi-host': 'nano-banana-gemini-fast-text-to-image-api.p.rapidapi.com',
        'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
    }

    try:
        # GET Method ဖြစ်သောကြောင့် requests.get ကို သုံးပါသည်
        response = requests.get(API_URL, headers=headers, params=query_params)
        
        if response.status_code == 200:
            # အကယ်၍ API က ပုံကို လင့်ခ်အဖြစ် မဟုတ်ဘဲ Image Binary (ဖိုင်စစ်စစ်) အနေနဲ့ ပြန်ပေးရင်
            # တိုက်ရိုက် ပို့ပေးနိုင်ရန် response.content ကို သုံးရပါမည်
            if "image" in response.headers.get("Content-Type", ""):
                image_data = response.content
                await update.message.reply_photo(photo=image_data, caption=f"✨ ဖန်တီးပြီးစီးသောပုံစံ- {user_prompt}")
            else:
                # အကယ်၍ JSON data ပြန်ပေးပြီး အထဲတွင် URL ပါဝင်ပါက
                result = response.json()
                output_url = result.get("url") or result.get("image_url") or result.get("image")
                
                if output_url:
                    await update.message.reply_photo(photo=output_url, caption=f"✨ ဖန်တီးပြီးစီးသောပုံစံ- {user_prompt}")
                else:
                    await update.message.reply_text(f"⚠️ ပုံကို ရှာမတွေ့ပါ။ API Response: {str(result)}")
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
    
    # User က စာသား (TEXT) ပို့လာရင် handle_text ထဲကို ပို့ပေးရန် သတ်မှတ်ခြင်း
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Gemini Image Bot စတင်ပတ်နေပါပြီ...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
