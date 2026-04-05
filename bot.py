import time, uuid, threading, os
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

# --- NEW: FILE SYSTEM HANDLERS ---

# Admin ဖိုင်ပို့လျှင် ဘယ်နေရာ သိမ်းမလဲ မေးခြင်း
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    file_id = update.message.document.file_id
    context.user_data['pending_file'] = file_id
    
    buttons = [
        [InlineKeyboardButton("TextView 8", callback_data="save_tv8"), InlineKeyboardButton("TextView 9", callback_data="save_tv9")],
        [InlineKeyboardButton("TextView 10", callback_data="save_tv10"), InlineKeyboardButton("TextView 11", callback_data="save_tv11")],
        [InlineKeyboardButton("TextView 12", callback_data="save_tv12")]
    ]
    await update.message.reply_text("📁 ဘယ် TextView ထဲကို သိမ်းမှာလဲ ခင်ဗျာ?", 
                                  reply_markup=InlineKeyboardMarkup(buttons))

# ဖိုင်ပြန်ဖျက်ရန် Menu
async def delete_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    buttons = [
        [InlineKeyboardButton("Delete TV 8", callback_data="del_tv8"), InlineKeyboardButton("Delete TV 9", callback_data="del_tv9")],
        [InlineKeyboardButton("Delete TV 10", callback_data="del_tv10"), InlineKeyboardButton("Delete TV 11", callback_data="del_tv11")],
        [InlineKeyboardButton("Delete TV 12", callback_data="del_tv12")]
    ]
    await update.message.reply_text("🚫 ဘယ်နေရာက ဖိုင်ကို ဖျက်မှာလဲ?", reply_markup=InlineKeyboardMarkup(buttons))

# --- ORIGINAL BOT LOGIC ---

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

    # Save File Logic
    elif query.data.startswith("save_tv"):
        tv_id = query.data.split("_")[1]
        file_id = context.user_data.get('pending_file')
        if file_id:
            new_file = await context.bot.get_file(file_id)
            await new_file.download_to_drive(os.path.join(DOWNLOAD_DIR, f"{tv_id}.dat"))
            await query.edit_message_text(f"✅ {tv_id.upper()} ထဲသို့ ဖိုင်သိမ်းဆည်းပြီးပါပြီ။")
            context.user_data['pending_file'] = None

    # Delete File Logic
    elif query.data.startswith("del_tv"):
        tv_id = query.data.split("_")[1]
        path = os.path.join(DOWNLOAD_DIR, f"{tv_id}.dat")
        if os.path.exists(path):
            os.remove(path)
            await query.edit_message_text(f"🗑️ {tv_id.upper()} ထဲက ဖိုင်ကို ဖျက်လိုက်ပါပြီ။")
        else:
            await query.edit_message_text("❌ ဖိုင်မရှိပါ။")

    # Block/Unblock Logic
    elif query.data.startswith("blk_") or query.data.startswith("unb_"):
        if query.from_user.id != ADMIN_ID: return
        action, target = query.data.split("_", 1)
        if target == "None": return await query.message.reply_text("❌ This user hasn't logged in yet.")
        if action == "blk":
            blocked_users.add(target)
            msg = f"🔒 Blocked Device: `{target}`"
        else:
            blocked_users.discard(target)
            msg = f"🔓 Unblocked Device: `{target}`"
        await query.message.reply_text(msg, parse_mode='Markdown')

async def user_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not active_keys: return await update.message.reply_text("📭 No active keys.")
    for k, v in active_keys.items():
        dev_id = str(v['used_by'])
        rem_min = int((v['expiry'] - time.time()) / 60)
        txt = f"👤 **User:** {v['tg_name']}\n🔑 **Key:** `{k}`\n📱 **Device:** `{dev_id}`\n⏳ **Time:** {rem_min} mins left"
        btn = [[
            InlineKeyboardButton("🚫 Block", callback_data=f"blk_{dev_id}"),
            InlineKeyboardButton("✅ Unblock", callback_data=f"unb_{dev_id}")
        ]]
        await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(btn), parse_mode='Markdown')

# --- ORIGINAL FLASK API + NEW DOWNLOAD ROUTE ---

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

@flask_app.route('/usernames')
def get_usernames():
    names = [v['tg_name'] for k, v in active_keys.items()]
    return jsonify({"names": names})

@flask_app.route('/download/<tv_id>')
def download_by_tv(tv_id):
    filename = f"{tv_id}.dat"
    if os.path.exists(os.path.join(DOWNLOAD_DIR, filename)):
        return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True, download_name=f"{tv_id}_Update.apk")
    return "File Not Found", 404

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("user", user_list))
    app.add_handler(CommandHandler("delete", delete_menu)) # ဖျက်ရန် Command
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document)) # ဖိုင်လက်ခံရန်
    app.add_handler(CallbackQueryHandler(button_handler))
    
    app.run_polling()
