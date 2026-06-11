import os
import sys
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Telegram Bot Token
TOKEN = "8702294693:AAHzhhFSuogotRM4US1SSlnb2sogss6FUPA"

# User တစ်ယောက်ချင်းစီရဲ့ ဓာတ်ပုံနှစ်ပုံကို ယာယီမှတ်ထားရန် Dictionary
user_photos = {}

# =====================================================================
# ၁။ /start ခေါ်လျှင် နှုတ်ခွန်းဆက်စကားနှင့် လမ်းညွှန်ချက်ပြခြင်း
# =====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "🎭 **AI Face Swap Bot မှ ကြိုဆိုပါတယ်** 🎭\n\n"
        "ဓာတ်ပုံတစ်ပုံထဲက မျက်နှာကို နောက်ဓာတ်ပုံတစ်ပုံရဲ့ ကိုယ်ထည်ပေါ်သို့ AI သုံးပြီး အစားထိုးပေးမည့် စနစ်ဖြစ်ပါသည်။\n\n"
        "📸 **အသုံးပြုနည်းလမ်းညွှန်-**\n"
        "၁။ ပထမဦးစွာ **မျက်နှာယူမည့်သူ၏ ဓာတ်ပုံ (Source Face)** ကို ပို့ပေးပါ။\n"
        "၂။ ပြီးနောက် သွားရောက်ထည့်သွင်းမည့် **နောက်ခံခန္ဓာကိုယ် ဓာတ်ပုံ (Target Body)** ကို ဒုတိယပုံအနေဖြင့် ပို့ပေးရပါမည်။"
    )
    await update.message.reply_text(text=welcome_text, parse_mode="Markdown")

# =====================================================================
# ၂။ User ပို့လာသော ဓာတ်ပုံများကို အဆင့်ဆင့် လက်ခံမှတ်သားပြီး API သို့ ပို့ခြင်း
# =====================================================================
async def handle_face_swap(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    
    # ဓာတ်ပုံထဲက အကြည်ဆုံး Size ရဲ့ file_path (URL) ကို ယူခြင်း
    photo_file = await update.message.photo[-1].get_file()
    telegram_image_url = photo_file.file_path

    # User က ပထမဆုံးအကြိမ် ပုံပို့ခြင်း ဖြစ်ပါက (Source Face အဖြစ် သတ်မှတ်မည်)
    if user_id not in user_photos:
        user_photos[user_id] = {
            "source_url": telegram_image_url
        }
        await update.message.reply_text(
            "✅ **ပထမပုံ (မျက်နှာ) ကို မှတ်သားပြီးပါပြီ။**\n\n"
            "ယခု အဆိုပါမျက်နှာကို သွားထည့်မည့် **ဒုတိယပုံ (Target Body Image)** ကို ပို့ပေးပါဗျာ။"
        )
        return

    # ဒုတိယပုံ ဝင်လာပါက (Target URL အဖြစ် သတ်မှတ်ပြီး API သို့ တန်းပို့မည်)
    source_url = user_photos[user_id]["source_url"]
    target_url = telegram_image_url
    
    # Session ကို ချက်ချင်းပြန်ဖျက်ခြင်း
    del user_photos[user_id]

    status_msg = await update.message.reply_text("⏳ AI က မျက်နှာချင်း အစားထိုးလဲလှယ်ပေးနေပါပြီ။ ခဏစောင့်ပေးပါ...")

    # ပေးထားသော curl specification အတိုင်း တည်ဆောက်ခြင်း
    API_URL = "https://face-swap-video-image-multiface.p.rapidapi.com/runsync"
    
    headers = {
        'Content-Type': 'application/json',
        'x-rapidapi-host': 'face-swap-video-image-multiface.p.rapidapi.com',
        'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
    }

    # curl --data အတွင်းရှိ JSON structure အတိုင်း ကွက်တိ ပြင်ဆင်ခြင်း
    payload = {
        "input": {
            "enhanceState": True,
            "mode": "swap-face",
            "url": source_url,       # ပထမပုံ (Source မျက်နှာ)
            "targetUrl": target_url   # ဒုတိယပုံ (Target ကိုယ်ထည်)
        }
    }

    try:
        # POST Request ပို့ခြင်း
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # API ရဲ့ output ပုံစံအလိုက် ရလဒ်ပုံလင့်ခ်ကို ဆွဲထုတ်ခြင်း
            # (အသုံးများသော ကီးများဖြစ်သည့် output_url, image, result သို့မဟုတ် data ထဲမှ ရှာပါမည်)
            swapped_photo_url = result.get("output_url") or result.get("image") or result.get("url") or result.get("result")
            
            if not swapped_photo_url and "data" in result and isinstance(result["data"], dict):
                swapped_photo_url = result["data"].get("url") or result["data"].get("image")
            
            # ဒေတာက list ပုံစံမျိုးနဲ့ ကျလာတတ်လျှင် (ဥပမာ- result["output"][0])
            if not swapped_photo_url and isinstance(result.get("output"), list):
                swapped_photo_url = result["output"][0]

            if swapped_photo_url:
                await status_msg.delete() # စောင့်ခိုင်းထားသော စာသားကို ဖျက်ခြင်း
                await update.message.reply_photo(
                    photo=swapped_photo_url, 
                    caption="🎭 **AI Face Swap ဖြင့် မျက်နှာလဲလှယ်ခြင်း အောင်မြင်ပါသည်!** 🎭", 
                    parse_mode="Markdown"
                )
            else:
                await status_msg.edit_text(f"⚠️ မျက်နှာလဲထားတဲ့ ပုံလင့်ခ်ကို ရှာမတွေ့ပါ။\nAPI Response: {str(result)}")
        else:
            await status_msg.edit_text(f"❌ API Error တက်သွားသည်။ Code: {response.status_code}\nအသေးစိတ်: {response.text}")
            
    except Exception as e:
        await status_msg.edit_text(f"❌ ဆာဗာချက်ဆက်မှု အဆင်မပြေပါ- {str(e)}")

# =====================================================================
# ၃။ ပရိုဂရမ် စတင်ပတ်မည့်နေရာ
# =====================================================================
def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    
    # User ပို့သမျှ ဓာတ်ပုံအားလုံးကို handle_face_swap ဆီ ညွှန်းပေးခြင်း
    application.add_handler(MessageHandler(filters.PHOTO, handle_face_swap))

    print("AI Face Swap Bot Running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
