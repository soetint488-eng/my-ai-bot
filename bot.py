import telebot
import requests
import time
from telebot import types

# ==================== [ CONFIGURATIONS ] ====================
BOT_TOKEN = "8702294693:AAHff0iYwzElcLNZzPhlXodImHePQuzYDl0"

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

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    status_msg = bot.reply_to(message, "⏳ ဓာတ်ပုံဒေတာကို ရယူနေပါပြီ... ခေတ္တစောင့်ပါဗျာ။")
    
    try:
        # ၁။ Telegram Server မှ ဓာတ်ပုံဖိုင်ကို Bytes အဖြစ် တိုက်ရိုက်ဒေါင်းလုဒ်ဆွဲခြင်း
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        bot.edit_message_text("🪄 AI က မျက်နှာကို အလှပြင်ပေးနေပါပြီ...", chat_id=message.chat.id, message_id=status_msg.message_id)
        
        # ၂။ API သို့ လင့်ခ်အစား ဖိုင်အဖြစ် ပို့ရန် headers ကို ပြင်ဆင်ခြင်း
        # Content-Type ကို requests က အလိုအလျောက် သတ်မှတ်ပေးရန် ဖြုတ်ထားရပါမည်
        headers = {
            "x-rapidapi-host": RAPIDAPI_HOST,
            "x-rapidapi-key": RAPIDAPI_KEY
        }
        
        # ဓာတ်ပုံဖိုင်ဒေတာကို image_target ထဲသို့ ထည့်ခြင်း
        files = {
            "image_target": ("image.jpg", downloaded_file, "image/jpeg")
        }
        
        # အခြား Parameter များကို data ထဲတွင် ပို့ခြင်း
        payload = {
            "multi_face": "undefined",
            "beauty_level": "3" # String ပုံစံဖြင့် လွှဲပေးလိုက်ပါသည်
        }
        
        # ၃။ API ထံ POST Request ဖြင့် ဖိုင်ကိုပါ ပူးတွဲပို့ခြင်း
        response = requests.post(RAPIDAPI_URL, headers=headers, data=payload, files=files)
        
        if response.status_code == 200:
            result = response.json()
            
            # API ရဲ့ JSON Format အလိုက် ပုံလင့်ခ်အသစ် ဆွဲထုတ်ခြင်း
            data_obj = result.get("data", {})
            ai_img_url = data_obj.get("url") or result.get("url") or data_obj.get("image_url")
            
            if ai_img_url:
                bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
                
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
    time.sleep(2)
    
    print("🤖 AI Face Beauty Bot စတင်ပွင့်နေပါပြီ...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5, allowed_updates=[], thread_pool_size=1)
