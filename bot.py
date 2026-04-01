import os
import asyncio
import logging
from openai import AsyncOpenAI
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# --- CONFIG ---
# သင့်ရဲ့ Telegram Bot Token
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
# သင့်ရဲ့ OpenAI API Key
OPENAI_API_KEY = "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"

# OpenAI Client Setup
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- RENDER PORT KEEP-ALIVE ---
async def handle(request): 
    return web.Response(text="OpenAI Bot is Online!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome = (
        f"🤖 **ᴄʜᴀᴛɢᴘᴛ ᴀɪ ᴀssɪsᴛᴀɴᴛ**\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"မင်္ဂလာပါ **{message.from_user.first_name}**! 👋\n\n"
        f"ကျွန်တော်က OpenAI ရဲ့ ChatGPT ဖြစ်ပါတယ်။ သိလိုသမျှကို "
        f"စာရိုက်ပြီး မေးမြန်းနိုင်ပါတယ်ဗျ။"
    )
    await message.answer(welcome, parse_mode="Markdown")

@dp.message(F.text)
async def ai_chat(message: types.Message):
    # Typing status ပြပေးမယ်
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # OpenAI ဆီက အဖြေတောင်းခြင်း
        response = await client.chat.completions.create(
            model="gpt-4o-mini", # စျေးသက်သာပြီး အဖြေမြန်တဲ့ model
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer in Myanmar language if possible."},
                {"role": "user", "content": message.text}
            ],
            max_tokens=1000
        )
        
        # အဖြေကို ပြန်ပို့ခြင်း
        ai_reply = response.choices[0].message.content
        await message.reply(ai_reply, parse_mode="Markdown")
            
    except Exception as e:
        logging.error(f"OpenAI Error: {e}")
        error_msg = str(e)
        
        # Error အလိုက် အသိပေးခြင်း
        if "insufficient_quota" in error_msg:
            await message.reply("❌ **Error:** သင့် OpenAI Key မှာ Credit မရှိတော့ပါဘူးဗျ။")
        elif "invalid_api_key" in error_msg:
            await message.reply("❌ **Error:** API Key မှားယွင်းနေပါတယ်ဗျ။")
        else:
            await message.reply(f"❌ **Error:**\n`{error_msg[:100]}`")

async def main():
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
