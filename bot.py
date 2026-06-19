import os
import sys
import asyncio
import threading
import requests
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# =====================================================================
# 🛠️ RENDER PORT BINDING ERROR FIX (FLASK WEB SERVER)
# =====================================================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "MLBB ID & Region Checker Bot is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host="0.0.0.0", port=port)

# =====================================================================
# Bot & RapidAPI Configuration
# =====================================================================
TOKEN = "8761954371:AAFJjatvSIsLuy6DHvSOlQ3koZ1LbDyNH3A"
bot = Bot(token=TOKEN)
dp = Dispatcher()

RAPID_URL = "https://mobile-legends-nickname-region-checker.p.rapidapi.com/mobile-legends"
HEADERS = {
    'Content-Type': 'application/json',
    'x-rapidapi-host': 'mobile-legends-nickname-region-checker.p.rapidapi.com',
    'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
}

# 1. /start Command (English Clean UI with HeinHtet Develop Credit)
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
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
    await message.reply(guide, parse_mode="Markdown")

# 2. MLBB Lookup Handler (Robust Key Parser Inside)
@dp.message(Command("ml"))
async def cmd_ml_check(message: types.Message):
    args = message.text.split()
    
    if len(args) < 3:
        await message.reply(
            "⚠️ **Invalid Format!**\n\n"
            "Please use: `/ml [User_ID] [Zone_ID]`\n"
            "Example: `/ml 114935204 2576`", 
            parse_mode="Markdown"
        )
        return
        
    user_id = args[1]
    zone_id = args[2]
    
    status_msg = await message.reply("⏳ *Fetching data from Moonton servers... Please wait.*", parse_mode="Markdown")

    payload = {
        "user_id": user_id,
        "zone_id": zone_id
    }

    try:
        response = requests.post(RAPID_URL, headers=HEADERS, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            # 🛡️ API တုံ့ပြန်မှု ပုံစံမျိုးစုံကို အကုန်လိုက်ဖတ်ပေးမည့်အပိုင်း
            nickname = result.get("nickname") or result.get("username") or result.get("name") or result.get("userName")
            region = result.get("region") or result.get("country") or result.get("zone_name") or result.get("zoneName")
            
            if not nickname and "data" in result and isinstance(result["data"], dict):
                inner_data = result["data"]
                nickname = inner_data.get("nickname") or inner_data.get("username") or inner_data.get("name") or inner_data.get("userName")
                region = inner_data.get("region") or inner_data.get("country") or inner_data.get("zone_name") or inner_data.get("zoneName")

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
            await status_msg.edit_text(cool_ui, parse_mode="Markdown")
        else:
            await status_msg.edit_text(
                f"❌ **API Request Failed!**\n\n"
                f"Status Code: `{response.status_code}`\n"
                "Please verify the User ID and Zone ID and try again.\n\n"
                "🛠️ `HeinHtet Develop`",
                parse_mode="Markdown"
            )
            
    except Exception as e:
        await status_msg.edit_text(f"❌ **Connection Error:** `{str(e)}` \n\n🛠️ `HeinHtet Develop`", parse_mode="Markdown")

# =====================================================================
# 3. Main Function to Run Server & Bot
# =====================================================================
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    print("MLBB Checker Bot is successfully running with HeinHtet Develop Credit...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot Stopped!")
