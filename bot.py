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
    return "GitHub Menu Bot is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

# =====================================================================
# Tokens & API Configuration
# =====================================================================
TOKEN = "8702294693:AAHzhhFSuogotRM4US1SSlnb2sogss6FUPA"

API_URL = "https://github-profiles-trending-developers-repositories-scrapping.p.rapidapi.com/search"
HEADERS = {
    'Content-Type': 'application/json',
    'x-rapidapi-host': 'github-profiles-trending-developers-repositories-scrapping.p.rapidapi.com',
    'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
}

# =====================================================================
# ၁။ /start နှိပ်လိုက်တာနဲ့ ရရှိနိုင်မည့် App/Project ဒေတာအမျိုးအစားအားလုံး ချပြခြင်း
# =====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "🐙 **GitHub Data Scraper Portal မှ ကြိုဆိုပါတယ် ကိုကို** 🐙\n\n"
        "ဒီ Bot ကြီးကနေ GitHub ပေါ်က ခေတ်အဆုံးဆုံး App တွေ၊ Repositories တွေနဲ့ "
        "Developer တွေရဲ့ အချက်အလက်တွေကို တိုက်ရိုက် ဆွဲထုတ်ပေးနိုင်ပါတယ်ရှင့်။\n\n"
        "👇 **ကိုကို သိလိုတဲ့ App/Project အမျိုးအစားကို အောက်က ခလုတ်တွေထဲမှာ ရွေးချယ်နှိပ်လိုက်ပါနော်-**"
    )
    
    # နှိပ်လို့ရမည့် Inline Buttons Menu များ တည်ဆောက်ခြင်း
    keyboard = [
        [
            InlineKeyboardButton("📦 Python Tools (Marketplace)", callback_data="app_python_market"),
        ],
        [
            InlineKeyboardButton("🔥 Trending Python Projects", callback_data="app_python_trending"),
            InlineKeyboardButton("☕ Trending Java Projects", callback_data="app_java_trending")
        ],
        [
            InlineKeyboardButton("💰 Premium/Sponsor Apps", callback_data="app_sponsorable"),
            InlineKeyboardButton("🧑‍💻 Top GitHub Developers", callback_data="app_top_developers")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# =====================================================================
# ၂။ User နှိပ်လိုက်သည့် ခလုတ်အလိုက် ဒေတာများကို ခွဲခြားဆွဲထုတ်ပေးမည့်အပိုင်း
# =====================================================================
async def handle_menu_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer() # Loading အဝိုင်းလည်နေတာကို ပိတ်ခြင်း
    
    chat_id = query.message.chat_id
    choice = query.data
    
    # ပြင်ဆင်နေစဉ် Typing status ပြခြင်း
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    status_msg = await query.message.reply_text("⏳ GitHub ဆာဗာဆီကနေ ကိုကိုတောင်းဆိုတဲ့ ဒေတာတွေကို ဆွဲထုတ်ပေးနေပါတယ်ရှင့်...")

    # ခလုတ်အလိုက် URL Target များ ခွဲခြားသတ်မှတ်ခြင်း
    target_url = "https://github.com/search?q=python&type=marketplace&query=is%3Asponsorable" # Default
    title_header = "📦 GitHub Tools"

    if choice == "app_python_market":
        target_url = "https://github.com/search?q=python&type=marketplace&query=is%3Asponsorable"
        title_header = "📦 Python Tools (Marketplace)"
    elif choice == "app_python_trending":
        target_url = "https://github.com/trending/python"
        title_header = "🔥 Trending Python Projects"
    elif choice == "app_java_trending":
        target_url = "https://github.com/trending/java"
        title_header = "☕ Trending Java Projects"
    elif choice == "app_sponsorable":
        target_url = "https://github.com/search?q=is%3Asponsorable&type=repositories"
        title_header = "💰 Premium / Sponsorable Projects"
    elif choice == "app_top_developers":
        target_url = "https://github.com/search?q=type%3Auser&type=users"
        title_header = "🧑‍💻 Top GitHub Developers"

    # API Payload ပြင်ဆင်ခြင်း
    payload = {
        "url": target_url,
        "pageNumber": 1,
        "maxPage": 1,
        "cookies": []
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            items = result.get("items") or result.get("results") or result.get("data")
            
            if not items:
                await status_msg.edit_text(f"⚠️ ကိုကိုရယ်... လောလောဆယ် `{title_header}` ထဲမှာ ဒေတာအသစ် ရှာမတွေ့သေးပါဘူးရှင့်။")
                return

            report_text = f"✨ **{title_header}** ✨\n\n"
            
            # ထိပ်ဆုံး ရလဒ် ၅ ခုကို ထုတ်ပြခြင်း
            for idx, item in enumerate(items[:5], 1):
                name = item.get("name") or item.get("title") or item.get("username") or "Unknown Result"
                repo_url = item.get("url") or item.get("link") or "https://github.com"
                desc = item.get("description") or item.get("bio") or "No description available."
                
                report_text += f"{idx}. 🚀 **{name}**\n"
                report_text += f"📝 {desc}\n"
                report_text += f"🔗 [ကြည့်ရှုရန်လင့်ခ်]({repo_url})\n\n"
                report_text += "------------------------\n\n"

            await status_msg.delete()
            await query.message.reply_text(text=report_text, parse_mode="Markdown", disable_web_page_preview=True)
            
        else:
            await status_msg.edit_text(f"❌ API Error တက်သွားသည် ကိုကို။ Code {response.status_code}")
            
    except Exception as e:
        await status_msg.edit_text(f"❌ ချိတ်ဆက်မှု အဆင်မပြေပါ ကိုကိုရယ်- {str(e)}")

# =====================================================================
# ၃။ ပရိုဂရမ် စတင် Run မည့်နေရာ
# =====================================================================
def main() -> None:
    threading.Thread(target=run_flask, daemon=True).start()

    application = Application.builder().token(TOKEN).build()
    
    # /start command ပို့လျှင် ဖမ်းရန်
    application.add_handler(CommandHandler("start", start))
    
    # ခလုတ် (Menu Buttons) များကို နှိပ်လျှင် ဖမ်းရန် CallbackQueryHandler သုံးခြင်း
    application.add_handler(CallbackQueryHandler(handle_menu_click))

    print("GitHub Portal Bot with full App Menu is running successfully...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
