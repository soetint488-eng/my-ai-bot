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

# --- TELEGRAM BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = f"@{user.username}" if user.username else f"ID:{user.id}"
    keyboard = [[InlineKeyboardButton("Create Key 🗝️", callback_data='gen_key')]]
    await update.message.reply_text(f"✨ **DOMINIC SYSTEM**\nWelcome {name}!", 
                                  reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# Admin ဆီက File လက်ခံခြင်း
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    file = await update.message.document.get_file()
    file_name = update.message.document.file_name
    # နောက်ဆုံးတင်တဲ့ဖိုင်ကို အမြဲတမ်း 'latest_update' အနေနဲ့သိမ်းမယ်
    file_path = os.path.join(DOWNLOAD_DIR, "latest_update")
    
    await file.download_to_drive(file_path)
    await update.message.reply_text(f"✅ **File Uploaded!**\nName: `{file_name}`\nSketchware users can now download it.", parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'gen_key':
        new_key = str(uuid.uuid4())[:8].upper()
        name = f"@{query.from_user.username}" if query.from_user.username else f"ID:{query.from_user.id}"
        active_keys[new_key] = {"expiry": time.time() + 10800, "used_by": None, "tg_name": name}
        await query.message.reply_text(f"✅ **Key:** `{new_key}`\n⏳ Valid for 3 Hours", parse_mode='Markdown')

# --- FLASK API ROUTES ---
@flask_app.route('/download_file')
def download_file():
    try:
        return send_from_directory(DOWNLOAD_DIR, "latest_update", as_attachment=True, download_name="Dominic_Update.apk")
    except Exception:
        return "No file found on server", 404

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

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    # File လက်ခံရန် Handler ထည့်သွင်းခြင်း
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    app.run_polling()
