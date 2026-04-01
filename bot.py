import os
import asyncio
import logging
import aiohttp
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
async def handle(request): return web.Response(text="TikTok Premium Bot is Online!")
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()

# --- FAST ASYNC API LOGIC ---
async def get_tiktok_data(url):
    api_url = f"https://www.tikwm.com/api/?url={url}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url, timeout=15) as response:
                res = await response.json()
                if res.get("code") == 0: return res["data"]
        except Exception as e:
            logging.error(f"API Error: {e}")
            return None
    return None

# --- PREMIUM BUTTONS ---
def premium_menu(v_id):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🎬 1080ᴘ ᴜʟᴛʀᴀ ʜᴅ", callback_data=f"q_1080_{v_id}"),
        types.InlineKeyboardButton(text="🎞️ 480ᴘ sᴛᴀɴᴅᴀʀᴅ", callback_data=f"q_480_{v_id}")
    )
    builder.row(types.InlineKeyboardButton(text="🎵 ᴅᴏᴡɴʟᴏᴀᴅ ᴍᴘ3 ᴀᴜᴅɪᴏ", callback_data=f"q_audio_{v_id}"))
    builder.row(types.InlineKeyboardButton(text="✨ sᴇᴀʀᴄʜ ᴀɢᴀɪɴ", callback_data="reset_search"))
    return builder.as_markup()

# --- HANDLERS ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome = (
        f"🌟 **ᴛɪᴋᴛᴏᴋ ᴘʀᴇᴍɪᴜᴍ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ** 🌟\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"ʜᴇʟʟᴏ **{message.from_user.first_name}**! 👋\n\n"
        f"💎 **ᴇxᴄʟᴜsɪᴠᴇ ғᴇᴀᴛᴜʀᴇs:**\n"
        f"╰┈➤ ɴᴏ ᴡᴀᴛᴇʀᴍᴀʀᴋ (ʜᴅ)\n"
        f"╰┈➤ ғᴀsᴛ ᴀᴘɪ ʀᴇsᴘᴏɴsᴇ\n\n"
        f"🔗 **ᴘᴀsᴛᴇ ʏᴏᴜʀ ʟɪɴᴋ ʙᴇʟᴏᴡ:**"
    )
    await message.answer(welcome, parse_mode="Markdown")

@dp.message(F.text.contains("tiktok.com"))
async def process_all_info(message: types.Message):
    wait_msg = await message.answer("💎 **ᴀɴᴀʟʏᴢɪɴɢ ʟɪɴᴋ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ**")
    
    data = await get_tiktok_data(message.text)
    
    if data:
        v_id = data['id']
        author = data['author']
        stats = data['stats']
        
        # Privacy & Status Icons
        is_private = "🔒 ᴘʀɪᴠᴀᴛᴇ" if author.get('private', False) else "🔓 ᴘᴜʙʟɪᴄ"
        is_verified = "👑 ᴠᴇʀɪғɪᴇᴅ" if author.get('verified', False) else "👤 ʀᴇɢᴜʟᴀʀ"
        
        info_text = (
            f"👤 **ᴀᴜᴛʜᴏʀ ᴘʀᴏғɪʟᴇ**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ **ɴᴀᴍᴇ:** {author['nickname']}\n"
            f"🛡️ **sᴛᴀᴛᴜs:** {is_verified}\n"
            f"📊 **sᴛᴀᴛɪsᴛɪᴄs:**\n"
            f"╰┈➤ ғᴏʟʟᴏᴡᴇʀs: **{author.get('followerCount', 0)}**\n"
            f"╰┈➤ ᴠɪᴅᴇᴏ ᴠɪᴇᴡs: **{stats.get('play_count', 0)}**\n\n"
            f"💎 **sᴇʟᴇᴄᴛ ʏᴏᴜʀ ǫᴜᴀʟɪᴛʏ:**"
        )
        
        # Link များကို Environment ထဲတွင် ယာယီသိမ်းခြင်း
        os.environ[f"vid_{v_id}"] = data['play']
        os.environ[f"sd_{v_id}"] = data.get('wmplay', data['play'])
        os.environ[f"aud_{v_id}"] = data['music']
        
        # Photo ပို့ပြီး UI ပြခြင်း
        await bot.send_photo(
            message.chat.id, 
            photo=author['avatar'], 
            caption=info_text, 
            parse_mode="Markdown",
            reply_markup=premium_menu(v_id)
        )
        await wait_msg.delete()
    else:
        await bot.edit_message_text("⚠️ **ᴇʀʀᴏʀ:** ᴜɴᴀʙʟᴇ ᴛᴏ ғᴇᴛᴄʜ ᴅᴀᴛᴀ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ!", 
                                    chat_id=message.chat.id, message_id=wait_msg.message_id)

@dp.callback_query(F.data.startswith("q_"))
async def download_logic(callback: types.CallbackQuery):
    _, quality, v_id = callback.data.split("_")
    await callback.answer(f"🚀 ᴜᴘʟᴏᴀᴅɪɴɢ {quality}...")

    url = os.environ.get(f"vid_{v_id}") if quality == "1080" else os.environ.get(f"sd_{v_id}")
    if quality == "audio": url = os.environ.get(f"aud_{v_id}")

    if url:
        # Bot ကိုယ်တိုင် Upload တင်ပေးခြင်း
        if quality == "audio":
            await bot.send_chat_action(callback.message.chat.id, "upload_document")
            await bot.send_audio(callback.message.chat.id, types.URLInputFile(url), caption="🎶 **ʜǫ ᴀᴜᴅɪᴏ sᴜᴄᴄᴇssғᴜʟʟʏ ᴇxᴛʀᴀᴄᴛᴇᴅ!**")
        else:
            await bot.send_chat_action(callback.message.chat.id, "upload_video")
            await bot.send_video(callback.message.chat.id, types.URLInputFile(url), caption=f"✅ **{quality}ᴘ ᴠɪᴅေᴏ ᴅᴇʟɪᴠᴇʀᴇᴅ!**")
    else:
        await callback.message.answer("❌ **ᴇʀʀᴏʀ:** ʟɪɴᴋ ᴇxᴘɪʀᴇᴅ. ᴘʟᴇᴀsᴇ sᴇɴᴅ ʟɪɴᴋ ᴀɢᴀɪɴ.")

@dp.callback_query(F.data == "reset_search")
async def reset(callback: types.CallbackQuery):
    await callback.message.answer("🔗 **ʀᴇᴀᴅʏ ғᴏʀ ɴᴇxᴛ ʟɪɴᴋ! sᴇɴဒ ɪᴛ ɴᴏᴡ.**")
    await callback.answer()

async def main():
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
