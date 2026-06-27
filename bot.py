import telebot
import requests
from telebot import types

# သင်ပေးထားသော Bot Token
BOT_TOKEN = "8702294693:AAFQUh4aT3Wh5ur4XFxO5ftB_evXD_5MrFM"
bot = telebot.TeleBot(BOT_TOKEN)

# RapidAPI သော့ချက်များနှင့် အချက်အလက်များ
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"
RAPIDAPI_HOST = "nodress.p.rapidapi.com"

# အသုံးပြုသူများ၏ အသက်အတည်ပြုချက် အခြေအနေကို မှတ်သားရန် (In-memory Database)
verified_users = set()

def get_age_markup():
    """အသက် ၁၈ နှစ် ပြည့်/မပြည့် စစ်ဆေးသည့် Inline Keyboard ခလုတ်"""
    markup = types.InlineKeyboardMarkup()
    btn_yes = types.InlineKeyboardButton("✅ ဟုတ်ကဲ့၊ ကျွန်ုပ် အသက် ၁၈ နှစ်ပြည့်ပါပြီ", callback_data="age_verified")
    btn_no = types.InlineKeyboardButton("❌ မပြည့်သေးပါ", callback_data="age_failed")
    markup.add(btn_yes)
    markup.add(btn_no)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if user_id in verified_users:
        bot.reply_to(message, "👋 ကြိုဆိုပါတယ်။ သင်သည် အသက် ၁၈ နှစ်ပြည့်ပြီးသူ ဖြစ်၍ Bot ကို စတင်အသုံးပြုနိုင်ပါပြီ။")
    else:
        text = "⚠️ **သတိပေးချက်**\n\nဤ Bot တွင် ပါဝင်သောအကြောင်းအရာများသည် အသက် ၁၈ နှစ်ပြည့်ပြီးသူများသာ အသုံးပြုရန် ဖြစ်သည်။ ဆက်လက်အသုံးပြုရန် သင်၏ အသက်ကို အတည်ပြုပေးပါ။"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=get_age_markup())

@bot.callback_query_handler(func=lambda call: call.data.startswith("age_"))
def handle_age_verification(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if call.data == "age_verified":
        verified_users.add(user_id)
        # အဟောင်းစာသားနှင့် ခလုတ်ကို ဖျက်ပြီး အောင်မြင်ကြောင်းပြရန်
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, 
                              text="✅ အသက်အတည်ပြုခြင်း အောင်မြင်ပါသည်။ ယခုမှစ၍ Bot ကို အသုံးပြုနိုင်ပါပြီ။")
        
    elif call.data == "age_failed":
        if user_id in verified_users:
            verified_users.remove(user_id)
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, 
                              text="❌ စိတ်မကောင်းပါဘူး။ ဤ Bot အား အသက် ၁၈ နှစ်အောက် ကလေးသူငယ်များ အသုံးပြုခွင့် မရှိပါ။")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    
    # အသက်မပြည့်သေးလျှင် လုပ်ဆောင်ခွင့် မပေးဘဲ တားမြစ်ရန်
    if user_id not in verified_users:
        bot.reply_to(message, "⚠️ သင်သည် အသက် ၁၈ နှစ်ပြည့်ကြောင်း အတည်မပြုရသေးပါ။ ကျေးဇူးပြု၍ /start ကိုနှိပ်ပြီး အရင် အတည်ပြုပါ။")
        return

    # အသက်ပြည့်ပြီးပါက API ခေါ်ယူမည့် လုပ်ငန်းစဉ်ကို လုပ်ဆောင်ခြင်း
    bot.reply_to(message, "🔄 API သို့ ချိတ်ဆက်တောင်းဆိုနေပါသည်...")
    
    url = "https://nodress.p.rapidapi.com/image"
    querystring = {"DeepStrip": "Image"}
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        
        if response.status_code == 200:
            # API မှ ပြန်လာသော Data အပေါ်မူတည်၍ တုံ့ပြန်ပုံ ပြောင်းလဲနိုင်သည်
            bot.send_message(message.chat.id, f"✅ API တောင်းဆိုမှု အောင်မြင်ပါသည်။\nResponse: {response.text[:200]}")
        elif response.status_code == 403 or response.status_code == 404:
            bot.send_message(message.chat.id, "❌ ဤ API သည် RapidAPI ပေါ်တွင် ပိတ်ပင်ခံထားရခြင်း သို့မဟုတ် အလုပ်မလုပ်တော့ခြင်း ဖြစ်နိုင်ပါသည်။")
        else:
            bot.send_message(message.chat.id, f"⚠️ Error ဖြစ်ပွားခဲ့သည်။ Status Code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        bot.send_message(message.chat.id, f"❌ ချိတ်ဆက်မှု အမှားအယွင်း ဖြစ်ပွားခဲ့သည်- {str(e)}")

if __name__ == "__main__":
    print("Bot စတင်ပတ်မောင်းနေပါပြီ...")
    bot.infinity_polling()
