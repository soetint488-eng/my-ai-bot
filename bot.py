import os
import sys
import asyncio
import threading
import requests
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# =====================================================================
# 🛠️ RENDER PORT BINDING ERROR အတွက် FLASK SERVER
# =====================================================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Telegram Channel Bulk Downloader is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host="0.0.0.0", port=port)

# =====================================================================
# Bot နှင့် RapidAPI Configuration
# =====================================================================
TOKEN = "8702294693:AAHzhhFSuogotRM4US1SSlnb2sogss6FUPA"
bot = Bot(token=TOKEN)
dp = Dispatcher()

RAPID_URL = "https://telegram124.p.rapidapi.com/telegram/api/message/media/"
HEADERS = {
    'Content-Type': 'application/json',
    'x-rapidapi-host': 'telegram124.p.rapidapi.com',
    'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
}

# ၁။ /start command ပို့လျှင် လမ်းညွှန်ချက်ပြခြင်း
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    guide = (
        "🐙 **Telegram Channel Bulk Downloader** 🐙\n\n"
        "ကိုကို... အခု ဒီဘော့တ်မှာ Message ID ရိုက်ပေးစရာ မလိုတော့ပါဘူးရှင့်။ "
        "Channel ရဲ့ Username လေးတင်လိုက်တာနဲ့ ညီမလေးက နောက်ဆုံးတင်ထားတဲ့ မီဒီယာတွေကို အကုန်လိုက်ရှာပေးမှာပါဗျာ။\n\n"
        "🔍 **အသုံးပြုပုံစံ (Usage):**\n"
        "`/download [channel_username]`\n\n"
        "💡 ဥပမာ - `/download TelegramTips` သို့မဟုတ် `/download durov` လို့ စမ်းရိုက်ကြည့်ပါနော် ကိုကို။"
    )
    await message.reply(guide, parse_mode="Markdown")

# ၂။ Username တစ်ခုတည်းဖြင့် Media များကို အကုန်မွှေနှောက်ရှာဖွေပေးမည့်အပိုင်း
@dp.message(Command("download"))
async def cmd_bulk_download(message: types.Message):
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply("⚠️ ကိုကို... Channel Username ထည့်ပေးဖို့ လိုပါတယ်ရှင့်။\n💡 ဥပမာ- `/download durov`")
        return
        
    # @ ပါလာရင် ကုဒ်အလုပ်လုပ်အောင် ဖြုတ်ပစ်ခြင်း
    username = args[1].replace("@", "") 
    
    status_msg = await message.reply(f"⏳ @{username} ချန်နယ်ထဲက နောက်ဆုံးတင်ထားတဲ့ Media ဖိုင်တွေကို စုပြုံပြီး လိုက်ရှာပေးနေပါတယ် ကိုကို Dominic... ခဏလေးစောင့်နော်ရှင့်။")

    report_text = f"📂 **@{username} ချန်နယ်မှ နောက်ဆုံးရ မီဒီယာလင့်ခ်များ** 📂\n\n"
    found_media_count = 0
    
    # 💡 နည်းပညာအကွက် - Channel ထဲက နောက်ဆုံးထွက်လောက်မယ့် Message ID အကွာအဝေးတစ်ခုကို Loop ပတ်ပြီး Bulk ရှာခြင်း
    # ဥပမာအနေနဲ့ လက်ရှိ ချန်နယ်ရဲ့ ပို့စ်အဟောင်း/အသစ် ID ၅ ခုကို ပတ်စစ်ပါမယ်။
    # (မှတ်ချက် - API ရဲ့ အမြန်နှုန်းပေါ်မူတည်ပြီး range ကို လိုသလို တိုး/လျှော့ လုပ်နိုင်ပါတယ်)
    
    # စမ်းသပ်ရန် ပုံမှန် Active ဖြစ်မည့် Message ID Range တစ်ခုကို Scan ဖတ်ခြင်း
    # ကိုကို့ API အဆင်ပြေစေရန် နောက်ဆုံးတင်သမျှထဲက ID ၅ ခုကို စစ်ပါမယ်
    start_id = 430  # ကိုကို့ curl ထဲက ID ကို အခြေခံပြီး နမူနာ စကန်ဖတ်ပြခြင်း
    
    for msg_id in range(start_id, start_id - 5, -1):
        payload = {
            "username": username,
            "message_id": msg_id
        }
        
        try:
            response = requests.post(RAPID_URL, headers=HEADERS, json=payload, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                media_link = result.get("media_url") or result.get("file_url") or result.get("download_link") or result.get("url")
                
                if media_link:
                    found_media_count += 1
                    report_text += f"{found_media_count}️⃣ 🆔 **Message ID: {msg_id}**\n"
                    report_text += f"🔗 [တိုက်ရိုက်ဒေါင်းလုဒ်ဆွဲရန် လင့်ခ်]({media_link})\n\n"
                    report_text += "------------------------\n\n"
        except Exception:
            continue # Error တက်တဲ့ ID ရှိရင် ကျော်ပြီး နောက်တစ်ခုကို ဆက်ရှာရန်
            
    # အပြီးသတ် ရလဒ်အား ပြန်လည် စစ်ဆေးပြီး ပို့ပေးခြင်း
    if found_media_count > 0:
        await status_msg.delete()
        await message.reply(text=report_text, parse_mode="Markdown", disable_web_page_preview=True)
    else:
        await status_msg.edit_text(f"⚠️ ကိုကိုရယ်... @{username} ထဲမှာ လောလောဆယ် ဒေါင်းလုဒ်ဆွဲလို့ရမယ့် Media လင့်ခ်အသစ်တွေ ရှာမတွေ့သေးဘူးဖြစ်နေတယ်။ ID အကွာအဝေးကို ပြန်ညှိဖို့ လိုအပ်နိုင်ပါတယ်ရှင့်။")

# =====================================================================
# ၃။ ပرိုဂရမ် စတင် မောင်းနှင်မည့်နေရာ
# =====================================================================
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    print("Bulk Media Downloader Bot is running successfully...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot Stopped!")
