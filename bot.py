import os
import asyncio
import logging
import urllib.parse
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# --- CONFIG ---
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- UI ELEMENTS ---
def get_style_markup(prompt):
    # ပုံရဲ့ Style ကို ရွေးဖို့ ခလုတ်များ
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎨 Anime", callback_data=f"style:anime:{prompt}"),
            InlineKeyboardButton(text="📸 Realistic", callback_data=f"style:photorealistic:{prompt}")
        ],
        [
            InlineKeyboardButton(text="🎮 Cyberpunk", callback_data=f"style:cyberpunk:{prompt}"),
            InlineKeyboardButton(text="🖌️ 3D Render", callback_data=f"style:3d-render:{prompt}")
        ]
    ])
    return markup

# --- RENDER PORT ---
async def handle(request): return web.Response(text="UI Image Bot is Live!")
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
    welcome_text = (
        "✨ **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴀɪ ɪᴍᴀɢᴇ ɢᴇɴᴇʀᴀᴛᴏʀ** ✨\n\n"
        "ကျွန်တော်က သင်ဖြစ်ချင်တဲ့ ပုံရိပ်တွေကို ဖန်တီးပေးမယ့် AI ဖြစ်ပါတယ်။\n\n"
        "🎨 **ဘယ်လိုသုံးမလဲ?**\n"
        "သင်ဆွဲချင်တဲ့ ပုံအကြောင်းကို စာသား (English) နဲ့ ရိုက်ပို့လိုက်ရုံပါပဲဗျ။"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message(F.text)
async def handle_prompt(message: types.Message):
    if message.text.startswith('/'): return
    
    prompt = message.text
    await message.reply(
        f"🔍 **Prompt:** `{prompt}`\n\nဘယ်လို **Style** မျိုးနဲ့ ဆွဲချင်လဲ အောက်မှာ ရွေးပေးပါဦးဗျ 👇",
        reply_markup=get_style_markup(prompt),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("style:"))
async def process_style(callback: types.CallbackQuery):
    _, style, original_prompt = callback.data.split(":")
    
    # User ကို ခေတ္တစောင့်ခိုင်းခြင်း
    await callback.message.edit_text(f"⏳ **{style.upper()}** Style နဲ့ ပုံဖန်တီးနေပါပြီ... ခဏစောင့်ပေးပါဗျ။")
    await bot.send_chat_action(callback.message.chat.id, "upload_photo")

    try:
        # Style ကို Prompt ထဲပေါင်းထည့်ခြင်း
        final_prompt = f"{original_prompt}, {style} style, high quality, 4k"
        encoded_prompt = urllib.parse.quote(final_prompt)
        
        # Pollinations AI - Flux Model (အလန်းဆုံး Model)
        image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed=123&model=flux"

        await callback.message.delete() # အဟောင်းကိုဖျက်
        await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=image_url,
            caption=f"✅ **Generated!**\n🎨 **Style:** `{style}`\n📝 **Prompt:** `{original_prompt}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        await callback.message.answer("❌ Error: ပုံဆွဲလို့မရဖြစ်သွားပါတယ်ဗျ။")

async def main():
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
