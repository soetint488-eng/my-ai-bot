import os
import sys
import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Telegram Bot Token
TOKEN = "8702294693:AAHzhhFSuogotRM4US1SSlnb2sogss6FUPA"

# Common Headers for RapidAPI
HEADERS = {
    'Content-Type': 'application/json',
    'x-rapidapi-host': 'text-to-video3.p.rapidapi.com',
    'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
}

# =====================================================================
# ၁။ /start ခေါ်လျှင် လမ်းညွှန်ချက်ပြသခြင်း
# =====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "🎬 **AI Text-to-Video Generator Bot** 🎬\n\n"
        "သင်စိတ်ကူးထဲရှိသော စာသားများကို ရိုက်ပို့ပေးရုံဖြင့် AI က စက္ကန့်ပိုင်းအတွင်း ဗီဒီယိုအဖြစ် ဖန်တီးပေးမည် ဖြစ်ပါသည်။\n\n"
        "📝 **အသုံးပြုနည်း-**\n"
        "ဗီဒီယိုအဖြစ် ပုံဖော်ချင်သည့် စာသား (Prompt) ကို အင်္ဂလိပ်လို ရိုက်ပို့ပေးလိုက်ပါဗျာ။\n"
        "(ဥပမာ - `A beautiful cyberpunk city at night, 4k, cinematic`)"
    )
    await update.message.reply_text(text=welcome_text, parse_mode="Markdown")

# =====================================================================
# ၂။ စာသားဝင်လာလျှင် ဗီဒီယိုဖန်တီးပြီး Polling စနစ်ဖြင့် စောင့်ဆိုင်းပေးမည့်အပိုင်း
# =====================================================================
async def generate_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt_text = update.message.text.strip()
    
    # စတင်ကြောင်း အကြောင်းကြားစာ ပို့ခြင်း
    status_msg = await update.message.reply_text("🚀 AI ဆာဗာသို့ Request ပို့နေပါပြီ...")

    # ⚠️ အဆင့် (၁) - Text to Video စတင်ရန် POST Request ပို့ခြင်း
    # (မှတ်ချက် - text-to-video3 API ၏ ပုံမှန် အသုံးများသော POST Generation Endpoint ဖြစ်ပါသည်)
    GENERATE_URL = "https://text-to-video3.p.rapidapi.com/MediaToVideo"
    payload = {
        "text_prompt": prompt_text,
        "aspect_ratio": "16:9"
    }

    try:
        response = requests.post(GENERATE_URL, headers=HEADERS, json=payload)
        
        if response.status_code == 200 or response.status_code == 201:
            gen_result = response.json()
            
            # API မှ ပြန်ပေးသော Task ID သို့မဟုတ် Media ID ကို ရယူခြင်း
            # (API တည်ဆောက်ပုံအလိုက် id, media_id, task_id စသဖြင့် လာနိုင်ပါသည်)
            task_id = gen_result.get("id") or gen_result.get("media_id") or gen_result.get("task_id")
            
            if not task_id:
                await status_msg.edit_text(f"⚠️ Task ID မထွက်လာပါ။ API Response: {str(gen_result)}")
                return
            
            await status_msg.edit_text("⏳ AI က ဗီဒီယိုကို စတင်ဆွဲနေပါပြီ။ မိနစ်အနည်းငယ် ကြာနိုင်သဖြင့် ခဏစောင့်ပေးပါ...")

            # 🔄 အဆင့် (၂) - မိတ်ဆွေပေးထားသော GET Endpoint ကို သုံးပြီး Polling (လှမ်းလှမ်းစစ်ခြင်း) ပြုလုပ်ခြင်း
            # အမြင့်ဆုံး ၁၅ ကြိမ် (စက္ကန့် ၁၅၀ ခန့်) အထိ စစ်ဆေးပါမည်
            max_attempts = 15
            video_url = None
            
            for attempt in range(max_attempts):
                await asyncio.sleep(10) # ၁၀ စက္ကန့် တစ်ကြိမ် စစ်ဆေးမည်
                
                # မိတ်ဆွေပေးထားသော GET url ပုံစံအတိုင်း နောက်ဆုံးတွင် task_id တွဲထည့်ခြင်း
                STATUS_URL = f"https://text-to-video3.p.rapidapi.com/MediaToVideo/{task_id}"
                status_response = requests.get(STATUS_URL, headers=HEADERS)
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    
                    # API သတ်မှတ်ချက်အရ status က "completed" သို့မဟုတ် ဗီဒီယိုလင့်ခ် တိုက်ရိုက်ပါမပါ စစ်ခြင်း
                    # (ပုံမှန်အားဖြင့် result["video_url"] သို့မဟုတ် status== 'success' တွင် လင့်ခ်ပါတတ်ပါသည်)
                    video_url = status_result.get("video_url") or status_result.get("url") or status_result.get("output_url")
                    
                    # အကယ်၍ အဆင့်ဆင့် ထပ်ဝင်ရလျှင်
                    if not video_url and "data" in status_result and isinstance(status_result["data"], dict):
                        video_url = status_result["data"].get("url") or status_result["data"].get("video")

                    # ဗီဒီယိုလင့်ခ် ရပြီဆိုလျှင် Loop ထဲမှ ထွက်မည်
                    if video_url:
                        break
                        
                    # စောင့်ဆိုင်းနေဆဲ အခြေအနေကို User အား ပြသရန်
                    current_status = status_result.get("status", "processing").lower()
                    if current_status in ["failed", "error"]:
                        await status_msg.edit_text("❌ AI ဗီဒီယို ဖန်တီးမှု မအောင်မြင်ပါ။ ဆာဗာတွင် Error ဖြစ်ပွားခဲ့သည်။")
                        return
                        
                    await status_msg.edit_text(f"⏳ ဗီဒီယို ဆွဲနေဆဲ ဖြစ်ပါသည်... (စမ်းသပ်မှုအကြိမ်ရေ: {attempt+1}/{max_attempts})")
                else:
                    print(f"Status check failed: {status_response.status_code}")

            # 📥 အဆင့် (၃) - ရလာသော ဗီဒီယိုအား User ထံ ပြန်လည်ပေးပို့ခြင်း
            if video_url:
                await status_msg.delete() # စောင့်ခိုင်းထားသော စာသားအား ဖျက်ခြင်း
                await update.message.reply_video(
                    video=video_url,
                    caption=f"🎬 **AI Video Generation အောင်မြင်ပါသည်!**\n\n📝 **Prompt:** `{prompt_text}`",
                    parse_mode="Markdown"
                )
            else:
                await status_msg.edit_text("⚠️ ဗီဒီယို ဖန်တီးချိန် ကြာမြင့်နေပါသည်။ နောက်မှတစ်ခါ ပြန်လည်စမ်းသပ်ပေးပါရန်။")
        else:
            await status_msg.edit_text(f"❌ API စတင်ချိတ်ဆက်မှု မအောင်မြင်ပါ။ Code: {response.status_code}\nအသေးစိတ်: {response.text}")
            
    except Exception as e:
        await status_msg.edit_text(f"❌ ချိတ်ဆက်မှု အဆင်မပြေပါ- {str(e)}")

# =====================================================================
# ၃။ ပရိုဂရမ် စတင်ပတ်မည့်နေရာ
# =====================================================================
def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    
    # ဝင်လာသမျှ စာသား (Prompt) များကို ဖမ်းယူရန်
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_video))

    print("Text-to-Video Polling Bot စတင်ပတ်နေပါပြီ...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
