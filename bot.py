import os
import sys
import threading
import requests
import base64
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# =====================================================================
# 🛠️ RENDER PORT BINDING ERROR အတွက် FLASK SERVER
# =====================================================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Edge TTS Bot is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

# =====================================================================
# Telegram Bot Token နှင့် API သတ်မှတ်ချက်များ
# =====================================================================
TOKEN = "8702294693:AAHzhhFSuogotRM4US1SSlnb2sogss6FUPA"

API_URL = "https://openai-whisper-text-to-speech.p.rapidapi.com/edgetts"
HEADERS = {
    'Content-Type': 'application/json',
    'x-rapidapi-host': 'openai-whisper-text-to-speech.p.rapidapi.com',
    'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "🎙️ **AI Text-to-Speech (Edge TTS) Bot** 🎙️\n\n"
        "သင်ရိုက်ပို့လိုက်သော စာသားများကို သဘာဝကျကျ အင်္ဂလိပ်လို ဖတ်ပြပေးမည့် Bot ဖြစ်ပါတယ်ဗျာ။\n\n"
        "📝 **အသုံးပြုနည်း-**\n"
        "အင်္ဂလိပ်လို စာသားတစ်ခုခု ရိုက်ပို့ပေးလိုက်ပါခင်ဗျာ။"
    )
    await update.message.reply_text(text=welcome_text, parse_mode="Markdown")

# =====================================================================
# 🔊 စာသားဝင်လာလျှင် အသံဖိုင်ပြောင်းလဲပြီး Voice Note ပြန်ပို့မည့်အပိုင်း
# =====================================================================
async def handle_tts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text.strip()
    chat_id = update.effective_chat.id
    
    # Bot က အသံဖိုင် သွင်းနေသလိုမျိုး Voice Status ပြထားခြင်း
    await context.bot.send_chat_action(chat_id=chat_id, action="record_voice")
    
    # curl ထဲကအတိုင်း payload ပြင်ဆင်ခြင်း
    payload = {
        "lang": "en-US-AriaNeural",
        "text": user_text
    }

    # ယာယီအသံဖိုင်အမည် သတ်မှတ်ခြင်း
    audio_filename = f"voice_{chat_id}.mp3"

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # 💡 API တည်ဆောက်ပုံအလိုက် အဖြေထုတ်နည်း (၂) မျိုးလုံးအတွက် ရေးထားပေးပါတယ်
            audio_url = result.get("audio_url") or result.get("url") or result.get("output")
            base64_data = result.get("base64") or result.get("audio_base64") or result.get("data")

            # ပုံစံ (၁) - အကယ်၍ API က Direct URL ပြန်ပေးလျှင်
            if audio_url:
                await update.message.reply_voice(voice=audio_url, caption="🗣️ AI Voice Generated!")
                
            # ပုံစံ (၂) - အကယ်၍ API က Base64 ဒေတာစစ်စစ် ပြန်ပေးလျှင် (Edge TTS API အများစု သုံးလေ့ရှိသည်)
            elif base64_data:
                # Base64 string အား binary ဖိုင်အဖြစ် ပြန်ပြောင်းပြီး စက်ထဲသိမ်းခြင်း
                if "base64," in base64_data:
                    base64_data = base64_data.split("base64,")[1]
                
                with open(audio_filename, "wb") as audio_file:
                    audio_file.write(base64.b64decode(base64_data))
                
                # အသံဖိုင်အား User ဆီ Voice Note အနေဖြင့် ပစ်ပို့ခြင်း
                with open(audio_filename, "rb") as voice_to_send:
                    await update.message.reply_voice(voice=voice_to_send, caption="🗣️ AI Voice Generated!")
                
                # ပို့ပြီးလျှင် ယာယီဖိုင်အား ပြန်ဖျက်ခြင်း
                if os.path.exists(audio_filename):
                    os.remove(audio_filename)
            else:
                await update.message.reply_text(f"⚠️ အသံဒေတာ ရှာမတွေ့ပါ။ API Response: {str(result)}")
        else:
            await update.message.reply_text(f"❌ API Error: Code {response.status_code}\n{response.text}")
            
    except Exception as e:
        if os.path.exists(audio_filename):
            os.remove(audio_filename)
        await update.message.reply_text(f"❌ ချိတ်ဆက်မှု အဆင်မပြေပါ- {str(e)}")

def main() -> None:
    threading.Thread(target=run_flask, daemon=True).start()

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tts))

    print("Edge TTS Voice Bot Running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
