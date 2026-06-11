import os
import sys
import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Telegram Bot Token
TOKEN = "8702294693:AAHzhhFSuogotRM4US1SSlnb2sogss6FUPA"

# User တစ်ယောက်ချင်းစီရဲ့ Video data ကို ယာယီမှတ်ထားရန် Dictionary
user_sessions = {}

# =====================================================================
# ၁။ /start ခေါ်လျှင် နှုတ်ခွန်းဆက်စကား ပြောခြင်း
# =====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "🎬 **RunwayML Video Extend Bot မှ ကြိုဆိုပါတယ်** 🎬\n\n"
        "ဤ Bot သည် သင့်ဗီဒီယိုကို AI နည်းပညာဖြင့် အရှည်ထပ်မံ တိုးမြှင့်ဖန်တီးပေးမည် ဖြစ်ပါသည်။\n\n"
        "📥 **အသုံးပြုနည်း-**\n"
        "၁။ ပထမဆုံး အနေဖြင့် သင်ပြုပြင်လိုသော **ဗီဒီယို (Video)** အသေးတစ်ခုကို ပို့ပေးပါ။\n"
        "၂။ ပြီးနောက် ဗီဒီယို ဆက်လက်ဖြစ်ပျက်သွားစေချင်သည့် **စာသား (Text Prompt)** ကို ရိုက်ပို့ပေးရပါမည်။"
    )
    await update.message.reply_text(text=welcome_text, parse_mode="Markdown")

# =====================================================================
# ၂။ User ပို့လာသော ဗီဒီယိုကို လက်ခံမှတ်သားထားခြင်း
# =====================================================================
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    
    # User ပို့လိုက်တဲ့ ဗီဒီယို File ကို ယူခြင်း
    video_file = await update.message.video.get_file()
    
    # စမ်းသပ်မှုလွယ်ကူစေရန် မူရင်းဗီဒီယိုရဲ့ Direct URL ကို မှတ်ထားလိုက်ပါမည်
    # (တကယ့် Runway API တွင် ယခင် Task ရဲ့ uuid တောင်းတတ်သော်လည်း နမူနာအရ ဤနေရာတွင် သိမ်းဆည်းပါသည်)
    user_sessions[user_id] = {
        "video_url": video_file.file_path,
        "uuid": video_file.file_id  # နမူနာ uuid အဖြစ် သုံးခြင်း
    }
    
    await update.message.reply_text(
        "✅ ဗီဒီယိုကို မှတ်သားပြီးပါပြီ။\n"
        "ယခု အဆိုပါဗီဒီယိုကို မည်သို့ဆက်လက် ပုံဖော်စေချင်သလဲဆိုသည့် **စာသား (Prompt)** ကို အင်္ဂလိပ်လို ရိုက်ပို့ပေးပါဗျာ။\n"
        "ဥပမာ - `cinematic lighting, drone shot, heavy rain`"
    )

# =====================================================================
# ၃။ စာသားရလာပါက RunwayML API သို့ လှမ်းပို့ပြီး Video ထုတ်ယူခြင်း
# =====================================================================
async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    prompt_text = update.message.text.strip()

    # User က ဗီဒီယို မပို့ဘဲ စာတန်းလာရိုက်ရင် တားဆီးခြင်း
    if user_id not in user_sessions:
        await update.message.reply_text("⚠️ ကျေးဇူးပြု၍ စာသားမပို့မီ ဗီဒီယိုကို အရင်ဆုံး ပို့ပေးပါခင်ဗျာ။")
        return

    video_data = user_sessions[user_id]
    
    # ယာယီ session အား ဖျက်သိမ်းခြင်း
    del user_sessions[user_id]

    status_msg = await update.message.reply_text("⏳ RunwayML API သို့ တောင်းဆိုနေပါပြီ။ ဗီဒီယိုဖန်တီးခြင်းသည် ၁ မိနစ်မှ ၂ မိနစ်အထိ ကြာမြင့်နိုင်သဖြင့် ခဏစောင့်ပေးပါ...")

    API_URL = "https://runwayml.p.rapidapi.com/extend"
    headers = {
        'Content-Type': 'application/json',
        'x-rapidapi-host': 'runwayml.p.rapidapi.com',
        'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
    }

    # curl --data အတွင်းရှိ သတ်မှတ်ချက်များအတိုင်း ဖြည့်သွင်းခြင်း
    payload = {
        "uuid": video_data["uuid"],       # မှတ်ထားသော ဗီဒီယို ID
        "model": "gen2",                  # Runway Gen-2 Model
        "text_prompt": prompt_text,       # User ရိုက်ပို့လိုက်သော စာသား
        "motion": 5,                      # လှုပ်ရှားမှုနှုန်း ၅
        "seed": 0,
        "callback_url": ""
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # 💡 ဗီဒီယို API များသည် ပုံမှန်အားဖြင့် ချက်ချင်း output မကျဘဲ task_id သို့မဟုတ် ရလဒ်လင့်ခ် ပေးတတ်ပါသည်
            # ဤနေရာတွင် တိုက်ရိုက် လင့်ခ်ကျလာသည်ဟု ယူဆပြီး ဆွဲထုတ်ပုံကို ရေးပြထားပါသည်
            output_video_url = result.get("video_url") or result.get("url") or result.get("output")
            
            if not output_video_url and "data" in result and isinstance(result["data"], dict):
                output_video_url = result["data"].get("url")

            # အကယ်၍ API က ချက်ချင်း ဗီဒီယိုမပေးဘဲ Task ID ပေးပြီး ခဏစောင့်ခိုင်းလျှင် (Polling စနစ်လိုအပ်ပါသည်)
            # ဤကုဒ်သည် တိုက်ရိုက်ရလဒ်ထွက်သော ပုံစံအတွက် ရည်ရွယ်ပါသည်
            if output_video_url:
                await status_msg.delete()
                await update.message.reply_video(
                    video=output_video_url,
                    caption=f"🎬 **RunwayML AI Video Extend အောင်မြင်ပါသည်!**\n\n📝 **Prompt:** `{prompt_text}`",
                    parse_mode="Markdown"
                )
            else:
                # ရလဒ် တိုက်ရိုက်မထွက်သေးဘဲ Status ပြနေပါက ပြသရန်
                await update.message.reply_text(f"⚙️ API မှ လုပ်ဆောင်ချက်ကို လက်ခံရရှိပြီးပါပြီ။\nResponse: {str(result)}")
        else:
            await update.message.reply_text(f"❌ API Error တက်သွားသည်။ Code: {response.status_code}\nအသေးစိတ်: {response.text}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ ဆာဗာချိတ်ဆက်မှု အဆင်မပြေပါ- {str(e)}")

# =====================================================================
# ၄။ ပရိုဂရမ် စတင်ပတ်မည့်နေရာ
# =====================================================================
def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    
    # ဗီဒီယို သီးသန့် ဖမ်းယူရန်
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    # ဗီဒီယိုပို့ပြီးမှ ဝင်လာမည့် စာသား (Prompt) ကို ဖမ်းယူရန်
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt))

    print("RunwayML Bot စတင်လည်ပတ်နေပါပြီ...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
