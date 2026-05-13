from flask import Flask
import requests
import os

app = Flask(__name__)

# --- Config ---
TOKEN = "YWMtOs1AxE6JEfGMQK35LXPHlwC3x2A3exHpkKgjudNTjb0ZQwwAzFsR8JWtDRpn0gquAwMAAAGeH7jqmTht7EDd_nns6iTySRbBrvMZueFVp-UzTJHDDF30mKnSJN8Oug"
ORG_APP = "1102190223222824/lit"
BASE_URL = f"http://a1-sgp-ga.easemob.com/{ORG_APP}"

def get_chat_names():
    url = f"{BASE_URL}/users/love144883120849408/contacts/users"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            users = data.get('data', [])
            return users
        return [f"Error: {response.status_code}"]
    except Exception as e:
        return [f"Exception: {str(e)}"]

@app.route('/')
def home():
    users = get_chat_names()
    
    # UI လေး နည်းနည်းလှအောင် လုပ်မယ်
    html = "🚀 <b>Dominic's Litmatch Scraper</b><br><hr>"
    html += f"📋 စုစုပေါင်း ရှာတွေ့သူ: {len(users)} ယောက်<br><br>"
    
    for i, user in enumerate(users, 1):
        name = user if isinstance(user, str) else user.get('nickname', 'Unknown')
        html += f"{i}။ 👤 Name: {name}<br>"
    
    return html

if __name__ == "__main__":
    # Render အတွက် Port ကို environment ကနေ ယူရပါမယ်
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
