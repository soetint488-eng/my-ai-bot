import os
import time
import logging
import aiohttp
from aiogram import Bot, Dispatcher, executor, types

# 📝 Logging စနစ်ကို ဖွင့်ခြင်း (Render Log ထဲမှာ အမှားရှာရလွယ်ကူစေရန်)
logging.basicConfig(level=logging.INFO)

# 🔑 TELEGRAM BOT TOKEN သတ်မှတ်ခြင်း
# (Render ရဲ့ Environment Variables ထဲမှာ BOT_TOKEN ထည့်ထားရင် အလိုအလျောက်ဖတ်မည်၊ မရှိရင် အောက်ပါ String နေရာတွင် ထည့်ပါ)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")

# Bot နှင့် Dispatcher အား ကနဦးသတ်မှတ်ခြင်း
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 ၁။ START COMMAND HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    welcome_text = (
        "⚡ **MOONTON CORE NETWORK INJECTOR BOT**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 **Developer:** `Dominic`\n"
        "🟢 **Status:** `ONLINE (CLOUD ENVIRONMENT)`\n\n"
        "🛠 **ရရှိနိုင်သော စနစ်များနှင့် အသုံးပြုနည်းများ:**\n"
        "📡 ရိုက်ရန် -> `myip` : Moonton Gateway သို့ Keep-Alive ချိတ်ဆက်ပြီး Server IP နှင့် Ping ကို စစ်ဆေးမည်။\n"
        "🔍 ရိုက်ရန် -> `/find [Game_ID] [Server_ID]` : Moonton Database ဆီကနေ Player Nickname ကို လှမ်းဆွဲမည်။\n"
        "📊 ရိုက်ရန် -> `check_report` : Moonton Telemetry Port 30071 လိုင်းကို စမ်းသပ်မည်။\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🌌 *System stabilized and deployed under Dominic Matrix.*"
    )
    await message.answer(welcome_text, parse_mode="Markdown")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📡 ၂။ MOONTON KEEP-ALIVE IP & LATENCY SNIFFER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(lambda message: message.text.lower() == 'myip')
async def check_moonton_network(message: types.Message):
    init_msg = await message.answer("🛰️ **PINGING MOONTON NETWORK GATEWAY...**")
    
    url = "http://ip.ml.youngjoygame.com:30220/myip"
    RAW_HEADERS = {
        'Host': 'ip.ml.youngjoygame.com:30220',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Android; 13; MLBB)'
    }
    
    start_time = time.time()  # Latency စတင်မှတ်သားခြင်း
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=RAW_HEADERS, timeout=10) as response:
                
                # Response ရောက်ရန် ကြာမြင့်ချိန် (Latency) ကို မီလီစက္ကန့်ဖြင့် တွက်ခြင်း
                latency = round((time.time() - start_time) * 1000, 2)
                
                if response.status == 200:
                    raw_ip = await response.text()
                    
                    # Network Signal Level Logic
                    status_indicator = "🟢 EXCELLENT" if latency < 150 else "🟡 DELAYED"
                    
                    network_ui = (
                        "📡 **MOONTON LIVE CONNECTIVITY MATRIX**\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🌐 **Target Host:** `ip.ml.youngjoygame.com:30220`\n"
                        f"⚡ **Connection Type:** `HTTP/1.1 Keep-Alive`\n"
                        f"📟 **Detected Server IP:** `{raw_ip.strip()}`\n"
                        f"⏱️ **Network Latency:** `{latency} ms`\n"
                        f"📊 **Signal Status:** `{status_indicator}`\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "🌌 *Diagnostic concluded cleanly by Dominic.*"
                    )
                    await bot.edit_message_text(network_ui, message.chat.id, init_msg.message_id, parse_mode="Markdown")
                else:
                    await bot.edit_message_text(f"❌ **HANDSHAKE ERROR:** Server returned HTTP `{response.status}`", message.chat.id, init_msg.message_id)
                    
    except Exception as e:
        await bot.edit_message_text(f"⚠️ **SOCKET TIMEOUT:** Moonton core is unreachable.\n`Error: {str(e)}`", message.chat.id, init_msg.message_id)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎮 ၃။ MLBB PLAYER ID LOOKUP STALKER SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(commands=['find', 'stalk'])
async def stalk_mlbb_player(message: types.Message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer(
            "💡 **MLBB PLAYER RADAR SYSTEM**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📝 **အသုံးပြုနည်း:** `/find [Game_ID] [Server_ID]`\n"
            "🔍 **ဥပမာ:** `/find 28483292 2038`"
        )
        return

    game_id = args[1]
    server_id = args[2]
    
    init_msg = await message.answer("🛰️ **EXTRACTING DATA FROM MOONTON REGISTRY CORE...**")
    
    # 🌐 Public Free API End-point (Vanyastore API Gateway)
    url = f"https://api.vanyastore.com/v1/digital/mlbb?id={game_id}&zone={server_id}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=12) as response:
                if response.status == 200:
                    res_data = await response.json()
                    
                    if res_data.get('status') == 200 or 'data' in res_data:
                        player_data = res_data.get('data', res_data)
                        nickname = player_data.get('username') or player_data.get('name') or "Not Found"
                        
                        if nickname == "Not Found":
                            await bot.edit_message_text("❌ **ERROR:** Player ID မှားယွင်းနေပါသည်။", message.chat.id, init_msg.message_id)
                            return

                        profile_ui = (
                            "🎮 **MLBB ACQUIRED TARGET PROFILE**\n"
                            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"👤 **In-Game Nickname:** **{nickname}**\n"
                            f"🆔 **Player ID:** `{game_id}`\n"
                            f"🌐 **Server ID:** `{server_id}`\n"
                            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            "🟢 *Status: TARGET ACQUIRED CLEANLY*"
                        )
                        await bot.edit_message_text(profile_ui, message.chat.id, init_msg.message_id, parse_mode="Markdown")
                    else:
                        await bot.edit_message_text("❌ **ERROR:** ကစားသမား အချက်အလက် ရှာမတွေ့ပါ။", message.chat.id, init_msg.message_id)
                else:
                    await bot.edit_message_text(f"⚠️ **SERVER REJECTED:** Gateway returned HTTP `{response.status}`", message.chat.id, init_msg.message_id)
                    
    except Exception as e:
        await bot.edit_message_text(f"🛑 **DECRYPT ERROR:** API လိုင်းမကောင်းပါ သို့မဟုတ် Down နေပါသည်။", message.chat.id, init_msg.message_id)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 ၄။ MOONTON TELEMETRY PORT 30071 LOG CHECKER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dp.message_handler(lambda message: message.text.lower() == 'check_report')
async def test_moonton_report_node(message: types.Message):
    init_msg = await message.answer("🛰️ **CONNECTING TO MOONTON TELEMETRY REGISTRY...**")
    
    url = "https://report.ml.youngjoygame.com:30071"
    headers = {
        'Host': 'report.ml.youngjoygame.com:30071',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Android; 13; MLBB)'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                
                report_ui = (
                    "📡 **MOONTON LOG REPORTING PORTAL**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🌐 **Gateway Host:** `report.ml.youngjoygame.com`\n"
                    f"🔌 **Port Node:** `30071`\n"
                    f"📟 **HTTP Response Status:** `{response.status}`\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🟢 *Status: TELEMETRY NODE REACHABLE*"
                )
                await bot.edit_message_text(report_ui, message.chat.id, init_msg.message_id, parse_mode="Markdown")
                
    except Exception as e:
        await bot.edit_message_text(f"⚠️ **REPORT NODE TIMEOUT:**\n`Error: {str(e)}`", message.chat.id, init_msg.message_id)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚡ BOT ENGINE EXECUTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == '__main__':
    print("--- Dominic MLBB Cloud Bot Engine Started Successfully ---")
    executor.start_polling(dp, skip_updates=True)
