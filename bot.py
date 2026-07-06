import telebot
import requests
from urllib.parse import quote

# ကိုကို ပေးထားတဲ့ Bot Token
TOKEN = "8702294693:AAFQUh4aT3Wh5ur4XFxO5ftB_evXD_5MrFM"
bot = telebot.TeleBot(TOKEN)

# RapidAPI Credentials
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"
RAPIDAPI_HOST = "pornhub-video-download-api-search-stars-tags-categories.p.rapidapi.com"

# /start ပို့ရင် ပြန်မယ့်စာ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါဗျာ။ ပုံမှန်အချိန်မှာ အလိုအလျောက် Auto Rp ပြန်ပေးမှာဖြစ်ပြီး၊ တကယ်လို့ Pornhub ဗီဒီယိုလင့်ခ် လာပို့ရင် ဒေါင်းလုဒ်လင့်ခ် ထုတ်ပေးမှာ ဖြစ်ပါတယ်ဗျ။ ✨")

# စာလာသမျှကို ကိုင်တွယ်တဲ့အပိုင်း
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_text = message.text.strip()
    
    # အကယ်၍ လာပို့တဲ့စာက Pornhub လင့်ခ် ဖြစ်နေရင်
    if "pornhub.com" in user_text:
        bot.reply_to(message, "ခဏစောင့်ပေးပါဗျာ... ဒေါင်းလုဒ်လင့်ခ် ရှာပေးနေပါတယ်... ⏳")
        
        try:
            # 1. သုံးစွဲသူ ပို့လိုက်တဲ့ URL ကို API သုံးလို့ရအောင် Encode လုပ်တာပါ
            encoded_url = quote(user_text, safe='')
            
            # Link ထဲက viewkey ကို ဆွဲထုတ်ခြင်း (ဥပမာ- viewkey=67722348d1efb)
            viewkey = "default"
            if "viewkey=" in user_text:
                viewkey = user_text.split("viewkey=")[1].split("&")[0]

            # 2. API Endpoint တည်ဆောက်ခြင်း (Format ကို 240p အပြင် တခြားဟာလည်း ပြောင်းနိုင်ပါတယ်)
            api_url = f"https://{RAPIDAPI_HOST}/download_video/{viewkey}?url={encoded_url}&format=240"
            
            headers = {
                "Content-Type": "application/json",
                "x-rapidapi-host": RAPIDAPI_HOST,
                "x-rapidapi-key": RAPIDAPI_KEY
            }
            
            # 3. API ဆီ Request ပို့ခြင်း
            response = requests.get(api_url, headers=headers)
            data = response.json()
            
            # API က ပြန်ပေးတဲ့ Response ပုံစံပေါ်မူတည်ပြီး လင့်ခ်ကို ဆွဲထုတ်တာပါ
            # (မှတ်ချက်- API Response ရဲ့ Key နာမည်တွေက 'download_url' သို့မဟုတ် 'url' ဖြစ်တတ်ပါတယ်)
            download_link = data.get("download_url") or data.get("url") or data.get("link")
            video_title = data.get("title", "ဗီဒီယို")

            if download_link:
                reply_msg = f"🎬 **{video_title}**\n\n⬇️ **ဒေါင်းလုဒ်ဆွဲရန်လင့်ခ်:**\n{download_link}"
                bot.reply_to(message, reply_msg, parse_mode="Markdown")
            else:
                bot.reply_to(message, "စိတ်မရှိပါနဲ့ဗျာ၊ ဒီဗီဒီယိုအတွက် ဒေါင်းလုဒ်လင့်ခ် ရှာမတွေ့လို့ပါ သို့မဟုတ် API Limit ပြည့်သွားလို့ ဖြစ်နိုင်ပါတယ်ဗျ။")
                
        except Exception as e:
            print(f"Error: {e}")
            bot.reply_to(message, "လင့်ခ်ထုတ်ပေးရမှာ အမှားအယွင်းတစ်ခု ရှိသွားပါတယ်ဗျာ။")
            
    else:
        # Pornhub လင့်ခ် မဟုတ်ရင် ပုံမှန် မအားသေးတဲ့အကြောင်း Auto Rp ပြန်ပေးမှာပါ
        AUTO_REPLY_TEXT = "လူကြီးမင်းခင်ဗျာ... လက်ရှိမှာ ကိုကို လိုင်းမအားသေးလို့ပါဗျာ။ အရေးကြီးရင် စာချန်ထားခဲ့ပါ၊ လိုင်းတက်လာတာနဲ့ ချက်ချင်း ပြန်စာပို့ပေးပါ့မယ်။ 🙏✨"
        bot.reply_to(message, AUTO_REPLY_TEXT)

print("Bot စတင် အလုပ်လုပ်နေပါပြီ...")
bot.infinity_polling()
