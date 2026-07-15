import os
import requests
import base64
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = "8702294693:AAHFj1uHEkpBfUVd9CTu2d7x3O_O767bxA8"  # အခုဆောက်နေတဲ့ Admin Bot Token
GITHUB_TOKEN = "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"
GITHUB_REPO = "soetint488-eng/my-bot" # ဥပမာ "soetint488-eng/my-bot"
RENDER_TOKEN = "rnd_GOBH4mR6EnE1EXNLusEf32gKQ3P7"
RENDER_SERVICE_ID = "srv-d67o32a4d50c73aibe80" # srv-xxxxxx (စောစောက ရှာထားတဲ့ ID)

# ယာယီ Data သိမ်းရန် (File ပြင်တဲ့အခါ သုံးဖို့)
USER_STATES = {}

# --- HELPER FUNCTIONS ---
def get_github_headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

def get_render_headers():
    return {
        "Authorization": f"Bearer {RENDER_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

# --- BOT COMMANDS & HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main Menu ပြသခြင်း"""
    keyboard = [
        [InlineKeyboardButton("📁 GitHub Folder Code", callback_data="view_folder")],
        [InlineKeyboardButton("🚀 Render Run (Clear & Restart)", callback_data="render_run")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎛️ **Admin Control Panel**\nအောက်က ခလုတ်များကို နှိပ်၍ စီမံနိုင်သည်၊", reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # 1. GitHub Folder ရှိ File များစာရင်းကို Button အနေနဲ့ပြခြင်း
    if data == "view_folder":
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/"
        res = requests.get(url, headers=get_github_headers())
        
        if res.status_code == 200:
            files = res.json()
            keyboard = []
            for f in files:
                if f['type'] == 'file': # ဖိုင်ဆိုရင် ရွေးလို့ရအောင် Button လုပ်မည်
                    keyboard.append([InlineKeyboardButton(f"📄 {f['name']}", callback_data=f"file_{f['path']}")])
            
            keyboard.append([InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu")])
            await query.edit_message_text("📂 **GitHub ထဲရှိ ဖိုင်များ စာရင်း:**\nကုဒ်ကြည့်ရန် သို့မဟုတ် ပြင်ဆင်ရန် ဖိုင်ကိုနှိပ်ပါ၊", 
                                          reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            await query.edit_message_text("❌ GitHub ကနေ File List ဆွဲမရဖြစ်နေသည်။")

    # 2. ရွေးလိုက်တဲ့ File ကို Telegram ထံ စာသားဖိုင်အနေနဲ့ ပို့ပေးခြင်း
    elif data.startswith("file_"):
        file_path = data.split("_", 1)[1]
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
        res = requests.get(url, headers=get_github_headers())
        
        if res.status_code == 200:
            file_data = res.json()
            # Base64 ကနေ စာသားအဖြစ် ပြောင်းလဲခြင်း
            code_content = base64.b64decode(file_data['content']).decode('utf-8')
            sha = file_data['sha']
            
            # ဖိုင်ကို ဆောက်ပြီး user ဆီ ပို့ပေးခြင်း
            local_filename = file_path.split("/")[-1]
            with open(local_filename, "w", encoding="utf-8") as f:
                f.write(code_content)
                
            # နောက်တစ်ကြိမ် ဖိုင်ပြန်ပို့ရင် auto-upload လုပ်နိုင်အောင် state မှတ်ထားခြင်း
            USER_STATES[query.from_user.id] = {"editing_file": file_path, "sha": sha}
            
            await query.message.reply_document(document=open(local_filename, 'rb'), 
                                               caption=f"📝 **{file_path}** ကို ပို့ပေးထားသည်။\n\n⚠️ **ပြင်ဆင်နည်း:** ဤဖိုင်ကို ဒေါင်းလုဒ်လုပ်၊ ကုဒ်များပြင်ဆင်ပြီး ဤ Bot ထံသို့ `.py` သို့မဟုတ် သက်ဆိုင်ရာဖိုင်အလိုက် **File အနေဖြင့် ပြန်လည် ပို့ပေးပါ** (Auto Upload တင်ပေးမည်)။")
            os.remove(local_filename)
        else:
            await query.edit_message_text("❌ ဖိုင်အကြောင်းအရာကို ဆွဲယူ၍မရပါ။")

    # 3. Render မှာ Auto Clear Cache & Deploy (Run) လုပ်ခြင်း
    elif data == "render_run":
        await query.edit_message_text("⏳ Render Engine ကို ရှင်းလင်းပြီး ပြန်လည်ပတ်နေပါသည်...")
        
        url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys"
        # clearCache: "clear" ထည့်ခြင်းဖြင့် ယခင် build အဟောင်းတွေကို ရှင်းထုတ်ပြီး အသစ် run စေပါသည်
        payload = {"clearCache": "clear"} 
        res = requests.post(url, json=payload, headers=get_render_headers())
        
        if res.status_code == 201:
            # အောင်မြင်လျှင် ပြသမည့် animation animation နှင့် message
            await query.edit_message_text("✨🚀 **SUCCESSFUL!** 🚀✨\n\nRender Service ကို Auto Clear လုပ်ပြီး အောင်မြင်စွာ စတင်မောင်းနှင်လိုက်ပါပြီ။\nBot ပြန်တက်လာရန် စက္ကန့်ပိုင်း စောင့်ပါ။")
        else:
            # Error ဖြစ်ရင် စာသား ကော်ပီကူးရလွယ်အောင် backtick (code text) နဲ့ ပြပေးခြင်း
            error_details = res.text
            await query.edit_message_text(f"❌ **Render Error ဖြစ်သွားပါသည်!**\n\nError Code ကို အောက်တွင် Copy ကူးနိုင်သည်-\n```text\nStatus: {res.status_code}\n{error_details}\n```", parse_mode="Markdown")

    elif data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("📁 GitHub Folder Code", callback_data="view_folder")],
            [InlineKeyboardButton("🚀 Render Run (Clear & Restart)", callback_data="render_run")]
        ]
        await query.edit_message_text("🎛️ **Admin Control Panel**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# 4. User ထံမှ ပြန်ပို့လာသော ပြင်ဆင်ပြီးသား File ကို လက်ခံပြီး GitHub သို့ Auto Upload (Commit) တင်ပေးခြင်း
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # ဤ User သည် ဖိုင်ပြင်ဆင်နေဆဲ ဟုတ်/မဟုတ် စစ်ဆေးခြင်း
    if user_id not in USER_STATES or "editing_file" not in USER_STATES[user_id]:
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ အရင်ဆုံး 'GitHub Folder Code' မှတစ်ဆင့် ပြင်ချင်သော ဖိုင်ကို အရင်ရွေးချယ်ပါ။")
        return
        
    file_path = USER_STATES[user_id]["editing_file"]
    old_sha = USER_STATES[user_id]["sha"]
    
    # Telegram ဆာဗာမှ ဖိုင်ကို ဒေါင်းလုဒ်လုပ်ခြင်း
    doc = update.message.document
    telegram_file = await context.bot.get_file(doc.file_id)
    
    # ဖတ်ပြီး content အား string ပြောင်းခြင်း
    file_bytes = requests.get(telegram_file.file_path).content
    encoded_content = base64.b64encode(file_bytes).decode('utf-8')
    
    # GitHub သို့ API ဖြင့် ပြန်လည် Upload (PUT request) လုပ်ခြင်း
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    payload = {
        "message": f"🤖 Auto updated via Telegram Admin Bot",
        "content": encoded_content,
        "sha": old_sha
    }
    
    res = requests.put(url, json=payload, headers=get_github_headers())
    
    if res.status_code == 200 or res.status_code == 201:
        await update.message.reply_text("🎉✨ **SUCCESSFUL!** ✨🎉\n\nကုဒ်အသစ်ကို GitHub ပေါ်သို့ Auto Upload တင်ပေးလိုက်ပါပြီ။ Render တွင် အလုပ်လုပ်ရန် 'Render Run' ခလုတ်ကို နှိပ်နိုင်ပါသည်။")
        # state ကို ရှင်းထုတ်ခြင်း
        del USER_STATES[user_id]
    else:
        await update.message.reply_text(f"❌ GitHub သို့ Upload တင်ရာတွင် အမှားအယွင်းရှိခဲ့သည်။\n```text\n{res.text}\n```", parse_mode="Markdown")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    print("Admin Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    application.run_polling()

if __name__ == "__main__":
    main()
