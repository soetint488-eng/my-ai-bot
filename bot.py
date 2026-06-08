import os
import requests
import time

# --- Configurations ---
# GitHub Secrets ထဲတွင် သေချာထည့်ပေးရမည့် အချက်အလက်များ
API_TOKEN = os.getenv('BOT_TOKEN', '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk')
# ကိုကို့ရဲ့ Telegram Chat ID (ကိုယ့်ဆီ စာတိုက်ရိုက်ရောက်လာရန်)
# @userinfobot ကနေ မိမိ ID ကို ယူပြီး ဒီမှာ ထည့်နိုင်ပါတယ် (ဥပမာ- 12345678)
CHAT_ID = os.getenv('CHAT_ID', '8584422107') 

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Android; 13; MLBB)',
    'Connection': 'keep-alive',
    'Accept': '*/*'
}

def send_telegram_report(text):
    """ရလာဒ်များကို Telegram ဆီသို့ Message လှမ်းပို့ခြင်း"""
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            print("🟢 Report transmitted to Telegram successfully.")
        else:
            print(f"❌ Failed to send message: {res.text}")
    except Exception as e:
        print(f"⚠️ Telegram Grid Error: {e}")

def run_matrix_scan():
    print("🛰️ INITIALIZING MOONTON CLUSTER SCAN...")
    
    # 1. Moonton IP Gateway Detection
    ip_url = "http://ip.ml.youngjoygame.com:30220/myip"
    detected_ip = "Unknown"
    ip_status = "🔴 OFFLINE"
    
    try:
        ip_res = requests.get(ip_url, headers=HEADERS, timeout=6, verify=False)
        if ip_res.status_code == 200 and ip_res.text.strip():
            detected_ip = ip_res.text.strip()
            ip_status = "🟢 ACTIVE"
    except Exception:
        ip_status = "⚠️ GATEWAY TIMEOUT"

    # 2. Asset Targets
    targets = {
        "Magic Chess Mode": "res_version5/ChessPlayerRes/630.1/ModeSize.bytes",
        "Solo Offline Mode": "res_version5/SoloMode/114.1/ModeSize.bytes",
        "DisOrder (Overdrive)": "res_version5/DisOrderMode/458.1/ModeSize.bytes"
    }
    
    base_url = "https://akmcdn.ml.youngjoygame.com/"
    
    report_text = (
        "🏁 **AUTOMATED SYSTEM MATRIX REPORT**\n"
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
            res = requests.head(full_url, headers=HEADERS, timeout=6, verify=False)
            if res.status_code == 200:
                size_kb = round(int(res.headers.get('Content-Length', 0)) / 1024, 2)
                report_text += f"🔷 **{mode_name}**\n   Status: `🟢 ONLINE`\n   Size: `{size_kb} KB`\n   Node: `{path.split('/')[-2]}`\n\n"
            else:
                report_text += f"🔷 **{mode_name}**\n   Status: `🔴 REJECTED ({res.status_code})`\n\n"
        except Exception:
            report_text += f"🔷 **{mode_name}**\n   Status: `⚠️ UNREACHABLE`\n\n"
            
        time.sleep(0.5)

    report_text += "━━━━━━━━━━━━━━━━━━━━━━━━\n🔥 *All automated loops flushed cleanly by Dominic.*"
    
    # Send directly to Dominic's chat
    send_telegram_report(report_text)

if __name__ == '__main__':
    run_matrix_scan()
