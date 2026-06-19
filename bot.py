import os
import sys
import threading
import requests
import telebot
from flask import Flask

# =====================================================================
# 🛠️ RENDER PORT BINDING ERROR FIX (FLASK WEB SERVER)
# =====================================================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "MLBB Telebot Checker is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host="0.0.0.0", port=port)

# =====================================================================
# Telegram Bot & RapidAPI Configuration (ပုံထဲကအတိုင်း ကွက်တိ)
# =====================================================================
BOT_TOKEN = "8761954371:AAFJjatvSIsLuy6DHvSOlQ3koZ1LbDyNH3A"
RAPIDAPI_KEY = "06b1562a59msh39810b847e9d0e2p151fd6jsn3a9d60ae50a9"
RAPIDAPI_HOST = "id-game-checker.p.rapidapi.com"

bot = telebot.TeleBot(BOT_TOKEN)

# =====================================================================
# API Function (ပုံထဲက အစ်ကို့ကုဒ်အတိုင်း ပြင်ဆင်ချက်လေးများဖြင့်)
# =====================================================================
def check_mlbb_id(user_id, zone_id):
    url = f"https://id-game-checker.p.rapidapi.com/mobile-legends/{user_id}/{zone_id}"
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None, f"API Error: {r.status_code}\n{r.text}"
        return r.json(), None
    except Exception as e:
        return None, str(e)

# =====================================================================
# Bot Handlers (telebot စနစ်)
# =====================================================================

# 1. /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    guide = (
        "⚔️ **Welcome to MLBB Player Checker Bot** ⚔️\n\n"
        "Easily find the Game Nickname and Region of any Mobile Legends account.\n\n"
        "🔍 **Format / Usage:**\n"
        "`/ml [User_ID] [Zone_ID]`\n\n"
        "💡 **Example:**\n"
        "`/ml 114935204 2576`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ **Powered by:** `HeinHtet Develop`"
    )
    bot.reply_to(message, guide, parse_mode="Markdown")

# 2. /ml command handler
@bot.message_handler(commands=['ml'])
def handle_ml_check(message):
    args = message.text.split()
    
    # Parameter စစ်ဆေးခြင်း
    if len(args) < 3:
        bot.reply_to(
            message,
            "⚠️ **Invalid Format!**\n\n"
            "Please use: `/ml [User_ID] [Zone_ID]`\n"
            "Example: `/ml 114935204 2576`",
            parse_mode="Markdown"
        )
        return
        
    user_id = args[1]
    zone_id = args[2]
    
    # Loading ပြသခြင်း
    status_msg = bot.reply_to(message, "⏳ *Fetching data from Moonton servers... Please wait.*", parse_mode="Markdown")
    
    # API သို့ လှမ်းခေါ်ခြင်း
    result, error = check_mlbb_id(user_id, zone_id)
    
    if error:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text=f"❌ **Error Occurred:** `{error}`\n\n🛠️ `HeinHtet Develop`",
            parse_mode="Markdown"
        )
        return
        
    if result:
        # Robust Key Parser (API က ကျလာသမျှ Nickname နဲ့ Region Key တွေကို dynamic ဖတ်ခြင်း)
        nickname = result.get("nickname") or result.get("username") or result.get("name") or result.get("userName")
        region = result.get("region") or result.get("country") or result.get("zone_name") or result.get("zoneName")
        
        # Nested Data ပါလာလျှင် ထပ်စစ်ခြင်း
        if not nickname and "data" in result and isinstance(result["data"], dict):
            inner = result["data"]
            nickname = inner.get("nickname") or inner.get("username") or inner.get("name") or inner.get("userName")
            region = inner.get("region") or inner.get("country") or inner.get("zone_name") or inner.get("zoneName")
            
        if not nickname:
            nickname = "Not Found / In-game Hidden"
        if not region:
            region = "International / Moonton Default"
            
        # ✨ UI Display with HeinHtet Develop Branding
        cool_ui = (
            "🎮 **MOBILE LEGENDS PLAYER PROFILE** 🎮\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 **Player Name :** `{nickname}`\n"
            f"🌐 **Region/Zone  :** `{region}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 **User ID :** `{user_id}`\n"
            f"📁 **Zone ID :** `{zone_id}`\n\n"
            "✨ *Status: Successfully Verified!*\n"
            "🛠️ *Developer:* `HeinHtet Develop`"
        )
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text=cool_ui,
            parse_mode="Markdown"
        )

# =====================================================================
# 3. Main Runner
# =====================================================================
if __name__ == "__main__":
    # Flask Server အား သီးသန့် Thread ဖြင့် အရင် Run ခြင်း (Render Port တက်အောင်)
    threading.Thread(target=run_flask, daemon=True).start()
    
    print("Telebot MLBB Checker with HeinHtet Develop Credit is Polling...")
    bot.infinity_polling()
