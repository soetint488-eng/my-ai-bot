import os
import asyncio
import logging
import openai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# --- CONFIG ---
# Telegram Bot Token ကိုတော့ ဒီမှာပဲ ထည့်ထားလို့ ရပါတယ်
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"

# OpenAI Key ကို Render ရဲ့ Environment Variables ထဲကနေ လှမ်းယူမယ်
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- RENDER PORT KEEP-ALIVE ---
async def handle(request): 
    return web.Response(text="ChatGPT Bot is Online and Secure!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()

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
    # API Key ရှိမရှိ အရင်စစ်မယ်
    if not OPENAI_API_KEY:
        await message.reply("❌ Error: OpenAI API Key ကို Render မှာ မထည့်ရသေးပါဘူးဗျ။")
        return

    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # OpenAI v0.28.1 ရဲ့ Asynchronous ခေါ်ဆိုမှု
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer in Myanmar language."},
                {"role": "user", "content": message.text}
            ]
        )
        
        ai_reply = response.choices[0].message.content
        await message.reply(ai_reply)
            
    except Exception as e:
        logging.error(f"OpenAI Error: {e}")
        error_msg = str(e)
        
        if "insufficient_quota" in error_msg:
            await message.reply("❌ **Error:** သင့် OpenAI အကောင့်မှာ Credit ကုန်နေပါပြီဗျ။")
        else:
            await message.reply(f"❌ **Error:**\n`{error_msg[:100]}`")

async def main():
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
