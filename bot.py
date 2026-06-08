import os
import time
import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# --- Configurations ---
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Target Asset URL
TARGET_URL = "https://akmcdn.ml.youngjoygame.com/predownload/PredownloadCombine_1173.1-1202.1_astc.zip"
OUTPUT_FILE = "MLBB_Patch.zip"

# Global System Flags
download_task = None
is_stopping = False

async def download_worker(chat_id: int, msg_id: int):
    """aiohttp ဖြင့် စစ်မှန်သော Non-blocking Async Stream ဖြင့် ဒေါင်းလုဒ်ဆွဲမည့် စနစ်"""
    global is_stopping
    is_stopping = False
    
    # 30-second connection timeout, 5-minute total timeout
    timeout = aiohttp.ClientTimeout(total=300, connect=30)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(TARGET_URL) as response:
                
                if response.status != 200:
                    await bot.edit_message_text(f"❌ **ERROR:** Gateway returned status `{response.status}`", chat_id, msg_id)
                    return

                # Total Size တွက်ချက်ခြင်း
                total_length = int(response.headers.get('Content-Length', 0))
                total_mb = round(total_length / (1024 * 1024), 2)
                downloaded = 0
                last_update_time = time.time()

                # Local File Storage Stream ဖွင့်ခြင်း
                with open(OUTPUT_FILE, 'wb') as f:
                    # Chunks များကို စနစ်တကျ Async ပုံစံဖြင့် ဖတ်ခြင်း
                    async for chunk in response.content.iter_chunked(1024 * 512): # 512KB Chunks
                        
                        # stop ဟု ရိုက်ပါက ချက်ချင်း Loop ဖြတ်ချမည်
                        if is_stopping:
                            await bot.edit_message_text("⏸️ **DOWNLOAD PROCESS FORCIBLY TERMINATED BY DOMINIC.**\n💾 *Local cluster logs flushed safely.*", chat_id, msg_id)
                            return
                        
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Rate Limiting: ၃.၅ စက္ကန့်ခြားမှ Telegram UI ကို Edit မည်
                            if time.time() - last_update_time > 3.5 or downloaded == total_length:
                                last_update_time = time.time()
                                
                                done = int(20 * downloaded / total_length)
                                current_mb = round(downloaded / (1024 * 1024), 2)
                                percentage = round((downloaded / total_length) * 100, 1)
                                
                                progress_bar = f"[{'▓' * done}{'░' * (20 - done)}]"
                                
                                ui_text = (
                                    "⚡ **PREMIUM ASYNC DOWNLOAD MATRIX**\n"
                                    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                    f"📦 **Object Target:** `{OUTPUT_FILE}`\n"
                                    f"📟 **Progress Core:** `{progress_bar}` `{percentage}%`\n"
                                    f"📊 **Data Transmitted:** `{current_mb} / {total_mb} MB`\n"
                                    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                    "🌌 *Status: STREAMING TARGET NODE*"
                                )
                                try:
                                    await bot.edit_message_text(ui_text, chat_id, msg_id, parse_mode="Markdown")
                                except Exception:
                                    pass
                                
                                # CPU Core ကို အသက်ရှူချောင်စေရန်
                                await asyncio.sleep(0.01)

                # ပြီးမြောက်သွားပါက အောင်မြင်ကြောင်း UI
                success_ui = (
                    "🏁 **DOWNLOAD PROCESS COMPLETED SUCCESSFULLY**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📦 **Saved Target:** `{OUTPUT_FILE}`\n"
                    f"📊 **Final Size:** `{total_mb} MB`\n"
                    f"🟢 **Status:** `FULLY INTEGRATED`\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🔥 *All network packets flushed safely by Dominic.*"
                )
                await bot.edit_message_text(success_ui, chat_id, msg_id, parse_mode="Markdown")

    except Exception as e:
        await bot.edit_message_text(f"⚠️ **NETWORK EXCEPTION:** `{str(e)}`", chat_id, msg_id)

# --- Chat Interface Commands ---

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(
        "⚡ **DOMINIC STANDALONE BOT CORE**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💬 **Available Text Signals:**\n"
        "➥ `download` - Execute async asset stream\n"
        "➥ `stop` - Terminate background loop safely\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📡 *Status: CORE ENGINE READY*", parse_mode="Markdown"
    )

@dp.message_handler(lambda message: message.text.lower() == 'download')
async def handle_download(message: types.Message):
    global download_task
    
    if download_task and not download_task.done():
        await message.answer("💡 **NOTICE:** A downloading process is already active inside the grid.")
        return
        
    init_msg = await message.answer("📡 **INITIALIZING ASYNC STREAM ENGINE...**")
    
    # Pure Async Background Task အဖြစ် Run သောကြောင့် လုံးဝ Crash မဖြစ်တော့ပါ
    download_task = asyncio.create_task(download_worker(message.chat.id, init_msg.message_id))

@dp.message_handler(lambda message: message.text.lower() == 'stop')
async def handle_stop(message: types.Message):
    global download_task, is_stopping
    
    if download_task and not download_task.done():
        is_stopping = True
        await message.answer("🛑 **DEPLOYING STOP SIGNAL...** Intercepting download worker thread.")
    else:
        await message.answer("💡 **NOTICE:** There are no active downloading nodes running right now.")

if __name__ == '__main__':
    print("Dominic's 100% Async Bot Core is Online.")
    executor.start_polling(dp, skip_updates=True)
