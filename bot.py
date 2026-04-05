import time, uuid, threading, os, requests, re
from flask import Flask, jsonify, send_from_directory
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# --- CONFIG ---
BOT_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
ADMIN_ID = 8584422107  
DOWNLOAD_DIR = "downloads"

if not os.path.exists(DOWNLOAD_DIR): 
    os.makedirs(DOWNLOAD_DIR)

flask_app = Flask(__name__)
active_keys = {}  
blocked_users = set()

# --- HELPER: MediaFire Direct Link Extractor ---
def get_mediafire_direct(url):
    try:
        r = requests.get(url, timeout=10)
        direct_link = re.findall(r'href="((http|https)://download[^"]+)"', r.text)
        if direct_link:
            return direct_link[0][0]
        return None
    except:
        return None

# --- NEW: MEDIAFIRE & LINK HANDLER ---

async def handle_admin_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    # ၁။ တကယ်လို့ Document ပို့လာရင် (20MB အောက်ဖိုင်များအတွက်)
    if update.message.document:
        file_id = update.message.document.file_id
        context.user_data['pending_file'] = file_id
        context.user_data['mode'] = 'file'
        
        buttons = [
            [InlineKeyboardButton("Save TV 8", callback_data="save_tv8"), InlineKeyboardButton("Save TV 9", callback_data="save_tv9")],
            [InlineKeyboardButton("Save TV 10", callback_data="save_tv10"), InlineKeyboardButton("Save TV 11", callback_data="save_tv11")],
            [InlineKeyboardButton("Save TV 12", callback_data="save_tv12")]
        ]
        await update.message.reply_text("📁 ဖိုင်ကို ဘယ်နေရာမှာ သိမ်းမလဲ?", reply_markup=InlineKeyboardMarkup(buttons))
    
    # ၂။ တကယ်လို့ MediaFire Link ပို့လာရင် (30MB+ ဖိုင်များအတွက်)
    elif update.message.text and "mediafire.com" in update.message.text:
        direct = get_mediafire_direct(update.message.text)
        if direct:
            context.user_data['pending_link'] = direct
            context.user_data['mode'] = 'link'
            buttons = [
                [InlineKeyboardButton("Link to TV 8", callback_data="save_tv8"), InlineKeyboardButton("Link to TV 9", callback_data="save_tv9")],
                [InlineKeyboardButton("Link to TV 10", callback_data="save_tv10"), InlineKeyboardButton("Link to TV 11", callback_data="save_tv11")],
                [InlineKeyboardButton("Link to TV 12", callback_data="save_tv12")]
            ]
            await update.message.reply_text("🔗 MediaFire Link ရပါပြီ။ ဘယ်မှာ သိမ်းမလဲ?", reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await update.message.reply_text("❌ MediaFire Link မှ Direct Download ရှာမတွေ့ပါ။")

# --- ORIGINAL BOT LOGIC (Key System) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = f"@{user.username}" if user.username else f"ID:{user.id}"
    keyboard = [[InlineKeyboardButton("Create Key 🗝️", callback_data='gen_key')]]
    await update.message.reply_text(f"✨ **DOMINIC SYSTEM**\nWelcome {name}!", 
                                  reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Key Generation
    if query.data == 'gen_key':
        new_key = str(uuid.uuid4())[:8].upper()
        name = f"@{query.from_user.username}" if query.from_user.username else f"ID:{query.from_user.id}"
        active_keys[new_key] = {"expiry": time.time() + 10800, "used_by": None, "tg_name": name}
        await query.message.reply_text(f"✅ **Key:** `{new_key}`\n⏳ Valid for 3 Hours", parse_mode='Markdown')

    # Save Logic (File ရော Link ရော ဒီမှာပဲ လုပ်မယ်)
    elif query.data.startswith("save_tv"):
        tv_id = query.data.replace("save_", "")
        mode = context.user_data.get('mode')
        
        if mode == 'file':
            file_id = context.user_data.get('pending_file')
            if file_id:
                new_file = await context.bot.get_file(file_id)
                await new_file.download_to_drive(os.path.join(DOWNLOAD_DIR, f"{tv_id}.dat"))
                await query.edit_message_text(f"✅ {tv_id.upper()} မှာ ဖိုင်သိမ်းပြီးပါပြီ။")
        
        elif mode == 'link':
            link = context.user_data.get('pending_link')
            if link:
                await query.edit_message_text(f"⏳ {tv_id.upper()} အတွက် Link မှဖိုင်ကို Server ထဲ ဆွဲထည့်နေပါသည်...")
                try:
                    r = requests.get(link, stream=True, timeout=300)
                    with open(os.path.join(DOWNLOAD_DIR, f"{tv_id}.dat"), 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk: f.write(chunk)
                    await query.edit_message_text(f"✅ {tv_id.upper()} မှာ MediaFire ဖိုင်ကို သိမ်းပြီးပါပြီ။")
                except Exception as e:
                    await query.edit_message_text(f"❌ Error: {str(e)}")
        
        context.user_data.clear()

    # Delete Logic
    elif query.data.startswith("del_tv"):
        tv_id = query.data.split("_")[1]
        path = os.path.join(DOWNLOAD_DIR, f"{tv_id}.dat")
        if os.path.exists(path):
            os.remove(path)
            await query.edit_message_text(f"🗑️ {tv_id.upper()} ဖိုင်ကို ဖျက်လိုက်ပါပြီ။")
        else:
            await query.edit_message_text("❌ ဖိုင်မရှိပါ။")

    # Block/Unblock Logic
    elif query.data.startswith("blk_") or query.data.startswith("unb_"):
        if query.from_user.id != ADMIN_ID: return
        action, target = query.data.split("_", 1)
        if target == "None": return await query.message.reply_text("❌ No user data.")
        if action == "blk":
            blocked_users.add(target)
            msg = f"🔒 Blocked: `{target}`"
        else:
            blocked_users.discard(target)
            msg = f"🔓 Unblocked: `{target}`"
        await query.message.reply_text(msg, parse_mode='Markdown')

async def delete_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    buttons = [
        [InlineKeyboardButton("Del TV 8", callback_data="del_tv8"), InlineKeyboardButton("Del TV 9", callback_data="del_tv9")],
        [InlineKeyboardButton("Del TV 10", callback_data="del_tv10"), InlineKeyboardButton("Del TV 11", callback_data="del_tv11")],
        [InlineKeyboardButton("Del TV 12", callback_data="del_tv12")]
    ]
    await update.message.reply_text("🚫 ဘယ်နေရာက ဖိုင်ကို ဖျက်မလဲ?", reply_markup=InlineKeyboardMarkup(buttons))

async def user_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not active_keys: return await update.message.reply_text("📭 No active keys.")
    for k, v in active_keys.items():
        dev_id = str(v['used_by'])
        rem_min = int((v['expiry'] - time.time()) / 60)
        txt = f"👤 **User:** {v['tg_name']}\n🔑 **Key:** `{k}`\n📱 **Device:** `{dev_id}`\n⏳ **Time:** {rem_min} mins"
        btn = [[InlineKeyboardButton("🚫 Block", callback_data=f"blk_{dev_id}"), InlineKeyboardButton("✅ Unblock", callback_data=f"unb_{dev_id}")]]
        await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(btn), parse_mode='Markdown')

# --- FLASK API ROUTES ---

@flask_app.route('/verify/<key_id>/<user_id>')
def verify(key_id, user_id):
    if user_id in blocked_users: return jsonify({"status": "blocked"})
    if key_id in active_keys:
        data = active_keys[key_id]
        if data["used_by"] and data["used_by"] != user_id:
            return jsonify({"status": "taken"})
        active_keys[key_id]["used_by"] = user_id
        return jsonify({"status": "success"})
    return jsonify({"status": "invalid"})

@flask_app.route('/download/<tv_id>')
def download_by_tv(tv_id):
    filename = f"{tv_id}.dat"
    path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(path):
        # အောက်က download_name နေရာမှာ ကိုယ်ပေးချင်တဲ့ နာမည်ပြောင်းနိုင်ပါတယ်
        return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True, download_name=f"Document.unity3d")
    return "File Not Found", 404

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("user", user_list))
    app.add_handler(CommandHandler("delete", delete_menu))
    # Admin ဆီက ဖိုင်ရော စာရော (MediaFire Link) လက်ခံရန်
    app.add_handler(MessageHandler(filters.Chat(ADMIN_ID) & (filters.Document.ALL | filters.TEXT), handle_admin_msg))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    app.run_polling()
