import os
import sys
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Telegram Bot Token
TOKEN = "8702294693:AAHzhhFSuogotRM4US1SSlnb2sogss6FUPA"

# =====================================================================
# ၁။ /start ခေါ်လျှင် လမ်းညွှန်ချက်ပြသခြင်း
# =====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "✨ **AI Face & Photo Enhancer Bot** ✨\n\n"
        "ဝါးနေတဲ့ ဓာတ်ပုံတွေနဲ့ မျက်နှာတွေကို AI နည်းပညာသုံးပြီး HD Quality ဖြစ်အောင် အကြည်ပြင်ပေးမည့် Bot ဖြစ်ပါတယ်။\n\n"
        "📸 **အသုံးပြုနည်း-**\n"
        "ကျွန်တော့်ဆီကို သင်အကြည်ပြင်ချင်တဲ့ **ဓာတ်ပုံ (Photo)** တစ်ပုံ ပို့ပေးလိုက်ရုံပါပဲဗျာ။"
    )
    await update.message.reply_text(text=welcome_text, parse_mode="Markdown")

# =====================================================================
# ၂။ User ပို့လာသော ဓာတ်ပုံကို ဖမ်းယူပြီး API ဖြင့် အကြည်ပြင်မည့်အပိုင်း
# =====================================================================
async def handle_enhance_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # User ပို့လိုက်တဲ့ ဓာတ်ပုံထဲက အကြည်ဆုံး Size ရဲ့ file_path ကို လှမ်းယူခြင်း
    photo_file = await update.message.photo[-1].get_file()
    telegram_image_url = photo_file.file_path

    await update.message.reply_text("⏳ AI က သင့်ဓာတ်ပုံကို စတင်ပြီး အကြည်ပြင်ပေးနေပါပြီ။ ခဏစောင့်ဆိုင်းပေးပါ...")

    # ပေးထားသော curl တိုင်း သတ်မှတ်ခြင်း
    API_URL = "https://ai-face-enhancer.p.rapidapi.com/face/editing/enhance-face"
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-rapidapi-host': 'ai-face-enhancer.p.rapidapi.com',
        'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
    }

    # x-raw-form-urlencoded ဖြစ်လို့ json= အစား data= သုံးပြီး ပို့ရပါမည်
    # curl ထဲက --data image= အတိုင်း key နာမည်ကို 'image' ဟု ပေးထားပါသည်
    payload = {
        "image": telegram_image_url
    }

    try:
        # POST Request ဖြင့် Form Data ပို့ခြင်း
        response = requests.post(API_URL, headers=headers, data=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # API က ပြန်ပေးမယ့် အကြည်ပြင်ပြီးသား ပုံလင့်ခ်ကို ရှာဖွေခြင်း
            enhanced_url = result.get("enhanced_image_url") or result.get("image_url") or result.get("url") or result.get("output")
            
            # အကယ်၍ ဒေတာက result['data']['url'] ထဲမှာ ရှိနေခဲ့လျှင်
            if not enhanced_url and "data" in result and isinstance(result["data"], dict):
                enhanced_url = result["data"].get("url") or result["data"].get("image")

            if enhanced_url:
                # ရလာတဲ့ HD ပုံကို User ဆီ ပြန်လည်ပေးပို့ခြင်း
                await update.message.reply_photo(
                    photo=enhanced_url, 
                    caption="🚀 **AI Photo Enhancer ဖြင့် အကြည်ပြင်ခြင်း အောင်မြင်ပါသည်!**", 
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(f"⚠️ ပုံထွက်မလာပါ။ API Response ကို စစ်ဆေးပါ-\nAPI Response: {str(result)}")
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
    
    # ဓာတ်ပုံဝင်လာသမျှကို ဖမ်းယူရန် သတ်မှတ်ခြင်း
    application.add_handler(MessageHandler(filters.PHOTO, handle_enhance_photo))

    print("Photo Enhancer Bot စတင်ပတ်နေပါပြီ...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
