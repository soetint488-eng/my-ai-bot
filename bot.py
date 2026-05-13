import asyncio
import websockets
import json
import os

# --- Config ---
TOKEN = "YWMtOs1AxE6JEfGMQK35LXPHlwC3x2A3exHpkKgjudNTjb0ZQwwAzFsR8JWtDRpn0gquAwMAAAGeH7jqmTht7EDd_nns6iTySRbBrvMZueFVp-UzTJHDDF30mKnSJN8Oug"
# Render အတွက် wss (Secure Websocket) ကို သုံးတာ ပိုစိတ်ချရပါတယ်
MSYNC_URL = "wss://msync-im1-sgp-aws-ga.easemob.com:6717"

async def get_chat_list():
    print("🚀 [Render] Starting Litmatch Scraper...")
    
    try:
        # Render မှာ SSL Issue မတက်အောင် extra_headers နဲ့ ping ပို့တာမျိုး ထည့်ထားပါတယ်
        async with websockets.connect(MSYNC_URL, ping_interval=20, ping_timeout=20) as websocket:
            print("📡 Connected to MSYNC Server.")

            # Login Packet
            auth_packet = {
                "op": 1,
                "token": TOKEN,
                "appId": "1102190223222824#lit"
            }
            await websocket.send(json.dumps(auth_packet))
            print("🔑 Auth Packet Sent.")

            # စကားပြောဖူးသူစာရင်းကို စောင့်ဖတ်မယ့် loop
            while True:
                try:
                    response = await websocket.recv()
                    data = json.loads(response)
                    
                    # နာမည်စာရင်း ဒါမှမဟုတ် ID ပါလာရင် Log မှာ ထုတ်ပြမယ်
                    if "from" in data:
                        user_name = data.get('from')
                        print(f"👤 Found Chat User: {user_name}")
                    
                except websockets.exceptions.ConnectionClosed:
                    print("⚠️ Connection closed by server. Retrying...")
                    break
                except Exception as e:
                    print(f"⚠️ Data Error: {e}")
                    
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    # Render မှာ Port error မတက်အောင် Dummy server အသေးစားလေး လိုအပ်နိုင်ပါတယ်
    # ဒါပေမဲ့ Background Worker အနေနဲ့ဆိုရင်တော့ ဒီအတိုင်း Run လို့ရပါတယ်
    asyncio.run(get_chat_list())
