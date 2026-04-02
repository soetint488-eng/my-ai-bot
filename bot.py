import os
import asyncio
import logging
import aiohttp
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# --- CONFIG ---
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
GROQ_API_KEY = "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"
BOT_NAME = "သားသား"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- RENDER PORT ALIVE ---
async def handle(request):
    return web.Response(text="သားသား Bot is running smoothly!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- AI RESPONSE FUNCTION ---
async def get_groq_response(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": f"မင်းနာမည်က {BOT_NAME} ဖြစ်ပါတယ်။ မင်းက အဖော်မွန်ကောင်းဖြစ်ပြီး ယဉ်ကျေးပျူငှာစွာ မြန်မာလို ပြန်ဖြေပေးရပါမယ်။"},
            {"role": "user", "content": user_text}
        ]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers, timeout=20) as resp:
            data = await resp.json()
            return data['choices'][0]['message']['content']

# --- AUTOMATION HANDLERS ---

# ၁။ ဆဲစာစစ်ခြင်း (Bad Words Filter)
BAD_WORDS = ["လီး", "စပ", "စောက်ပ", "တပတ်", "ဖာ"] # မောင်ထည့်ချင်တာ ထပ်ဖြည့်လို့ရတယ်

@dp.message(F.text)
async def main_handler(message: types.Message):
    text = message.text.lower()

    # (က) ဆဲစာစစ်မယ်
    if any(word in text for word in BAD_WORDS):
        try:
            await message.reply("သပ့နဲ့ တတ်ပွတ်လိုက်မယ်။ စကားကို ဆင်ခြင်ပြောပါဆို‌ နေမှပဲ🖕🏻🖕🏻။")
        except: pass
        return

    # (ခ) Link ဖျက်မယ် (Group ဖြစ်မှ)
    if message.chat.type in ["group", "supergroup"]:
        if re.search(r"http[s]?://", text) or ".com" in text:
            try:
                await message.delete()
                # await message.answer(f"@{message.from_user.username} လင့်ခ်ချလို့မရပါဘူးရှင့်။")
            except: pass
            return

    # (ဂ) AI Chat (သားသား လို့ပါမှ ဖြေမယ်)
    if BOT_NAME in text or message.chat.type == "private":
        await bot.send_chat_action(message.chat.id, "typing")
        try:
            # "သားသား" ဆိုတဲ့ စာလုံးကို ဖယ်ပြီးမှ AI ဆီ ပို့မယ်
            clean_text = text.replace(BOT_NAME, "").strip()
            reply = await get_groq_response(clean_text if clean_text else "နေကောင်းလား")
            await message.reply(reply)
        except Exception as e:
            await message.reply("❌ သားသား ခဏနားနေလို့ နောက်မှ ပြန်မေးပေးပါ ရှင့်။")

# --- STARTUP ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"🤖 ကျွန်တော့်နာမည် {BOT_NAME} ပါဗျ!\n\nGroup ထဲမှာ စကားပြောချင်ရင် '{BOT_NAME}' လို့ ထည့်ပြောပေးပါနော် ။")

async def main():
    server_task = asyncio.create_task(start_web_server())
    poll_task = asyncio.create_task(dp.start_polling(bot))
    await asyncio.gather(server_task, poll_task)

if __name__ == "__main__":
    asyncio.run(main())
