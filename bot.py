import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from duckduckgo_search import DDGS

# ၁။ Bot ရဲ့ လုပ်ဆောင်ချက်တွေကို မှတ်တမ်းတင်ရန်
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ၂။ DuckDuckGo AI ဆီက အဖြေတောင်းတဲ့ Function
def get_ai_response(user_text):
    try:
        with DDGS() as ddgs:
            # GPT-4o-mini မော်ဒယ်ကို သုံးထားပါတယ် (အမြန်ဆုံးနဲ့ အခမဲ့ပါ)
            response = ddgs.chat(user_text, model='gpt-4o-mini')
            return response
    except Exception as e:
        # Error တက်ရင် လူလိုနားလည်အောင် ပြန်ပြောပေးမယ်
        return "ခဏလေးနော် မောင်... DuckDuckGo ဘက်က အလုပ်မလုပ်လို့ပါ။ ခဏနေမှ ပြန်မေးကြည့်ပါဦး။"

# ၃။ Message Handler (User ပို့တဲ့စာကို ကိုင်တွယ်ပုံ)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # စာသားမဟုတ်ရင် ဘာမှမလုပ်ဘူး
    if not update.message or not update.message.text:
        return
        
    user_input = update.message.text
    
    # Bot က စဉ်းစားနေတဲ့ပုံစံ (typing...) ပြမယ်
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # AI ဆီက အဖြေယူမယ်
    ai_reply = get_ai_response(user_input)
    
    # User ဆီ အဖြေပြန်ပို့မယ်
    await update.message.reply_text(ai_reply)

# ၄။ Main Function (Bot စတင်နှိုးဆော်ခြင်း)
if __name__ == '__main__':
    # မောင့်ရဲ့ Bot Token အသစ်
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI' 
    
    try:
        # Bot ကို တည်ဆောက်မယ်
        app = ApplicationBuilder().token(TOKEN).build()
        
        # စာသား Message တွေအတွက် Handler ထည့်မယ်
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("--- DuckDuckGo AI Bot စတင်နေပါပြီ မောင် ---")
        # Bot ကို အမြဲတမ်း အလုပ်လုပ်ခိုင်းထားမယ်
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"Bot စတင်ရတာ အဆင်မပြေဘူး မောင်: {e}")
