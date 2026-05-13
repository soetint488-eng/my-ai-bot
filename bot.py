import requests
import json

# --- Config ---
# ကိုကိုပေးထားတဲ့ Token ကို သုံးထားပါတယ်
TOKEN = "YWMtOs1AxE6JEfGMQK35LXPHlwC3x2A3exHpkKgjudNTjb0ZQwwAzFsR8JWtDRpn0gquAwMAAAGeH7jqmTht7EDd_nns6iTySRbBrvMZueFVp-UzTJHDDF30mKnSJN8Oug"
ORG_APP = "1102190223222824/lit"
BASE_URL = f"http://a1-sgp-ga.easemob.com/{ORG_APP}"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def get_recent_chat_names():
    print("📋 ကိုကိုနဲ့ စကားပြောဖူးသူများစာရင်းကို ရှာဖွေနေပါတယ်...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # စကားပြောထားတဲ့ Chat Sessions တွေကို ယူမယ့် API
    url = f"{BASE_URL}/chatmessages" # ဒါမှမဟုတ် /chatgroups/ ကို သုံးနိုင်ပါတယ်
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # အချက်အလက်တွေထဲက User နာမည်တွေကို ဆွဲထုတ်မယ်
            entities = data.get('entities', [])
            
            if not entities:
                print("⚠️ စကားပြောဖူးတဲ့သူ မတွေ့သေးဘူး ကိုကို။")
                return

            user_list = set() # နာမည်တွေ မထပ်အောင် set ကိုသုံးမယ်
            
            for entry in entities:
                # API Response ထဲက Nickname သို့မဟုတ် User ID ကို ယူမယ်
                name = entry.get('nickname') or entry.get('from')
                if name:
                    user_list.add(name)
            
            # စာရင်းကို နံပါတ်စဉ်နဲ့ ပြပေးမယ်
            for i, user_name in enumerate(user_list, 1):
                print(f"{i}။ 👤 Name: {user_name}")
                
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"✅ စုစုပေါင်း {len(user_list)} ယောက်ကို ရှာတွေ့ပါတယ် ကိုကို။")
            
        elif response.status_code == 401:
            print("❌ Token သက်တမ်းကုန်သွားပြီ ကိုကို။ Token အသစ်ပြန်ယူပေးပါ။")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ တစ်ခုခုမှားသွားတယ် ကိုကို: {e}")

if __name__ == "__main__":
    get_recent_chat_names()
