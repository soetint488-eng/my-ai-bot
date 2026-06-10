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
        "🎨 မင်္ဂလာပါဗျာ။ ကျွန်တော်ကတော့ **FLUX AI Text-to-Image Bot** ဖြစ်ပါတယ်။\n\n"
        "သင် စိတ်ကူးထဲရှိတဲ့အတိုင်း ပုံဖော်ချင်တဲ့ စာသား (Prompt) တွေကို ပေးပို့နိုင်ပါတယ်ခင်ဗျာ။\n"
        "*(မြန်မာလိုရော အင်္ဂလိပ်လိုပါ ရိုက်ပို့လို့ရပါတယ်)*\n\n"
        "ဥပမာ - `iron man and spider man` သို့မဟုတ် `လှပတဲ့ မြန်မာအမျိုးသမီးတစ်ဦး` စသဖြင့်။"
    )
    await update.message.reply_text(text=welcome_text, parse_mode="Markdown")

# =====================================================================
# ၂။ User ပို့လာသည့် စာသားကို FLUX AI ဖြင့် ပုံဖော်ပေးမည့်အပိုင်း
# =====================================================================
async def handle_flux_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_prompt = update.message.text  # User ရိုက်ပို့လိုက်သော စာသား

    await update.message.reply_text("⏳ FLUX AI ဖြင့် ဓာတ်ပုံ စတင်ဖန်တီးနေပါပြီ။ ၁ မိနစ်ခန့် ကြာနိုင်သဖြင့် ခဏစောင့်ဆိုင်းပေးပါ...")

    # ပေးထားသော curl အတိုင်း အချက်အလက်များ သတ်မှတ်ခြင်း
    API_URL = "https://ai-text-to-image-generator-flux-free-api.p.rapidapi.com/aaaaaaaaaaaaaaaaaiimagegenerator/quick.php"
    
    headers = {
        'Content-Type': 'application/json',
        'x-rapidapi-host': 'ai-text-to-image-generator-flux-free-api.p.rapidapi.com',
        'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
    }

    # curl ထဲက --data အတိုင်း JSON Payload တည်ဆောက်ခြင်း
    payload = {
        "prompt": user_prompt, # User ပို့လိုက်သော စာသားကို ထည့်သွင်းခြင်း
        "style_id": 4,         # ပေးထားသည့်အတိုင်း Style ID 4 သုံးထားသည်
        "size": "1-1"          # ပုံစံ 1:1 လေးထောင့်ပုံစံ
    }

    try:
        # POST Method ဖြစ်ပြီး content-type: json မို့ json=payload ကို သုံးပါသည်
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # API က ပြန်ပေးတဲ့ JSON ထဲက ထွက်လာမယ့် ပုံလင့်ခ် (Key) ကို ရှာဖွေခြင်း
            # FLUX API အများစုတွင် 'url', 'image', 'status: success' စသဖြင့် ပါတတ်သည်
            output_url = result.get("url") or result.get("image_url") or result.get("image") or result.get("output")
            
            # အကယ်၍ API က direct url မပေးဘဲ key တစ်ခုခုထဲ ဝှက်ပေးထားရင် စစ်ဆေးရန် (ဥပမာ- result['data'][0]['url'])
            if not output_url and "data" in result and len(result["data"]) > 0:
                output_url = result["data"][0].get("url")

            if output_url:
                await update.message.reply_photo(photo=output_url, caption=f"✨ FLUX AI ဖြင့် ဖန်တီးပြီးစီးပါပြီ-\n`{user_prompt}`", parse_mode="Markdown")
            else:
                # ပုံထွက်မလာရင် API Response ကို စာသားအတိုင်း ပြပေးဖို့ပါ
                await update.message.reply_text(f"⚠️ ပုံလင့်ခ်ကို ရှာမတွေ့ပါ။\nAPI Response: {str(result)}")
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
    
    # User ပို့သမျှ စာသားတွေကို ဖမ်းယူပြီး handle_flux_image ဆီ ပို့ပေးခြင်း
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_flux_image))

    print("FLUX Image Bot စတင်ပတ်နေပါပြီ...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
