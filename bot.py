import os
import asyncio
import logging
import random
import string
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web, ClientSession

# --- CONFIG ---
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- UTILS ---
def generate_random_name(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# --- UI KEYBOARDS ---
def mail_menu(user, domain):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📥 Check Inbox", callback_data=f"check:{user}:{domain}"),
            InlineKeyboardButton(text="🔄 New Email", callback_data="gen_new")
        ],
        [
            InlineKeyboardButton(text="ℹ️ About TempMail", callback_data="about")
        ]
    ])

# --- RENDER PORT (Keep Alive) ---
async def handle(request): return web.Response(text="TempMail Bot is Running!")
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()

# --- HANDLERS ---

@dp.message(Command("start"))
@dp.callback_query(F.data == "gen_new")
async def start_and_gen(event):
    # Command ရော Callback ရော လက်ခံနိုင်အောင် event လို့ သုံးထားပါတယ်
    user = generate_random_name()
    domain = "1secmail.com"
    email = f"{user}@{domain}"
    
    text = (
        "📧 **Your Temporary Email is Ready!**\n\n"
        f"Address: `{email}`\n\n"
        "💡 **Note:** အပေါ်က Email ကို ဖိပြီး Copy ကူးယူနိုင်ပါတယ်။ "
        "OTP ဒါမှမဟုတ် Verification စာတွေ ဝင်လာရင် **Check Inbox** ကို နှိပ်ပြီး ကြည့်နိုင်ပါတယ်ဗျ။"
    )
    
    if isinstance(event, types.Message):
        await event.answer(text, reply_markup=mail_menu(user, domain), parse_mode="Markdown")
    else:
        await event.message.edit_text(text, reply_markup=mail_menu(user, domain), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("check:"))
async def check_inbox(callback: types.CallbackQuery):
    _, user, domain = callback.data.split(":")
    url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={user}&domain={domain}"
    
    async with ClientSession() as session:
        async with session.get(url) as resp:
            mails = await resp.json()
            
            if not mails:
                return await callback.answer("📭 စာအသစ် မရှိသေးပါဘူး။ ခဏနေမှ ပြန်စစ်ကြည့်ပါဦး။", show_alert=True)
            
            # နောက်ဆုံးဝင်တဲ့စာ (Index 0) ကို ယူခြင်း
            msg_id = mails[0]['id']
            msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={user}&domain={domain}&id={msg_id}"
            
            async with session.get(msg_url) as msg_resp:
                msg_data = await msg_resp.json()
                
                # စာသားကို သပ်သပ်ရပ်ရပ် ပြခြင်း
                inbox_text = (
                    "📩 **New Message Received!**\n\n"
                    f"👤 **From:** {msg_data['from']}\n"
                    f"📌 **Subject:** {msg_data['subject']}\n"
                    "━━━━━━━━━━━━━━━\n"
                    f"📝 **Content:**\n\n{msg_data['textBody'][:800]}"
                )
                await callback.message.answer(inbox_text, parse_mode="Markdown")
                await callback.answer("စာအသစ်ကို အောက်မှာ ကြည့်နိုင်ပါပြီ!")

@dp.callback_query(F.data == "about")
async def about_tool(callback: types.CallbackQuery):
    about_text = (
        "🛡️ **About Temporary Email**\n\n"
        "ဒီ Tool ဟာ သင့်ရဲ့ Real Email ကို မသုံးချင်တဲ့အခါ (ဥပမာ - Website တွေမှာ အကောင့်ဖွင့်စမ်းသပ်တာ) "
        "မှာ သုံးဖို့အတွက် ဖြစ်ပါတယ်။\n\n"
        "⚠️ **သတိပေးချက်:**\n"
        "ဒီ Email တွေဟာ ယာယီသာဖြစ်လို့ အရေးကြီးတဲ့ Banking အကောင့်တွေ၊ "
        "ဂိမ်းအကောင့်အစစ်တွေမှာ မသုံးပါနဲ့ဗျ။"
    )
    await callback.answer(about_text, show_alert=True)

async def main():
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
