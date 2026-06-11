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
# ၂။ User ပို့လာသော ဓာတ်ပုံကို ဒေါင်းလုဒ်ဆွဲပြီး API သို့ File အလိုက် Upload တင်မည့်အပိုင်း
# =====================================================================
async def handle_enhance_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # User ပို့လိုက်တဲ့ ဓာတ်ပုံထဲက အကြည်ဆုံး Size ကို ယူခြင်း
    photo_file = await update.message.photo[-1].get_file()
    
    # ယာယီသိမ်းမည့် ဖိုင်အမည် သတ်မှတ်ခြင်း
    local_filename = f"temp_{update.message.from_user.id}.jpg"
    
    # ၁။ Telegram ဆာဗာပေါ်က ပုံကို စက်ထဲ (သို့မဟုတ်) Render ဆာဗာထဲသို့ အရင်ဒေါင်းလုဒ်ဆွဲခြင်း
    await photo_file.download_to_drive(local_filename)

    status_message = await update.message.reply_text("⏳ AI က သင့်ဓာတ်ပုံကို စတင်ပြီး အကြည်ပြင်ပေးနေပါပြီ။ ခဏစောင့်ဆိုင်းပေးပါ...")

    API_URL = "https://ai-face-enhancer.p.rapidapi.com/face/editing/enhance-face"
    
    # ⚠️ 'Content-Type' ကို ဖယ်ထုတ်လိုက်ပါသည်၊ requests က file တင်တဲ့အခါ boundary အလိုအလျောက် သတ်မှတ်ပေးရန်ဖြစ်သည်
    headers = {
        'x-rapidapi-host': 'ai-face-enhancer.p.rapidapi.com',
        'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
    }

    try:
        # ၂။ ဒေါင်းလုဒ်ဆွဲထားသော ပုံကို Binary File အဖြစ် ဖွင့်ပြီး API ဆီ တိုက်ရိုက်တွဲတင် (Upload) ခြင်း
        with open(local_filename, 'rb') as f:
            files = {
                'image': (local_filename, f, 'image/jpeg') # curl ထဲက image= နေရာတွင် ဖိုင်တွဲထည့်ခြင်း
            }
            
            # files= ကို သုံးပြီး POST Request ပို့ပါသည်
            response = requests.post(API_URL, headers=headers, files=files)
        
        # ဒေါင်းလုဒ်လုပ်ထားသော ယာယီဖိုင်ကို ချက်ချင်းပြန်ဖျက်ခြင်း (ဆာဗာနေရာ မပြည့်စေရန်)
        if os.path.exists(local_filename):
            os.remove(local_filename)
            
        if response.status_code == 200:
            result = response.json()
            
            # API Response ထဲက ပုံလင့်ခ်ကို ရှာဖွေခြင်း
            enhanced_url = result.get("enhanced_image_url") or result.get("image_url") or result.get("url") or result.get("output")
            
            if not enhanced_url and "data" in result and isinstance(result["data"], dict):
                enhanced_url = result["data"].get("url") or result["data"].get("image")

            if enhanced_url:
                await status_message.delete() # စောင့်ခိုင်းထားသော စာသားကို ဖျက်ခြင်း
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
        # ဘာပဲဖြစ်ဖြစ် Error တက်ရင်လည်း ယာယီဖိုင်ကို ပြန်ဖျက်ပေးရန်
        if os.path.exists(local_filename):
            os.remove(local_filename)
        await update.message.reply_text(f"❌ ဆာဗာချက်ဆက်မှု အဆင်မပြေပါ- {str(e)}")

# =====================================================================
# ၃။ ပရိုဂရမ် စတင်ပတ်မည့်နေရာ
# =====================================================================
def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_enhance_photo))

    print("Photo Enhancer Bot Files Version Running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
