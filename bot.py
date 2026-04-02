import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from duckduckgo_search import DDGS

# ၁။ Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ၂။ DuckDuckGo AI Function (Version အသစ် Syntax)
def get_ai_response(user_text):
    try:
        with DDGS() as ddgs:
            # Version အသစ်မှာ chat function ကို ဒီလို ခေါ်ရပါတယ်
            response = ddgs.chat(user_text, model='gpt-4o-mini')
            return response
    except Exception as e:
        # အကယ်၍ chat attribute မရှိဘူး ထပ်ပြနေရင် ဒီနည်းနဲ့ စမ်းကြည့်မယ်
        try:
            with DDGS() as ddgs:
                # model list ထဲက တစ်ခုခုနဲ့ စမ်းကြည့်တာပါ
                results = [r for r in ddgs.chat(user_text, model="gpt-4o-mini")]
                return "".join(results)
        except:
            return f"Error တက်နေတယ် မောင်: {str(e)}"

# ၃။ Message Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_input = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    ai_reply = get_ai_response(user_input)
    await update.message.reply_text(ai_reply)

# ၄။ Main
if __name__ == '__main__':
    TOKEN = '8463257017:AAHQH_bFCF1ENzJtwy_zswp1VywkofI4nA0' 
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot က Version အသစ်နဲ့ ပြန်စတင်နေပါပြီ မောင်...")
    app.run_polling(drop_pending_updates=True)
