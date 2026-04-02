import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from duckduckgo_search import DDGS

# ၁။ Logging သတ်မှတ်ချက်
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ၂။ DuckDuckGo AI Function
def get_ai_response(user_text):
    try:
        # Render ပေါ်မှာဆိုရင် timeout ကို နည်းနည်း ပိုထားပေးရတယ်
        with DDGS() as ddgs:
            results = ddgs.chat(user_text, model='gpt-4o-mini')
            return results
    except Exception as e:
        return f"ခဏလေးနော် မောင်... DuckDuckGo ဘက်က အလုပ်မလုပ်လို့ပါ။ (Error: {str(e)})"

# ၃။ Message Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_input = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    ai_reply = get_ai_response(user_input)
    await update.message.reply_text(ai_reply)

# ၄။ Main Function
if __name__ == '__main__':
    TOKEN = '8463257017:AAHQH_bFCF1ENzJtwy_zswp1VywkofI4nA0' 
    
    # Render မှာ Error မတက်အောင် Application ကို သေချာ Build လုပ်မယ်
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Render ပေါ်မှာ Bot စတင်နေပါပြီ မောင်...")
    app.run_polling(drop_pending_updates=True)
