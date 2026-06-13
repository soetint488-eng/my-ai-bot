import os
import sys
import threading
import requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# =====================================================================
# 🛠️ RENDER PORT BINDING ERROR အတွက် FLASK SERVER
# =====================================================================
app = Flask(__name__)

@app.route('/')
def home():
    return "GitHub Stable Bot is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

# =====================================================================
# Tokens & API Configuration
# =====================================================================
TOKEN = "8702294693:AAHzhhFSuogotRM4US1SSlnb2sogss6FUPA"

# RapidAPI Settings
RAPID_URL = "https://github-profiles-trending-developers-repositories-scrapping.p.rapidapi.com/search"
HEADERS = {
    'Content-Type': 'application/json',
    'x-rapidapi-host': 'github-profiles-trending-developers-repositories-scrapping.p.rapidapi.com',
    'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
}

# =====================================================================
# ၁။ /start ခေါ်လျှင် Menu ချပြခြင်း
# =====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "🐙 **GitHub Data Portal (Stable Version) မှ ကြိုဆိုပါတယ် ကိုကို** 🐙\n\n"
        "RapidAPI ဆာဗာ Error တက်ခဲ့ရင်တောင် GitHub Official API နဲ့ပါ "
        "အလိုအလျောက် အစားထိုး ရှာဖွေပေးနိုင်အောင် အဆင့်မြှင့်ထားပါတယ်ရှင့်။\n\n"
        "👇 **ကိုကို ရှာဖွေလိုတဲ့ Category ကို အောက်မှာ ရွေးချယ်ပေးပါနော်-**"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎮 MLBB Mod / Skin Scripts", callback_data="app_mlbb_scripts")],
        [InlineKeyboardButton("📦 Python Tools (Market)", callback_data="app_python_market"),
         InlineKeyboardButton("💰 Premium/Sponsor Apps", callback_data="app_sponsorable")],
        [InlineKeyboardButton("🔥 Trending Python", callback_data="app_python_trending"),
         InlineKeyboardButton("🧑‍💻 Top GitHub Developers", callback_data="app_top_developers")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# =====================================================================
# ၂။ ဒေတာဆွဲထုတ်ပေးမည့်အပိုင်း (Error 500 ကျော်ဖြတ်ရန် Backup ပါဝင်သည်)
# =====================================================================
async def handle_menu_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    choice = query.data
    
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    status_msg = await query.message.reply_text("⏳ GitHub ဆာဗာထဲမှာ ဒေတာတွေကို မွှေနှောက်ရှာဖွေပေးနေပါတယ် ကိုကို...")

    # ခလုတ်အလိုက် ဒေတာများ ပြင်ဆင်ခြင်း
    target_url = ""
    github_official_api_url = "" # Backup အတွက် တရားဝင် API လမ်းကြောင်း
    title_header = "📦 GitHub Tools"

    if choice == "app_mlbb_scripts":
        target_url = "https://github.com/search?q=mobile+legends+script+OR+mlbb+mod&type=repositories&s=updated"
        github_official_api_url = "https://api.github.com/search/repositories?q=mobile+legends+script+OR+mlbb+mod&sort=updated&per_page=5"
        title_header = "🎮 MLBB Mod / Skin Scripts"
    elif choice == "app_python_market":
        target_url = "https://github.com/search?q=python&type=marketplace&query=is%3Asponsorable"
        github_official_api_url = "https://api.github.com/search/repositories?q=python+topic:marketplace&per_page=5"
        title_header = "📦 Python Tools (Marketplace)"
    elif choice == "app_python_trending":
        target_url = "https://github.com/trending/python"
        github_official_api_url = "https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc&per_page=5"
        title_header = "🔥 Trending Python Projects"
    elif choice == "app_sponsorable":
        target_url = "https://github.com/search?q=is%3Asponsorable&type=repositories"
        github_official_api_url = "https://api.github.com/search/repositories?q=stars:>1000&per_page=5"
        title_header = "💰 Premium / Sponsorable Projects"
    elif choice == "app_top_developers":
        target_url = "https://github.com/search?q=type%3Auser&type=users"
        github_official_api_url = "https://api.github.com/search/users?q=followers:>5000&per_page=5"
        title_header = "🧑‍💻 Top GitHub Developers"

    # Step A: 🛑 RapidAPI သို့ အရင်ပို့ကြည့်ခြင်း
    payload = {"url": target_url, "pageNumber": 1, "maxPage": 1, "cookies": []}
    
    try:
        response = requests.post(RAPID_URL, headers=HEADERS, json=payload, timeout=10)
        
        # အကယ်၍ ၅၀၀ မဟုတ်ဘဲ အောင်မြင်ခဲ့လျှင် ရလဒ်ထုတ်ပြမည်
        if response.status_code == 200:
            result = response.json()
            items = result.get("items") or result.get("results") or result.get("data")
            
            if items:
                report_text = f"✨ **{title_header} (Via RapidAPI Scraper)** ✨\n\n"
                for idx, item in enumerate(items[:5], 1):
                    name = item.get("name") or item.get("title") or "Unknown"
                    repo_url = item.get("url") or item.get("link") or "https://github.com"
                    desc = item.get("description") or "No description available."
                    report_text += f"{idx}. 🛠️ **{name}**\n📝 {desc}\n🔗 [ကြည့်ရန်လင့်ခ်]({repo_url})\n\n---\n\n"
                
                await status_msg.delete()
                await query.message.reply_text(text=report_text, parse_mode="Markdown", disable_web_page_preview=True)
                return

        # Step B: 🛡️ RapidAPI က Code 500 ပြန်လာလျှင် (သို့မဟုတ်) ပျက်နေလျှင် GitHub Official API ဘက်သို့ Auto ကူးပြောင်းခြင်း
        if github_official_api_url:
            backup_res = requests.get(github_official_api_url, timeout=10)
            
            if backup_res.status_code == 200:
                backup_data = backup_res.json()
                # GitHub official API က item တွေကို "items" key ထဲမှာ ပေးပါတယ်
                b_items = backup_data.get("items") or backup_data.get("incomplete_results") or []
                
                report_text = f"🛡️ **{title_header} (GitHub Official Live API)** 🛡️\n*(RapidAPI ဆာဗာ ခေတ္တမအားသဖြင့် Official API ဖြင့် ရှာပေးထားပါသည်)*\n\n"
                
                for idx, item in enumerate(b_items[:5], 1):
                    name = item.get("full_name") or item.get("login") or "Unknown Project"
                    repo_url = item.get("html_url") or "https://github.com"
                    desc = item.get("description") or "No bio/description available."
                    
                    report_text += f"{idx}. 🚀 **{name}**\n📝 {desc}\n🔗 [Source လင့်ခ်]({repo_url})\n\n---\n\n"
                
                await status_msg.delete()
                await query.message.reply_text(text=report_text, parse_mode="Markdown", disable_web_page_preview=True)
                return

        # တကယ်လို့ နှစ်ခုလုံးက ဘာမှ မထွက်လာခဲ့ရင်
        await status_msg.edit_text("⚠️ ကိုကိုရယ်... GitHub ဆာဗာနှစ်ခုလုံးက လက်ရှိ တုံ့ပြန်မှုမရှိပါဘူးရှင့်။ ခဏနေမှ ထပ်စမ်းကြည့်ပေးပါနော်။")

    except Exception as e:
        await status_msg.edit_text(f"❌ Error ဖြစ်သွားပါတယ် ကိုကို- {str(e)}")

def main() -> None:
    threading.Thread(target=run_flask, daemon=True).start()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_menu_click))
    print("Stable GitHub Bot with 500 Error Bypass is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
