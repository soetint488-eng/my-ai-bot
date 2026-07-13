import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ၁။ Telegram Bot အချက်အလက်များ ဖြည့်ရန်
TOKEN = "8702294693:AAGyc787bFvYl5vvNJVajSE5cu5lYcgI_ok"
bot = telebot.TeleBot(TOKEN)

# ၂။ Slot API အချက်အလက်များ
SLOT_URL = "http://13.251.67.72:8865/api/Async/com.fsf.gfh.jhg"
HEADERS = {
    "Accept-Encoding": "identity",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 8.1.0; vivo 1807 Build/OPM1.171019.026)",
    "Connection": "keep-alive"
}

# Bot ဆီကို /start လို့ ပို့ရင် Button လေး ပြပေးမယ့်အပိုင်း
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # Button တည်ဆောက်ခြင်း
    markup = InlineKeyboardMarkup()
    check_btn = InlineKeyboardButton("Slot API စစ်မယ် 🎰", callback_data="check_api")
    markup.add(check_btn)
    
    welcome_text = "👋 မင်္ဂလာပါ၊ Slot API ကို စစ်ဆေးရန် အောက်က Button ကို နှိပ်ပါ။"
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# Button ကို နှိပ်လိုက်တဲ့အခါ အလုပ်လုပ်မယ့်အပိုင်း
@bot.callback_query_handler(func=lambda call: call.data == "check_api")
def callback_query(call):
    # လူက နှိပ်လိုက်တဲ့အချိန်မှာ 'ခဏစောင့်ပါ...' ဆိုပြီး Loading ပြပေးတာ
    bot.answer_callback_query(call.id, "Slot API ကို လှမ်းစစ်နေပါတယ်...")
    
    try:
        # Slot API ဆီ လှမ်းတောင်းခြင်း
        response = requests.get(SLOT_URL, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            message_text = f"🎰 **Slot API ရလဒ်** 🎰\n\n🟢 Status: အောင်မြင်သည်\n\n```json\n{data}\n```"
        else:
            message_text = f"⚠️ API စစ်ရတာ အဆင်မပြေပါ။ Error Code: {response.status_code}"
            
    except Exception as e:
        message_text = f"❌ Error ဖြစ်ပွားခဲ့သည်: {str(e)}"

    # Button ထပ်နှိပ်လို့ရအောင် Button အဟောင်းလေးပါ တစ်ပါတည်း ပြန်ထည့်ပေးထားခြင်း
    markup = InlineKeyboardMarkup()
    check_btn = InlineKeyboardButton("ထပ်မံစစ်ဆေးရန် 🔄", callback_data="check_api")
    markup.add(check_btn)

    # ရလဒ်ကို စာအသစ်မပို့ဘဲ မူလစာနေရာမှာတင် လဲလှယ် (Edit) ပြောင်းလဲပြသပေးခြင်း
    bot.edit_message_text(chat_id=call.message.chat.id, 
                          message_id=call.message.message_id, 
                          text=message_text, 
                          parse_mode="Markdown",
                          reply_markup=markup)

# Bot ကို တစ်ချိန်လုံး Run ထားခြင်း
if __name__ == "__main__":
    print("Button စနစ်သုံး Slot Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    bot.infinity_polling()
