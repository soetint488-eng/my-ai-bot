import telebot
import requests
from telebot import types

# ==================== [ CONFIGURATIONS ] ====================
# အစ်ကို့ရဲ့ Telegram Bot Token
BOT_TOKEN = "8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk"

# API Configurations (အစ်ကိုပေးထားတဲ့ Keys များနှင့် အချက်အလက်များ)
RAPIDAPI_URL = "https://girls-nude-image.p.rapidapi.com/"
RAPIDAPI_HOST = "girls-nude-image.p.rapidapi.com"
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"
# ============================================================

bot = telebot.TeleBot(BOT_TOKEN)

# ခလုတ်များ ဖန်တီးပေးမည့် Function
def get_nsfw_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    # Callback Data သတ်မှတ်ပြီး ခလုတ်များ ပြုလုပ်ခြင်း
    btn1 = types.InlineKeyboardButton("🍒 Boobs", callback_data="nsfw_boobs")
    btn2 = types.InlineKeyboardButton("🍑 Ass", callback_data="nsfw_ass")
    markup.add(btn1, btn2)
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_text = (
        "🔞 **NSFW Image Bot မှ ကြိုဆိုပါတယ်** 🔞\n\n"
        "အောက်ပါ ခလုတ်များကို နှိပ်ပြီး သင်ကြည့်ရှုလိုသော ကျပန်း (Random) NSFW ရုပ်ပုံများကို တောင်းယူနိုင်ပါတယ်ဗျာ။"
    )
    bot.reply_to(message, welcome_text, reply_markup=get_nsfw_keyboard(), parse_mode="Markdown")

# Inline ခလုတ်နှိပ်ခြင်းကို ဖမ်းယူသည့် Handler
@bot.callback_query_handler(func=lambda call: call.data.startswith("nsfw_"))
def handle_nsfw_requests(call):
    # ခလုတ်အလိုက် ပုံစံခွဲခြားခြင်း (boobs သို့မဟုတ် ass)
    img_type = call.data.replace("nsfw_", "")
    
    # User ကို ခေတ္တစောင့်ရန် loading ပြခြင်း
    bot.answer_callback_query(call.id, text="🔄 ပုံဆွဲထုတ်နေပါတယ်... ခေတ္တစောင့်ပါ")
    
    # API တောင်းရန် ချက်ပြုတ်ခြင်း
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    querystring = {"type": img_type}

    try:
        # API ထံမှ GET Request ဖြင့် ဒေတာလှမ်းတောင်းခြင်း
        response = requests.get(RAPIDAPI_URL, headers=headers, params=querystring)
        
        if response.status_code == 200:
            result = response.json()
            
            # API က ပေးလေ့ရှိတဲ့ response format အလိုက် ရုပ်ပုံလင့်ခ်ကို ဆွဲထုတ်ခြင်း
            # ပုံမှန်အားဖြင့် 'url', 'image', 'link' သို့မဟုတ် 'data' အနေနဲ့ လာတတ်ပါတယ်
            img_url = result.get("url") or result.get("link") or result.get("image") or result.get("data")
            
            if img_url:
                # ဓာတ်ပုံကို Telegram ထံ တိုက်ရိုက်ပို့ခြင်း
                bot.send_photo(
                    chat_id=call.message.chat.id,
                    photo=img_url,
                    caption=f"🔞 Type: **{img_type.capitalize()}**",
                    reply_markup=get_nsfw_keyboard(), # ခလုတ်ကို အောက်မှာ ဆက်ပြထားပေးမည်
                    parse_mode="Markdown"
                )
            else:
                # ဒေတာရှိသော်လည်း ပုံလင့်ခ် ရှာမတွေ့လျှင် Raw text အဖြစ်ပြမည်
                bot.send_message(call.message.chat.id, f"⚠️ API Response မှ ရုပ်ပုံလင့်ခ် ရှာမတွေ့ပါ။\n**Return:** `{response.text}`")
        else:
            bot.send_message(call.message.chat.id, f"❌ API Error - Status Code: {response.status_code}\nMessage: {response.text}")
            
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Error တစ်ခုခု ဖြစ်ပွားသွားသည် - {str(e)}")

if __name__ == "__main__":
    print("🤖 NSFW Image Bot စတင်ပွင့်နေပါပြီ...")
    bot.infinity_polling()
