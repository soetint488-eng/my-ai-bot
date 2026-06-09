import telebot
import requests
import time
from telebot import types

# ==================== [ CONFIGURATIONS ] ====================
BOT_TOKEN = "8702294693:AAHff0iYwzElcLNZzPhlXodImHePQuzYDl0"

# အစ်ကိုပေးထားသော cURL အချက်အလက်များအတိုင်း ထည့်သွင်းထားပါသည်
RAPIDAPI_URL = "https://undress-strip-person.p.rapidapi.com/UndressImage"
RAPIDAPI_HOST = "undress-strip-person.p.rapidapi.com"
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"
# ============================================================

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_text = (
        "🤖 **Undress AI Bot မှ ကြိုဆိုပါတယ်**\n\n"
        "ကျွန်တော့်ဆီကို ပြုပြင်လိုတဲ့ ဓာတ်ပုံတစ်ပုံ ပို့ပေးလိုက်ပါဗျာ။"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    status_msg = bot.reply_to(message, "⏳ ဓာတ်ပုံဒေတာကို ရယူနေပါပြီ... ခေတ္တစောင့်ပါဗျာ။")
    
    try:
        # ၁။ Telegram Server မှ ဓာတ်ပုံဖိုင်လမ်းကြောင်းနှင့် Bytes ဒေတာကို ဆွဲထုတ်ခြင်း
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        telegram_img_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        
        bot.edit_message_text("🪄 AI စနစ်ဖြင့် ပုံကို ပြုပြင်နေပါပြီ... (စက္ကန့်အနည်းငယ် ကြာနိုင်ပါသည်)", chat_id=message.chat.id, message_id=status_msg.message_id)
        
        headers = {
            "x-rapidapi-host": RAPIDAPI_HOST,
            "x-rapidapi-key": RAPIDAPI_KEY
        }
        
        # နည်းလမ်း (၁) - အကယ်၍ API က ပုံလင့်ခ်ကိုပဲ တောင်းတာဆိုလျှင် (payload)
        payload = {
            "image": telegram_img_url
        }
        
        # နည်းလမ်း (၂) - အကယ်၍ API က ဖိုင်ကို တိုက်ရိုက်တောင်းတာဆိုလျှင် (files)
        files = {
            "image": ("image.jpg", downloaded_file, "image/jpeg")
        }
        
        # ပထမဦးစွာ ဖိုင်အလိုက် ပို့ကြည့်ပါမည် (ဒါက စိတ်အချရဆုံးမို့လို့ပါ)
        response = requests.post(RAPIDAPI_URL, headers=headers, data=payload, files=files)
        
        # အကယ်၍ error တက်ခဲ့ရင် ပုံလင့်ခ်တစ်ခုတည်းပဲ data အနေနဲ့ ပို့ကြည့်ပါမည်
        if response.status_code != 200:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            response = requests.post(RAPIDAPI_URL, headers=headers, data=payload)

        # ရလဒ် စစ်ဆေးခြင်း
        if response.status_code == 200:
            result = response.json()
            
            # API မှ ပြန်ပေးလေ့ရှိသော key နာမည်များအတိုင်း ရှာဖွေခြင်း
            ai_img_url = result.get("url") or result.get("image_url") or result.get("data", {}).get("url") or result.get("output")
            
            if ai_img_url:
                bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
                
                bot.send_photo(
                    chat_id=message.chat.id,
                    photo=ai_img_url,
                    caption="✨ **AI ပြုပြင်ပြီးသားပုံ ရပါပြီဗျာ။**",
                    reply_to_message_id=message.message_id
                )
            else:
                bot.edit_message_text(
                    f"⚠️ API အလုပ်လုပ်သော်လည်း ပုံလင့်ခ် ရှာမတွေ့ပါ။\n**Response:** `{response.text[:300]}`",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id
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
    
    print("🤖 Undress AI Bot စတင်ပွင့်နေပါပြီ...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5, allowed_updates=[], thread_pool_size=1)
