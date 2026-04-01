import os
import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# --- CONFIG ---
API_TOKEN = "8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# --- RENDER PORT KEEP-ALIVE ---
async def handle(request): return web.Response(text="TikTok HD Bot is Online!")
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()

# --- TIKTOK API LOGIC ---
def get_tiktok_data(url):
    api_url = f"https://www.tikwm.com/api/?url={url}"
    try:
        res = requests.get(api_url).json()
        if res.get("code") == 0: return res["data"]
    except: return None
    return None

# --- QUALITY SELECTION UI ---
def quality_menu(v_id):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🎬 1080p (Full HD)", callback_data=f"q_1080_{v_id}"))
    builder.row(types.InlineKeyboardButton(text="🎞️ 480p (Standard)", callback_data=f"q_480_{v_id}"))
    builder.row(types.InlineKeyboardButton(text="🎵 Download MP3", callback_data=f"q_audio_{v_id}"))
    return builder.as_markup()

# --- HANDLERS ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🚀 **TikTok HD Downloader**\n\nLink ပို့ပေးပါ၊ Quality ရွေးချယ်နိုင်ပါတယ်ဗျ။", parse_mode="Markdown")

@dp.message(F.text.contains("tiktok.com"))
async def process_link(message: types.Message):
    wait_msg = await message.answer("🔍 **Searching for high quality...**")
    data = get_tiktok_data(message.text)
    
    if data:
        v_id = data['id']
        # ယာယီသိမ်းဆည်းခြင်း
        os.environ[f"vid_{v_id}"] = data['play'] # HD/Original
        os.environ[f"sd_{v_id}"] = data.get('wmplay', data['play']) # Watermark ပါတဲ့ဟာ သို့မဟုတ် SD Link
        os.environ[f"aud_{v_id}"] = data['music']
        
        caption = f"📌 **Video Found!**\n\n👤 Author: {data['author']['nickname']}\nQuality ကို အောက်မှာ ရွေးချယ်ပါ 👇"
        await bot.send_photo(message.chat.id, photo=data['cover'], caption=caption, reply_markup=quality_menu(v_id))
        await wait_msg.delete()
    else:
        await message.answer("❌ ဗီဒီယို ရှာမတွေ့ပါဘူးဗျ။")

@dp.callback_query(F.data.startswith("q_"))
async def download_quality(callback: types.CallbackQuery):
    _, quality, v_id = callback.data.split("_")
    await callback.answer(f"⏳ {quality} ကို ပြင်ဆင်နေပါတယ်...")

    if quality == "1080":
        url = os.environ.get(f"vid_{v_id}")
        label = "✅ 1080p Full HD"
    elif quality == "480":
        url = os.environ.get(f"sd_{v_id}")
        label = "✅ 480p Standard"
    else: # Audio
        url = os.environ.get(f"aud_{v_id}")
        label = "🎶 High Quality MP3"

    if url:
        await bot.send_chat_action(callback.message.chat.id, "upload_video" if quality != "audio" else "upload_document")
        if quality == "audio":
            await bot.send_audio(callback.message.chat.id, types.URLInputFile(url), caption=label)
        else:
            await bot.send_video(callback.message.chat.id, types.URLInputFile(url), caption=label)
    else:
        await callback.message.answer("❌ Link Expired. Please resend the link.")

async def main():
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
