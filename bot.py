import telebot
import requests
from telebot import types

# ==================== [ CONFIGURATIONS ] ====================
BOT_TOKEN = "8702294693:AAHff0iYwzElcLNZzPhlXodImHePQuzYDl0
RAPIDAPI_URL = "https://girls-nude-image.p.rapidapi.com/"
RAPIDAPI_HOST = "girls-nude-image.p.rapidapi.com"
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
    
    # ခလုတ်နှိပ်လိုက်ရင် Loading လည်နေတာကို ပျောက်အောင် အရင်လုပ်ခြင်း
    bot.answer_callback_query(call.id, text="🔄 ပုံရှာနေပါပြီ...")
    
    # ဘာ Error တက်လဲ သိရအောင် စောင့်ကြည့်မည့် မက်ဆေ့ခ်ျ အရင်ပို့ထားမည်
    status_msg = bot.send_message(call.message.chat.id, "⏳ API ထံမှ ပုံဆွဲထုတ်နေဆဲ...")
    
    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    querystring = {"type": img_type}

    try:
        response = requests.get(RAPIDAPI_URL, headers=headers, params=querystring)
        
        # အကယ်၍ Subscribe မလုပ်ရသေးရင် သို့မဟုတ် Error တက်ရင် တန်းပြပေးရန်
        if response.status_code != 200:
            bot.edit_message_text(
                f"❌ API Error ဖြစ်သွားပါပြီ။\nStatus Code: {response.status_code}\nMessage: {response.text}",
                chat_id=call.message.chat.id,
                message_id=status_msg.message_id
            )
            return

        img_url = None
        raw_text = response.text.strip()

        # ၁။ API က JSON ပုံစံနဲ့ ပြန်ပေးခဲ့ရင် ဆွဲထုတ်နည်း
        try:
            result = response.json()
            img_url = result.get("url") or result.get("link") or result.get("image") or result.get("data")
        except Exception:
            # ၂။ JSON မဟုတ်ဘဲ ရိုးရိုး လင့်ခ်စာသား (Plain URL Text) သက်သက်ပဲ ပြန်ပေးခဲ့ရင်
            if raw_text.startswith("http://") or raw_text.startswith("https://"):
                img_url = raw_text

        # ဓာတ်ပုံလင့်ခ် ရပြီဆိုရင် ပို့ပေးမည်
        if img_url:
            # စောင့်ခိုင်းထားတဲ့ စာသားကို ဖြတ်လိုက်ခြင်း
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
                f"⚠️ ပုံလင့်ခ်ကို ခွဲထုတ်လို့ မရဖြစ်နေပါတယ်။\n**API ပြန်ပေးတဲ့စာသား:** `{raw_text[:300]}`",
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
    print("🤖 NSFW Image Bot စတင်ပွင့်နေပါပြီ...")
    bot.infinity_polling()
