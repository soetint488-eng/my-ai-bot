import os
import sys
import time
import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# --- Configurations ---
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Targets
TARGET_URL = "https://akmcdn.ml.youngjoygame.com/predownload/PredownloadCombine_1173.1-1202.1_astc.zip"
OUTPUT_FILE = "MLBB_Patch.zip"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Android; 13; MLBB)',
    'Accept': '*/*'
}

# Global Control Flags (ဒေါင်းလုဒ် အခြေအနေကို စောင့်ကြည့်ရန်)
download_task = None
is_stopping = False

async def download_worker(message: types.Message, msg_id: int):
    """ဒေါင်းလုဒ် ဆွဲပေးပြီး Telegram UI အား မွမ်းမံပေးမည့် Background Worker"""
    global is_stopping
    is_stopping = False
    
    try:
        # Blocking requests.get ကို non-blocking ဖြစ်အောင် Thread Pool ထဲတွင် Run ခြင်း
        loop = asyncio.get_event_loop()
        
        def fetch_stream():
            return requests.get(TARGET_URL, headers=HEADERS, stream=True, timeout=15)
            
        res = await loop.run_in_executor(None, fetch_stream)
        
        if res.status_code != 200:
            await bot.edit_message_text(f"❌ **ERROR:** Server rejected status `{res.status_code}`", message.chat.id, msg_id)
            return

        total_length = int(res.headers.get('content-length', 0))
        total_mb = round(total_length / (1024 * 1024), 2)
        downloaded = 0
        last_update_time = time.time()

        # အမှန်တကယ် ဖိုင်ထဲသို့ ရေးမည့် စနစ်
        with open(OUTPUT_FILE, 'wb') as f:
            # Chunk size ကို 256KB ထားပြီး ကွင်းဆက်ပတ်မည်
            for chunk in res.iter_content(chunk_size=1024 * 256):
                
                # ကိုကိုက stop ဟု ရိုက်လိုက်ပါက ဤနေရာတွင် ချက်ချင်း ဖြတ်ချမည်
                if is_stopping:
                    res.close()
                    await bot.edit_message_text("⏸️ **DOWNLOAD PROCESS FORCIBLY TERMINATED BY DOMINIC.**\n💾 *Cache registry cleared safely.*", message.chat.id, msg_id)
                    return
                
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Telegram Flooding ကာကွယ်ရန် ၃ စက္ကန့်ခြားမှတစ်ကြိမ် ပြင်မည်
                    if time.time() - last_update_time > 3.0 or downloaded == total_length:
                        last_update_time = time.time()
                        
                        done = int(20 * downloaded / total_length)
                        current_mb = round(downloaded / (1024 * 1024), 2)
                        percentage = round((downloaded / total_length) * 100, 1)
                        
                        progress_bar = f"[{'▓' * done}{'░' * (20 - done)}]"
                        
                        ui_text = (
                            "⚡ **PREMIUM LOCAL DOWNLOAD MATRIX**\n"
                            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"📦 **File:** `{OUTPUT_FILE}`\n"
                            f"📟 **Progress:** `{progress_bar}` `{percentage}%`\n"
                            f"📊 **Data Stream:** `{current_mb} / {total_mb} MB`\n"
                            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            "🌌 *Status: ACTIVE DOWNLOADING NODE*"
                        )
                        try:
                            await bot.edit_message_text(ui_text, message.chat.id, msg_id, parse_mode="Markdown")
                        except Exception:
                            pass
                        
                        # Async Loop ကို အသက်ရှူချောင်စေရန် ခဏလွှတ်ပေးခြင်း
                        await asyncio.sleep(0.01)

        # ပြီးမြောက်သွားပါက အောင်မြင်ကြောင်း UI တက်မည်
        success_ui = (
            "🏁 **DOWNLOAD PROCESS COMPLETED SUCCESSFULLY**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 **Saved Target:** `{OUTPUT_FILE}`\n"
            f"📊 **Total Size:** `{total_mb} MB`\n"
            f"🟢 **Status:** `FULLY SYNCED & INTEGRATED`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔥 *Process concluded cleanly by Dominic.*"
        )
        await bot.edit_message_text(success_ui, message.chat.id, msg_id, parse_mode="Markdown")

    except Exception as e:
        await bot.edit_message_text(f"⚠️ **RUNTIME EXCEPTION:** `{str(e)}`", message.chat.id, msg_id)

# --- Command Handlers ---

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(
        "⚡ **DOMINIC LOCAL DOWNLOAD CONTROLLER**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💬 **Available Text Commands:**\n"
        "➥ `download` - Start downloading asset file\n"
        "➥ `stop` - Force stop the current process\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📡 *Status: RUNNING LOCAL CORE*", parse_mode="Markdown"
    )

@dp.message_handler(lambda message: message.text.lower() == 'download')
async def handle_download(message: types.Message):
    global download_task
    
    # လက်ရှိ ဒေါင်းလက်စ ရှိမရှိ စစ်ဆေးခြင်း
    if download_task and not download_task.done():
        await message.answer("💡 **NOTICE:** A downloading process is already active inside the grid.")
        return
        
    init_msg = await message.answer("📡 **INITIALIZING LOCAL STREAM ENGINE...**")
    
    # Background Task အဖြစ် Run လိုက်ခြင်းကြောင့် Bot ကြီး ကြောင်မသွားဘဲ စာတွေကို ဆက်ဖတ်နိုင်မည်
    download_task = asyncio.create_task(download_worker(message, init_msg.message_id))

@dp.message_handler(lambda message: message.text.lower() == 'stop')
async def handle_stop(message: types.Message):
    global download_task, is_stopping
    
    if download_task and not download_task.done():
        is_stopping = True
        await message.answer("🛑 **DEPLOYING STOP SIGNAL...** Please wait for the loop to terminate safely.")
    else:
        await message.answer("💡 **NOTICE:** There are no active downloading nodes running right now.")

if __name__ == '__main__':
    print("Dominic's Standalone Bot Core is Online.")
    executor.start_polling(dp, skip_updates=True)
