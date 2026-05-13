import os
import asyncio
import requests
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from flask import Flask
from threading import Thread

# --- Config ---
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
# Dominic အသစ်ကြည့်လာတဲ့ Token ကို ဒီမှာ သေချာထည့်ပေးပါ
LIT_TOKEN = "YWMtzPWP7E6iEfG34Kkt_SyshgC3x2A3exHpkKgjudNTjb0mnqlAcGcR8ItMGWYExFEOAwMAAAGeIGB_fjht7EDhriKvyK2dW2gm-zGLW7s4WZomlUCWd9pPsEcRmZprNw"
ORG_APP = "1102190223222824/lit"
BASE_URL = f"http://a1-sgp-ga.easemob.com/{ORG_APP}"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)

@app.route('/')
def home(): return "Account Diagnostic Online"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Deep Profile Fetching ---
def get_detailed_info():
    headers = {
        "Authorization": f"Bearer {LIT_TOKEN}",
        "User-Agent": "Easemob-SDK(Android) 4.5.3",
        "Accept-Encoding": "gzip"
    }
    
    info_data = {"status": "fail", "name": "N/A", "diamonds": "N/A", "id": "N/A"}
    
    try:
        # Method 1: Standard Easemob Me
        r1 = requests.get(f"{BASE_URL}/users/me", headers=headers, timeout=10)
        if r1.status_code == 200:
            res = r1.json().get('entities', [{}])[0]
            info_data["name"] = res.get('nickname', 'N/A')
            info_data["diamonds"] = res.get('diamond', 0)
            info_data["id"] = res.get('username', 'N/A')
            info_data["status"] = "success"
            
        # Method 2: Fallback to Profile API (If Diamond is 0/NA)
        if info_data["diamonds"] == 0 or info_data["diamonds"] == "N/A":
            r2 = requests.get("https://api.litatom.com/api/v1/users/profile/me", headers=headers, timeout=10)
            if r2.status_code == 200:
                res2 = r2.json().get('data', {})
                info_data["name"] = res2.get('nickname', info_data["name"])
                info_data["diamonds"] = res2.get('diamond_count', info_data["diamonds"])
                info_data["status"] = "success"

    except Exception as e:
        print(f"Connection Error: {e}")
        
    return info_data

# --- Handlers ---
@dp.message_handler(commands=['start'])
async def cmd_start(m: types.Message):
    await m.answer("🔍 စနစ်မှ အချက်အလက်များကို နက်နက်ရှိုင်းရှိုင်း စစ်ဆေးနေပါသည်။ ခေတ္တစောင့်ဆိုင်းပါ...")
    
    info = get_detailed_info()
    
    if info["status"] == "success":
        response_text = (
            f"📊 **ACCOUNT DIAGNOSTICS**\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 **Nickname:** {info['name']}\n"
            f"🆔 **User ID:** `{info['id']}`\n"
            f"💎 **Diamonds:** {info['diamonds']}\n"
            f"━━━━━━━━━━━━━━\n"
            f"✅ စနစ် ချိတ်ဆက်မှု အောင်မြင်ပါသည်။\n\n"
            f"စိန်စတင်ကောက်ရန်: /collect"
        )
    else:
        response_text = (
            f"❌ **အချက်အလက် ဆွဲယူ၍မရပါ။**\n\n"
            f"ဖြစ်နိုင်ခြေများ:\n"
            f"၁။ Token မှာ Space (သို့မဟုတ်) စာလုံးအမှား ပါနေခြင်း။\n"
            f"၂။ Network Connection အားနည်းခြင်း။\n"
            f"၃။ Litmatch ဘက်မှ API ပိတ်ထားခြင်း။"
        )
        
    await m.answer(response_text, parse_mode="Markdown")

if __name__ == '__main__':
    print("Dominic's Account Checker is booting up...")
    Thread(target=run_flask).start()
    executor.start_polling(dp, skip_updates=True)
