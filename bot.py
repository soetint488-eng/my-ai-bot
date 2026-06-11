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
    return "ChatGPT Human-like Bot is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

# =====================================================================
# Telegram Bot Token နှင့် API သတ်မှတ်ချက်များ
# =====================================================================
TOKEN = "8702294693:AAHzhhFSuogotRM4US1SSlnb2sogss6FUPA"

API_URL = "https://chatgpt-42.p.rapidapi.com/conversationgpt4-2"
HEADERS = {
    'Content-Type': 'application/json',
    'x-rapidapi-host': 'chatgpt-42.p.rapidapi.com',
    'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "🤖 **ChatGPT AI Chatbot (Human-like) မှ ကြိုဆိုပါတယ်** 🤖\n\n"
        "ကျွန်တော့်ဆီကို သင်သိလိုသမျှ မေးခွန်းများကို စိတ်ကြိုက် မေးမြန်းနိုင်ပါတယ်ဗျာ။"
    )
    await update.message.reply_text(text=welcome_text, parse_mode="Markdown")

# =====================================================================
# 💬 User ပို့လာသော စာသားကို လူရိုက်သလို တစ်ဆင့်ချင်း ပြပေးမည့်အပိုင်း
# =====================================================================
async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text.strip()
    chat_id = update.effective_chat.id
    
    # ၁။ AI စဉ်းစားနေစဉ် "bot is typing..." အခြေအနေ ပြထားခြင်း
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    payload = {
        "messages": [{"role": "user", "content": user_message}],
        "system_prompt": "Reply to the user language naturally.",
        "temperature": 0.9,
        "top_k": 5,
        "top_p": 0.9,
        "max_tokens": 512,
        "web_access": False
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            ai_reply = result.get("result") or result.get("reply")
            
            if not ai_reply and "choices" in result and len(result["choices"]) > 0:
                ai_reply = result["choices"][0].get("message", {}).get("content")

            if ai_reply:
                # ✍️ ၂။ လူရိုက်သလို စာလုံးများကို တစ်ဆင့်ချင်း တိုးပြမည့် အပိုင်း
                current_text = ""
                # စာသားကို "..." ဟု အရင်ပို့ပြီး Message ID ကို ယူထားခြင်း
                typing_msg = await update.message.reply_text("⏳")
                
                # စာလုံးရေ ၅ လုံး သို့မဟုတ် ၁၀ လုံးစီ ဖြတ်ပြီး တဖြည်းဖြည်း ချပြမည်
                chunk_size = 10 
                
                for i in range(0, len(ai_reply), chunk_size):
                    # စာသားကို တဖြည်းဖြည်းချင်း ပေါင်းထည့်ခြင်း
                    current_text += ai_reply[i:i+chunk_size]
                    
                    try:
                        # ပို့ထားပြီးသား စာသားဟောင်းကို စာသားအသစ်ဖြင့် လှမ်းပြင် (Edit) ခြင်း
                        await context.bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=typing_msg.message_id,
                            text=current_text + " ✍️" # ရိုက်နေဆဲပုံစံ Icon ပြထားခြင်း
                        )
                        # တကယ့်လူ ရိုက်သလို ဖြစ်အောင် ၀.၃ စက္ကန့် ခဏနားခြင်း
                        await asyncio.sleep(0.3)
                        
                    except Exception:
                        # Telegram က ခဏခဏ edit လုပ်ရင် တားတတ်သဖြင့် Error တက်ပါက ကျော်ရန်
                        continue
                
                # ၃။ စာသားအားလုံး ပြီးသွားပါက နောက်ဆုံး ပုံစံအတိုင်း အပြီးသတ် ပြောင်းလဲခြင်း
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=typing_msg.message_id,
                    text=ai_reply
                )
            else:
                await update.message.reply_text(f"⚠️ AI ထံမှ အဖြေစာသား မထွက်လာပါ။")
        else:
            await update.message.reply_text(f"❌ API Error: Code {response.status_code}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ ချိတ်ဆက်မှု အဆင်မပြေပါ- {str(e)}")

def main() -> None:
    threading.Thread(target=run_flask, daemon=True).start()

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chat))

    print("ChatGPT Human-like Animation Bot Running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
