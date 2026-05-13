import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# --- Config ---
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
# Dominic ပေးထားတဲ့ Token
LIT_TOKEN = "YWMtzPWP7E6iEfG34Kkt_SyshgC3x2A3exHpkKgjudNTjb0mnqlAcGcR8ItMGWYExFEOAwMAAAGeIGB_fjht7EDhriKvyK2dW2gm-zGLW7s4WZomlUCWd9pPsEcRmZprNw"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def get_account_data():
    # Token ထဲမှာ ပါလာနိုင်တဲ့ ဟာကွက်တွေကို ဖယ်ထုတ်ပါတယ်
    clean_token = LIT_TOKEN.strip()
    
    headers = {
        "Authorization": f"Bearer {clean_token}",
        "User-Agent": "Easemob-SDK(Android) 4.5.3",
        "Content-Type": "application/json",
        "Host": "a1-sgp-ga.easemob.com"
    }
    
    # ORG_APP ကို URL ထဲမှာ တန်းထည့်ထားပါတယ်
    url = "http://a1-sgp-ga.easemob.com/1102190223222824/lit/users/me"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json().get('entities', [{}])[0]
            return {
                "success": True,
                "name": data.get('nickname', 'N/A'),
                "id": data.get('username', 'N/A'),
                "diamonds": data.get('diamond', 0)
            }
        else:
            return {
                "success": False, 
                "error": response.status_code, 
                "msg": response.text[:100]
            }
    except Exception as e:
        return {"success": False, "error": "Connection", "msg": str(e)[:50]}

@dp.message_handler(commands=['start'])
async def cmd_start(m: types.Message):
    await m.answer("🔄 System Checking... အချက်အလက်များကို စစ်ဆေးနေပါသည်။")
    
    res = get_account_data()
    
    if res["success"]:
        text = (
            f"✅ **DATABASE CONNECTED**\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 **Nickname:** {res['name']}\n"
            f"🆔 **Username:** `{res['id']}`\n"
            f"💎 **Diamonds:** {res['diamonds']}\n"
            f"━━━━━━━━━━━━━━"
        )
    else:
        text = (
            f"❌ **CONNECTION FAILED**\n"
            f"━━━━━━━━━━━━━━\n"
            f"Status: `{res['error']}`\n"
            f"Response: `{res['msg']}`\n"
            f"━━━━━━━━━━━━━━"
        )
    
    await m.answer(text, parse_mode="Markdown")

if __name__ == '__main__':
    print("Dominic's Bot is Starting...")
    executor.start_polling(dp, skip_updates=True)
