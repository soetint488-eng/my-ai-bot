import time
import uuid
import threading
import os
from flask import Flask, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# --- CONFIG ---
BOT_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
ADMIN_ID = 5664321356  # မောင့် ID ကို ဒီမှာ ထည့်ပါ
flask_app = Flask(__name__)

active_keys = {}  # {key: {"expiry": timestamp, "used_by": device_id}}
blocked_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in blocked_users:
        await update.message.reply_text("🚫 You are blocked.")
        return
    keyboard = [[InlineKeyboardButton("Create Key 🗝️", callback_data='gen_key')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✨ **DOMINIC LICENSE SYSTEM**\nClick below for a 3-hour key.", reply_markup=reply_markup, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id in blocked_users: return
    if query.data == 'gen_key':
        new_key = str(uuid.uuid4())[:8].upper()
        active_keys[new_key] = {"expiry": time.time() + 10800, "used_by": None}
        await query.message.reply_text(f"✅ **Key Created!**\n🗝️ Key: `{new_key}`\n⏳ Validity: 3 Hours", parse_mode='Markdown')

# Admin Commands: /block [ID], /unblock [ID]
async def block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID and context.args:
        blocked_users.add(context.args[0])
        await update.message.reply_text(f"🔒 Blocked: {context.args[0]}")

# --- API FOR SKETCHWARE ---
@flask_app.route('/verify/<key_id>/<user_id>')
def verify(key_id, user_id):
    if user_id in blocked_users: return jsonify({"status": "blocked"})
    if key_id in active_keys:
        data = active_keys[key_id]
        if data["used_by"] and data["used_by"] != user_id:
            return jsonify({"status": "taken"})
        if time.time() < data["expiry"]:
            active_keys[key_id]["used_by"] = user_id
            return jsonify({"status": "success"})
        return jsonify({"status": "expired"})
    return jsonify({"status": "invalid"})

@flask_app.route('/count')
def get_count(): return jsonify({"count": len(active_keys)})

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("block", block))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
