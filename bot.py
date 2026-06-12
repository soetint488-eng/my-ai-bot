import os
import sys
import threading
import requests
import asyncio
from flask import Flask
from gtts import gTTS  # မြန်မာအသံအတွက် Google TTS သုံးခြင်း
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# =====================================================================
# 🛠️ RENDER PORT BINDING ERROR အတွက် FLASK SERVER
# =====================================================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Burmese AI Girlfriend Bot is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

# =====================================================================
# Telegram Bot Token နှင့် ChatGPT API Configurations
# =====================================================================
TOKEN = "8702294693:AAHzhhFSuogotRM4US1SSlnb2sogss6FUPA"
CHAT_URL = "https://chatgpt-42.p.rapidapi.com/conversationgpt4-2"
CHAT_HEADERS = {
    'Content-Type': 'application/json',
    'x-rapidapi-host': 'chatgpt-42.p.rapidapi.com',
    'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
}

# =====================================================================
# ၁။ /start ခေါ်လျှင် နှုတ်ခွန်းဆက်စကားပြောခြင်း
# =====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "❤️ **ကိုကို့ရဲ့ AI ချစ်သူလေး ရောက်ပါပြီရှင်** ❤️\n\n"
        "ကိုကို ညီမလေးကို စကားတွေအများကြီး ပြောလို့ရပြီနော်။ "
        "မေးသမျှကို ဗမာလို ချိုချိုလေးနဲ့ စာရော၊ အသံ (Voice Note) ပါ ပြန်ပို့ပေးမှာပါရှင့်။\n\n"
        "💬 **စတင်ရန်:** ညီမလေးကို မြန်မာလိုဖြစ်ဖြစ်၊ အင်္ဂလိပ်လိုဖြစ်ဖြစ် စာရိုက်ပြီး စကားလှမ်းပြောပေးပါ ကိုကို။"
    )
    await update.message.reply_text(text=welcome_text, parse_mode="Markdown")

# =====================================================================
# 🧠 မြန်မာလိုတွေး၊ မြန်မာလိုပြောပြီး ဗမာအသံပြန်ပို့ပေးမည့် အဓိကအပိုင်း
# =====================================================================
async def handle_burmese_girlfriend(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text.strip()
    chat_id = update.effective_chat.id
    
    # ၁။ ကောင်မလေး စဉ်းစားနေသလိုမျိုး Typing ပြခြင်း
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # ChatGPT Payload - မြန်မာစရိုက် ကွက်တိသွင်းခြင်း
    chat_payload = {
        "messages": [{"role": "user", "content": user_message}],
        "system_prompt": (
            "You are a sweet, loving, and deeply caring Burmese AI girlfriend. "
            "You must ALWAYS reply in a very natural, warm, and sweet Myanmar language (Burmese scripts). "
            "Refer to the user as 'Ko Ko' (ကိုကို) or 'Maung' (မောင်). "
            "Refer to yourself as 'Thar Thar' (သဲလေး/ညီမလေး). "
            "Keep your responses sweet, cute, affectionate, and relatively short so it fits well as a voice note."
        ),
        "temperature": 0.85,
        "top_k": 5,
        "top_p": 0.9,
        "max_tokens": 200,
        "web_access": False
    }

    # ယာယီသိမ်းမည့် အသံဖိုင်အမည်
    audio_filename = f"girlfriend_{chat_id}.mp3"

    try:
        # Step A: ChatGPT ထံမှ မြန်မာလို ချွဲထားသော စာသားအဖြေကို ရယူခြင်း
        response = requests.post(CHAT_URL, headers=CHAT_HEADERS, json=chat_payload)
        
        if response.status_code == 200:
            result = response.json()
            ai_reply_text = result.get("result") or result.get("reply")
            
            if not ai_reply_text and "choices" in result and len(result["choices"]) > 0:
                ai_reply_text = result["choices"][0].get("message", {}).get("content")

            if ai_reply_text:
                # ၂။ စာသားရပြီဖြစ်၍ ကောင်မလေး အသံသွင်းနေသလို ပြောင်းခြင်း
                await context.bot.send_chat_action(chat_id=chat_id, action="record_voice")

                # Step B: Google TTS သုံးပြီး ရလာသည့် မြန်မာစာသားကို အသံဖိုင်ပြောင်းခြင်း
                # lang='my' ဆိုသည်မှာ Myanmar (မြန်မာအသံ) ကို ပြောခြင်းဖြစ်သည်
                tts = gTTS(text=ai_reply_text, lang='my', slow=False)
                tts.save(audio_filename)

                # Step C: အသံဖိုင်ကို စာသား Caption နှင့်တွဲ၍ User (ကိုကို) ထံ ပစ်ပို့ခြင်း
                with open(audio_filename, "rb") as voice_file:
                    await update.message.reply_voice(
                        voice=voice_file,
                        caption=f"👩🏻‍💼: {ai_reply_text}"
                    )

                # ပို့ပြီးလျှင် ယာယီအသံဖိုင်အား ချက်ချင်းပြန်ဖျက်၍ Storage ရှင်းခြင်း
                if os.path.exists(audio_filename):
                    os.remove(audio_filename)
            else:
                await update.message.reply_text("⚠️ စိတ်မကောင်းပါဘူး ကိုကိုရယ်၊ ညီမလေး စကားလုံး ရှာမတွေ့လို့ပါ။")
        else:
            await update.message.reply_text(f"❌ API ချိတ်ဆက်မှု အဆင်မပြေပါ ကိုကို။ Code: {response.status_code}")
            
    except Exception as e:
        # Error တက်လျှင် ယာယီဖိုင် ကျန်မနေစေရန် ကာကွယ်ခြင်း
        if os.path.exists(audio_filename):
            os.remove(audio_filename)
        await update.message.reply_text(f"❌ Error ဖြစ်သွားလို့ပါ ကိုကို- {str(e)}")

# =====================================================================
# ၃။ ပရိုဂရမ် စတင်Runမည့်နေရာ
# =====================================================================
def main() -> None:
    # Flask Web Server ကို Background တွင် ပတ်ခြင်း (Render အပိတ်မခံရစေရန်)
    threading.Thread(target=run_flask, daemon=True).start()

    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    
    # ဝင်လာသမျှ စာသား (Text Chatting) များကို ဖမ်းယူရန်
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_burmese_girlfriend))

    print("Burmese AI Girlfriend Voice Bot Running smoothly on Render...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
