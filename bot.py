import os
import sys
import threading
import requests
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# =====================================================================
# 🛠️ RENDER PORT BINDING ERROR အတွက် FLASK SERVER
# =====================================================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Face Swap Bot is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

# =====================================================================
# Telegram Bot Token နှင့် ယာယီ Session နေရာများ
# =====================================================================
TOKEN = "8702294693:AAHzhhFSuogotRM4US1SSlnb2sogss6FUPA"
user_photos = {}

HEADERS = {
    'Content-Type': 'application/json',
    'x-rapidapi-host': 'face-swap-video-image-multiface.p.rapidapi.com',
    'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "🎭 **AI Face Swap Bot (Polling Version)** 🎭\n\n"
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
            "ယခု အဆိုပါမျက်နှာကို သွားထည့်မည့် **ดုတိယပုံ (Target Body Image)** ကို ပို့ပေးပါဗျာ။"
        )
        return

    # ဒုတိယပုံ ဝင်လာခြင်း
    source_url = user_photos[user_id]["source_url"]
    target_url = telegram_image_url
    del user_photos[user_id] # Session ဖြတ်ခြင်း

    status_msg = await update.message.reply_text("⏳ AI ဆာဗာတွင် တန်းစီစောင့်ဆိုင်းနေပါပြီ (IN_QUEUE)...")

    API_URL = "https://face-swap-video-image-multiface.p.rapidapi.com/runsync"
    payload = {
        "input": {
            "enhanceState": True,
            "mode": "swap-face",
            "url": source_url,
            "targetUrl": target_url
        }
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # မိတ်ဆွေပြခဲ့တဲ့ Response အတိုင်း 'id' (Task ID) ကို ယူခြင်း
            task_id = result.get("id")
            status = result.get("status", "").upper()
            
            # အကယ်၍ တန်းပြီး ပုံထွက်မလာဘဲ Queue ဖြစ်နေလျှင် Polling ပတ်မည်
            if status in ["IN_QUEUE", "IN_PROGRESS", "STARTING"] and task_id:
                
                # အမြင့်ဆုံး အကြိမ် ၂၀ (စက္ကန့် ၁၀၀ ခန့်) အထိ လှမ်းစစ်ပါမည်
                max_attempts = 20
                swapped_photo_url = None
                
                for attempt in range(max_attempts):
                    await asyncio.sleep(5) # ၅ စက္ကန့်တစ်ကြိမ် လှမ်းစစ်မည်
                    
                    # 💡 Task ID ကို သုံးပြီး Status ပြန်စစ်သည့် Endpoint
                    # (RapidAPI Face Swap များတွင် ပုံမှန်အားဖြင့် /status သို့မဟုတ် /get သုံးလေ့ရှိသည်၊ ဤနေရာတွင် status check လုပ်ပုံကို စနစ်တကျ ရေးထားပါသည်)
                    STATUS_URL = f"https://face-swap-video-image-multiface.p.rapidapi.com/status/{task_id}"
                    
                    # တကယ်လို့ API က status စစ်ဖို့ endpoint သီးသန့်မပေးထားရင် /runsync ဆီကိုပဲ Task ID နဲ့ GET request ပို့ကြည့်ရတတ်ပါတယ်
                    # အောက်ပါအတိုင်း status စစ်ဆေးခြင်းကို ပြုလုပ်ပါမည်
                    status_response = requests.get(STATUS_URL, headers=HEADERS)
                    
                    if status_response.status_code == 200:
                        status_result = status_response.json()
                        
                        # ရလဒ်ထဲက ပုံလင့်ခ်ကို ရှာဖွေခြင်း
                        swapped_photo_url = status_result.get("output_url") or status_result.get("image") or status_result.get("url")
                        if not swapped_photo_url and isinstance(status_result.get("output"), list):
                            swapped_photo_url = status_result["output"][0]
                        elif not swapped_photo_url and "data" in status_result and isinstance(status_result["data"], dict):
                            swapped_photo_url = status_result["data"].get("url")
                            
                        # ပုံထွက်လာပြီဆိုလျှင် စစ်ဆေးခြင်းကို ရပ်တန့်မည်
                        if swapped_photo_url:
                            break
                            
                        current_status = status_result.get("status", "IN_QUEUE")
                        await status_msg.edit_text(f"⏳ AI က မျက်နှာလဲလှယ်ပေးနေဆဲ ဖြစ်ပါသည်... ({current_status})")
                    else:
                        # အကယ်၍ /status/{id} မဟုတ်ဘဲ GET parameter နဲ့ သွားရတာမျိုး ဖြစ်နိုင်လျှင်
                        ALT_URL = f"https://face-swap-video-image-multiface.p.rapidapi.com/status?id={task_id}"
                        alt_response = requests.get(ALT_URL, headers=HEADERS)
                        if alt_response.status_code == 200:
                            alt_result = alt_response.json()
                            swapped_photo_url = alt_result.get("output_url") or alt_result.get("image") or (alt_result.get("output")[0] if isinstance(alt_result.get("output"), list) else None)
                            if swapped_photo_url:
                                break
                
                # စစ်ဆေးပြီးနောက် ပုံရလာပါက ပို့ပေးမည်
                if swapped_photo_url:
                    await status_msg.delete()
                    await update.message.reply_photo(
                        photo=swapped_photo_url, 
                        caption="🎭 **AI Face Swap ဖြင့် မျက်နှာလဲလှယ်ခြင်း အောင်မြင်ပါသည်!** 🎭", 
                        parse_mode="Markdown"
                    )
                else:
                    await status_msg.edit_text("⚠️ ဓာတ်ပုံဖန်တီးချိန် ကြာမြင့်နေပါသည်။ ခဏနေမှ ထပ်မံစမ်းသပ်ပေးပါရန်။")
            
            # အကယ်၍ Queue မဝင်ဘဲ တိုက်ရိုက် ပုံထွက်လာခဲ့လျှင် (Direct Output)
            else:
                swapped_photo_url = result.get("output_url") or result.get("image") or (result.get("output")[0] if isinstance(result.get("output"), list) else None)
                if swapped_photo_url:
                    await status_msg.delete()
                    await update.message.reply_photo(photo=swapped_photo_url, caption="🎭 AI Face Swap အောင်မြင်ပါသည်!")
                else:
                    await status_msg.edit_text(f"⚠️ ပုံထွက်မလာပါ။ API Response: {str(result)}")
        else:
            await status_msg.edit_text(f"❌ API Error တက်သွားသည်။ Code: {response.status_code}\nအသေးစိတ်: {response.text}")
            
    except Exception as e:
        await status_msg.edit_text(f"❌ ဆာဗာချက်ဆက်မှု အဆင်မပြေပါ- {str(e)}")

def main() -> None:
    threading.Thread(target=run_flask, daemon=True).start()

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_face_swap))

    print("AI Face Swap Polling Version Running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
