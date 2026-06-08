import os
import logging
import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Runtime Configuration ---
# GitHub Secrets ထဲတွင် BOT_TOKEN အဖြစ် သိမ်းဆည်းထားပါက ၎င်းကို အော်တိုဖတ်မည်။
# မရှိပါက အောက်ပါ Hardcoded Token အား အသုံးပြုမည်ဖြစ်သည်။
API_TOKEN = os.getenv('BOT_TOKEN', '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# HTTP Headers with Stream Keep-Alive Matrix
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
        "🎯 Click below to execute automated thread query:"
    )
    await message.answer(welcome, parse_mode="Markdown", reply_markup=markup)

@dp.callback_query_handler(text="run_scan")
async def run_multi_scan(callback_query: types.CallbackQuery):
    status_msg = await callback_query.message.edit_text("🛰 **INITIALIZING THREAD MATRIX ANALYSIS...**")
    
    # 1. Moonton IP Gateway Detection Target
    ip_url = "http://ip.ml.youngjoygame.com:30220/myip"
    detected_ip = "Unknown"
    ip_status = "🔴 OFFLINE"
    
    try:
        # verify=False ဖြင့် GitHub Environment အတွင်း SSL Handshake Error များအား ကျော်လွှားရန်
        ip_res = requests.get(ip_url, headers=HEADERS, timeout=5, verify=False)
        if ip_res.status_code == 200 and ip_res.text.strip():
            detected_ip = ip_res.text.strip()
            ip_status = "🟢 ACTIVE"
    except Exception:
        ip_status = "⚠️ GATEWAY TIMEOUT"

    # 2. Asset Cluster Target Routes
    targets = {
        "Magic Chess Mode": "res_version5/ChessPlayerRes/630.1/ModeSize.bytes",
        "Solo Offline Mode": "res_version5/SoloMode/114.1/ModeSize.bytes",
        "DisOrder (Overdrive)": "res_version5/DisOrderMode/458.1/ModeSize.bytes"
    }
    
    base_url = "https://akmcdn.ml.youngjoygame.com/"
    
    # Building Premium UI Dashboard Output
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
            # Check size and availability instantly using HEAD requests
            res = requests.head(full_url, headers=HEADERS, timeout=5, verify=False)
            if res.status_code == 200:
                size_kb = round(int(res.headers.get('Content-Length', 0)) / 1024, 2)
                report_text += f"🔷 **{mode_name}**\n   Status: `🟢 ONLINE`\n   Size: `{size_kb} KB`\n   Node: `{path.split('/')[-2]}`\n\n"
            else:
                report_text += f"🔷 **{mode_name}**\n   Status: `🔴 REJECTED ({res.status_code})`\n\n"
        except Exception:
            report_text += f"🔷 **{mode_name}**\n   Status: `⚠️ UNREACHABLE`\n\n"
            
        await asyncio.sleep(0.2) # Micro-interval to bypass cloud platform flood protection

    report_text += "━━━━━━━━━━━━━━━━━━━━━━━━\n🔥 *All queries flushed cleanly by Dominic.*"
    
    re_markup = InlineKeyboardMarkup()
    re_markup.add(InlineKeyboardButton("🔄 RE-RUN ANALYSIS", callback_data="run_scan"))
    
    await status_msg.edit_text(report_text, parse_mode="Markdown", reply_markup=re_markup)
    await callback_query.answer()

if __name__ == '__main__':
    print("Dominic's Integrated Multi-Scanner Core is Live inside the target Matrix.")
    executor.start_polling(dp, skip_updates=True)
