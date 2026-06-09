import telebot
import requests

# ==================== [ CONFIGURATIONS ] ====================
BOT_TOKEN = "8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk"

RAPIDAPI_URL = "https://mobile-legends-nickname-region-checker.p.rapidapi.com/mobile-legends"
RAPIDAPI_HOST = "mobile-legends-nickname-region-checker.p.rapidapi.com"
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"
# ============================================================

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_text = (
        "👋 မင်္ဂလာပါဗျာ! MLBB Nickname Checker Bot မှ ကြိုဆိုပါတယ်။\n\n"
        "စစ်ဆေးလိုသော Player ID နှင့် Zone ID ကို အောက်ပါပုံစံအတိုင်း ရိုက်ပို့ပေးပါဗျာ။\n\n"
        "📌 ပုံစံ - `ID|Zone`\n"
        "📝 ဥပမာ - `114935204|2576`"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def check_mlbb_nickname(message):
    user_input = message.text.strip()
    
    if "|" not in user_input:
        bot.reply_to(message, "❌ ပုံစံမမှန်ကန်ပါ။ ကျေးဇူးပြု၍ `ID|Zone` ပုံစံအတိုင်း ပို့ပေးပါဗျာ။\nဥပမာ - `114935204|2576`")
        return

    try:
        user_id, zone_id = user_input.split("|")
        user_id = user_id.strip()
        zone_id = zone_id.strip()
    except Exception:
        bot.reply_to(message, "❌ စာသားခွဲထုတ်ရာတွင် မှားယွင်းနေပါသည်။ `ID|Zone` ပုံစံကို သေჩာပြန်စစ်ပေးပါ။")
        return

    status_msg = bot.reply_to(message, "🔎 MLBB Nickname ကို လှမ်းစစ်ပေးနေပါပြီ။ ခေတ္တစောင့်ပါ...")

    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    
    payload = {
        "user_id": user_id,
        "zone_id": zone_id
    }

    try:
        response = requests.post(RAPIDAPI_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            
            # API Response Structure အသစ်အရ ဒေတာ ဆွဲထုတ်ခြင်း
            api_data = result.get("data", {})
            nickname = api_data.get("nickname")
            region = api_data.get("region")

            if nickname:
                response_text = (
                    "🎮 **MLBB Account Found!** 🎮\n"
                    "━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 **Nickname:** `{nickname}`\n"
                    f"🆔 **Player ID:** `{user_id}`\n"
                    f"🌐 **Zone ID:** `{zone_id}`\n"
                )
                if region:
                    response_text += f"📍 **Region:** `{region}`\n"
                response_text += "━━━━━━━━━━━━━━━━━━━"
                
                bot.edit_message_text(response_text, chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")
            else:
                bot.edit_message_text(f"⚠️ ရှာမတွေ့ပါ သို့မဟုတ် ဒေတာ ဆွဲမထုတ်နိုင်ပါ။\n**Response:** `{response.text}`", 
                                      chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text(f"❌ API Error ဖြစ်သွားပါပြီ။\nStatus Code: {response.status_code}\nMessage: {response.text}", 
                                  chat_id=message.chat.id, message_id=status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Error ဖြစ်ပွားသွားသည် - {str(e)}", chat_id=message.chat.id, message_id=status_msg.message_id)

if __name__ == "__main__":
    print("🤖 Telebot MLBB Checker Bot စတင်ပွင့်နေပါပြီ...")
    bot.infinity_polling()
