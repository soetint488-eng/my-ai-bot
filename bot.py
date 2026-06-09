import telebot
import requests
import time
from telebot import types

# ==================== [ CONFIGURATIONS ] ====================
BOT_TOKEN = "8702294693:AAHff0iYwzElcLNZzPhlXodImHePQuzYDl0"

# အစ်ကိုပေးထားသော Face Pretty API အချက်အလက်များ
RAPIDAPI_URL = "https://photo-retouching.p.rapidapi.com/huoshan/facebody/facepretty"
RAPIDAPI_HOST = "photo-retouching.p.rapidapi.com"
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"
# ============================================================

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_text = (
        "✨ **AI Face Beauty Bot မှ ကြိုဆိုပါတယ်** ✨\n\n"
        "ကျွန်တော့်ဆီကို အလှပြင်လိုတဲ့ **လူပုံပါဝင်သော ဓာတ်ပုံတစ်ပုံ** ပို့ပေးလိုက်ပါဗျာ။ "
        "AI စနစ်ကနေ မျက်နှာကို အလိုအလျောက် ချောမွေ့လှပအောင် ပြုပြင်ပေးသွားမှာ ဖြစ်ပါတယ်!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# User ဆီမှ ဓာတ်ပုံလှမ်းဖမ်းသည့် Handler
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # အခြေအနေပြ စာသားအရင်ပို့ခြင်း
    status_msg = bot.reply_to(message, "⏳ ဓာတ်ပုံကို ရယူနေပါပြီ... ခေတ္တစောင့်ပါဗျာ။")
    
    try:
        # ၁။ Telegram Server ပေါ်မှ ပုံရဲ့ Direct URL လင့်ခ်ကို ဆွဲထုတ်ခြင်း
        file_info = bot.get_file(message.photo[-1].file_id)
        telegram_img_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        
        bot.edit_message_text("🪄 AI က မျက်နှာကို အလှပြင်ပေးနေပါပြီ...", chat_id=message.chat.id, message_id=status_msg.message_id)
        
        # ၂။ API သို့ ပေးပို့ရန် ချက်ပြုတ်ခြင်း (cURL အတိုင်း)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "x-rapidapi-host": RAPIDAPI_HOST,
            "x-rapidapi-key": RAPIDAPI_KEY
        }
        
        # User ပို့လိုက်တဲ့ ပုံလင့်ခ်ကို image_target ထဲ ထည့်လိုက်ခြင်း
        payload = {
            "image_target": telegram_img_url,
            "multi_face": "undefined",
            "beauty_level": 3 # အလှပြင်နှုန်းကို သိသာအောင် Level 3 အထိ မြှင့်ထားပေးပါတယ် (1-5 ကြိုက်သလိုပြောင်းနိုင်သည်)
        }
        
        # ၃။ API ထံ POST Request ဖြင့် ပို့ခြင်း
        response = requests.post(RAPIDAPI_URL, headers=headers, data=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # API က ပေးလေ့ရှိတဲ့ response json format အလိုက် ဆွဲထုတ်ခြင်း
            # (ပုံမှန်အားဖြင့် data သို့မဟုတ် result အောက်က url ထဲမှာ လင့်ခ်အသစ် လာတတ်ပါတယ်)
            data_obj = result.get("data", {})
            ai_img_url = data_obj.get("url") or result.get("url") or data_obj.get("image_url")
            
            if ai_img_url:
                # စောင့်ခိုင်းထားတဲ့ မက်ဆေ့ခ်ျကို ဖျက်ခြင်း
                bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
                
                # ပြင်ပြီးသား ပုံအသစ်ကို User ထံ ပြန်ပို့ပေးခြင်း
                bot.send_photo(
                    chat_id=message.chat.id,
                    photo=ai_img_url,
                    caption="✨ **AI နဲ့ အသားအရေ ချောမွေ့အောင် ပြင်ဆင်ပေးပြီးပါပြီဗျာ။** ✨",
                    reply_to_message_id=message.message_id,
                    parse_mode="Markdown"
                )
            else:
                bot.edit_message_text(
                    f"⚠️ API အလုပ်လုပ်သော်လည်း ပုံအသစ်လင့်ခ် ခွဲထုတ်မရပါ။\n**Response:** `{response.text[:300]}`",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    parse_mode="Markdown"
                )
        else:
            bot.edit_message_text(
                f"❌ API Error ဖြစ်သွားပါပြီ။\nStatus Code: {response.status_code}\nMessage: {response.text}",
                chat_id=message.chat.id,
                message_id=status_msg.message_id
            )
            
    except Exception as e:
        bot.edit_message_text(f"❌ Error ဖြစ်ပွားသွားသည် - {str(e)}", chat_id=message.chat.id, message_id=status_msg.message_id)

if __name__ == "__main__":
    print("🧹 Cleaning old bot connections...")
    bot.remove_webhook()
    time.sleep(1)
    
    print("🤖 AI Face Beauty Bot စတင်ပွင့်နေပါပြီ...")
    bot.infinity_polling()
