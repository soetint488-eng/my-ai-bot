import logging
import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Configuration ---
API_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Android; 13; MLBB)',
    'Connection': 'keep-alive',
    'Accept': '*/*'
}

# --- Handlers ---

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📡 LAUNCH SYSTEM MATRIX", callback_data="run_scan"))
    
    welcome = (
        "⚡ **MLBB MULTI-SCANNER & IP CORE**\n"
        "🌌 *DEVELOPED BY DOMINIC*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Directly query Moonton's CDN cluster paths and network "
        "gateways to analyze resource status and host node IPs in real-time.\n\n"
        "🎯 Click below to execute automated thread query:",
        reply_markup=markup
    )
    await message.answer(welcome, parse_mode="Markdown")

@dp.callback_query_handler(text="run_scan")
async def run_multi_scan(callback_query: types.CallbackQuery):
    status_msg = await callback_query.message.edit_text("🛰 **INITIALIZING THREAD MATRIX ANALYSIS...**")
    
    # ၁။ IP Lookup Section (အသစ်ပေါင်းထည့်ထားသော Moonton IP Gateway စစ်ဆေးချက်)
    ip_url = "http://ip.ml.youngjoygame.com:30220/myip"
    detected_ip = "Unknown"
    ip_status = "🔴 OFFLINE"
    
    try:
        ip_res = requests.get(ip_url, headers=HEADERS, timeout=5)
        if ip_res.status_code == 200 and ip_res.text.strip():
            detected_ip = ip_res.text.strip()
            ip_status = "🟢 ACTIVE"
    except Exception:
        ip_status = "⚠️ GATEWAY TIMEOUT"

    # ၂။ Asset Cluster Targets Section
    targets = {
        "Magic Chess Mode": "res_version5/ChessPlayerRes/630.1/ModeSize.bytes",
        "Solo Offline Mode": "res_version5/SoloMode/114.1/ModeSize.bytes",
        "DisOrder (Overdrive)": "res_version5/DisOrderMode/458.1/ModeSize.bytes"
    }
    
    base_url = "https://akmcdn.ml.youngjoygame.com/"
    
    # UI Dashboard တည်ဆောက်ခြင်း
    report_text = (
        "🏁 **SYSTEM MATRIX ANALYSIS REPORT**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 **MOONTON IP GATEWAY:**\n"
        f"➥ Gateway Status: `{ip_status}`\n"
        f"➥ Host Node IP: `{detected_ip}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📦 **CDN ASSET REGISTRY STATUS:**\n\n"
    )
    
    for mode_name, path in targets.items():
        full_url = f"{base_url}{path}"
        try:
            res = requests.head(full_url, headers=HEADERS, timeout=5)
            if res.status_code == 200:
                size_kb = round(int(res.headers.get('Content-Length', 0)) / 1024, 2)
                report_text += f"🔷 **{mode_name}**\n   Status: `🟢 ONLINE`\n   Size: `{size_kb} KB`\n   Node: `{path.split('/')[-2]}`\n\n"
            else:
                report_text += f"🔷 **{mode_name}**\n   Status: `🔴 REJECTED ({res.status_code})`\n\n"
        except Exception:
            report_text += f"🔷 **{mode_name}**\n   Status: `⚠️ UNREACHABLE`\n\n"
            
        await asyncio.sleep(0.2) # Flood Protection Interval

    report_text += "━━━━━━━━━━━━━━━━━━━━━━━━\n🔥 *All queries flushed cleanly by Dominic.*"
    
    re_markup = InlineKeyboardMarkup()
    re_markup.add(InlineKeyboardButton("🔄 RE-RUN ANALYSIS", callback_data="run_scan"))
    
    await status_msg.edit_text(report_text, parse_mode="Markdown", reply_markup=re_markup)
    await callback_query.answer()

if __name__ == '__main__':
    print("Dominic's Integrated Multi-Scanner Core is Online.")
    executor.start_polling(dp, skip_updates=True)
