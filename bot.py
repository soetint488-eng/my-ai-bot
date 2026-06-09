import telebot
import requests

# ==================== [ CONFIGURATIONS ] ====================
# BotFather ကပေးတဲ့ Bot Token တစ်ခုတည်းကိုပဲ ဒီမှာ ထည့်ပေးပါ
BOT_TOKEN = "သင့်ရဲ့_bot_token_ကို_ဒီမှာထည့်ပါ"

# RapidAPI Settings (အစ်ကိုပေးထားတဲ့ Keys များနှင့် အချက်အလက်များ)
RAPIDAPI_URL = "https://mobile-legends-nickname-region-checker.p.rapidapi.com/mobile-legends"
RAPIDAPI_KEY = "283b178159msh486932881be989fp157c27jsn617224a255da"
RAPIDAPI_HOST = "mobile-legends-nickname-region-checker.p.rapidapi.com"
# ============================================================

# Bot ကို Token တစ်ခုတည်းဖြင့် တည်ဆောက်ခြင်း
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_text = (
        "👋 မင်္ဂလာပါဗျာ! ကျွန်တော်ကတော့ MLBB Nickname Checker Bot ဖြစ်ပါတယ်။\n\n"
        "စစ်ဆေးလိုသော Player ID နှင့် Zone ID ကို အောက်ပါပုံစံအတိုင်း ရိုက်ပို့ပေးပါဗျာ။\n\n"
        "📌 ပုံစံ - `ID|Zone`\n"
        "📝 ဥပမာ - `114935204|2576`"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def check_mlbb_nickname(message):
    user_input = message.text.strip()
    
    # Input Format မှန်မမှန် စစ်ဆေးခြင်း
    if "|" not in user_input:
        bot.reply_to(message, "❌ ပုံစံမမှန်ကန်ပါ။ ကျေးဇူးပြု၍ `ID|Zone` ပုံစံအတိုင်း ပို့ပေးပါဗျာ။\nဥပမာ - `114935204|2576`")
        return

    # ID နှင့် Zone ခွဲထုတ်ခြင်း
    try:
        user_id, zone_id = user_input.split("|")
        user_id = user_id.strip()
        zone_id = zone_id.strip()
    except Exception:
        bot.reply_to(message, "❌ စာသားခွဲထုတ်ရာတွင် မှားယွင်းနေပါသည်။ `ID|Zone` ပုံစံကို သေချာပြန်စစ်ပေးပါ။")
        return

    # စောင့်ခိုင်းသည့် မက်ဆေ့ခ်ျ ပို့ခြင်း
    status_msg = bot.reply_to(message, "🔎 MLBB Nickname ကို လှမ်းစစ်ပေးနေပါပြီ။ ခေတ္တစောင့်ပါ...")

    # RapidAPI ထံ ပို့မည့် Headers နှင့် Payload Data
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
        # RapidAPI သို့ POST Request ပို့ခြင်း
        response = requests.post(RAPIDAPI_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            
            # API Response ထဲက ကျလာမည့် ဒေတာများကို ဆွဲထုတ်ခြင်း
            # API အလိုက် response key မတူနိုင်သဖြင့် စုံအောင် စစ်ထားပေးပါတယ်
            nickname = (result.get("nickname") or result.get("username") or 
                        result.get("name") or result.get("data", {}).get("username"))
            
            region = result.get("region") or result.get("zone") or result.get("country")

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
                # အကောင့် ရှာမတွေ့ခဲ့လျှင် သို့မဟုတ် API ဒေတာ ပုံစံပြောင်းနေလျှင် Raw response ပြပေးမည်
                bot.edit_message_text(f"⚠️ ရှာမတွေ့ပါ သို့မဟုတ် Response မမှန်ပါ။\n**API Return:** `{response.text}`", 
                                      chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text(f"❌ API Error ဖြစ်သွားပါပြီ။\nStatus Code: {response.status_code}\nMessage: {response.text}", 
                                  chat_id=message.chat.id, message_id=status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Error ဖြစ်ပွားသွားသည် - {str(e)}", chat_id=message.chat.id, message_id=status_msg.message_id)

if __name__ == "__main__":
    print("🤖 Telebot MLBB Checker Bot စတင်ပွင့်နေပါပြီ...")
    bot.infinity_polling()
