import telebot
import requests
import time
from telebot import types

# ==================== [ CONFIGURATIONS ] ====================
BOT_TOKEN = "8702294693:AAHff0iYwzElcLNZzPhlXodImHePQuzYDl0"

# URL ကို အနောက်က api/get-nude ဖြုတ်ပြီး Home URL အမှန်အတိုင်း ပြန်ပြင်ထားပါတယ်
RAPIDAPI_URL = "https://porn-image.p.rapidapi.com/"
RAPIDAPI_HOST = "porn-image.p.rapidapi.com"
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"
# ============================================================

bot = telebot.TeleBot(BOT_TOKEN)

def get_nsfw_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🍒 Boobs", callback_data="nsfw_boobs")
    btn2 = types.InlineKeyboardButton("🍑 Ass", callback_data="nsfw_ass")
    markup.add(btn1, btn2)
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_text = (
        "🔞 **NSFW Image Bot မှ ကြိုဆိုပါတယ်** 🔞\n\n"
        "အောက်ပါ ခလုတ်များကို နှိပ်ပြီး ပုံများကို တောင်းယူနိုင်ပါတယ်ဗျာ။"
    )
    bot.reply_to(message, welcome_text, reply_markup=get_nsfw_keyboard(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("nsfw_"))
def handle_nsfw_requests(call):
    img_type = call.data.replace("nsfw_", "")
    
    bot.answer_callback_query(call.id, text="🔄 ပုံရှာနေပါပြီ...")
    status_msg = bot.send_message(call.message.chat.id, "⏳ API ထံမှ ပုံဆွဲထုတ်နေဆဲ...")
    
    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    querystring = {"type": img_type}

    try:
        response = requests.get(RAPIDAPI_URL, headers=headers, params=querystring)
        
        if response.status_code != 200:
            bot.edit_message_text(
                f"❌ API Error ဖြစ်သွားပါပြီ။\nStatus Code: {response.status_code}\nMessage: {response.text}",
                chat_id=call.message.chat.id,
                message_id=status_msg.message_id
            )
            return

        result = response.json()
        img_url = result.get("url")

        if img_url:
            bot.delete_message(chat_id=call.message.chat.id, message_id=status_msg.message_id)
            
            bot.send_photo(
                chat_id=call.message.chat.id,
                photo=img_url,
                caption=f"🔞 Type: **{img_type.capitalize()}**",
                reply_markup=get_nsfw_keyboard(),
                parse_mode="Markdown"
            )
        else:
            bot.edit_message_text(
                f"⚠️ API အလုပ်လုပ်သော်လည်း JSON ထဲတွင် url ရှာမတွေ့ပါ။\n**API Return:** `{response.text}`",
                chat_id=call.message.chat.id,
                message_id=status_msg.message_id,
                parse_mode="Markdown"
            )
            
    except Exception as e:
        bot.edit_message_text(
            f"❌ Error ဖြစ်ပွားသွားသည် - {str(e)}",
            chat_id=call.message.chat.id,
            message_id=status_msg.message_id
        )

if __name__ == "__main__":
    print("🧹 Cleaning old bot connections...")
    bot.remove_webhook()
    time.sleep(1)
    
    print("🤖 NSFW Image Bot စတင်ပွင့်နေပါပြီ...")
    bot.infinity_polling(non_stop=True)
