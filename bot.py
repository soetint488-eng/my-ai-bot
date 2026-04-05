import time, uuid, threading, os
from flask import Flask, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# --- CONFIG ---
BOT_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
ADMIN_ID = 8584422107  # မောင့် Admin ID ကို ပြင်ပေးထားပါတယ်
flask_app = Flask(__name__)

active_keys = {}  # {key: {"expiry": t, "used_by": dev_id, "tg_name": name}}
blocked_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = f"@{user.username}" if user.username else f"ID:{user.id}"
    keyboard = [[InlineKeyboardButton("Create Key 🗝️", callback_data='gen_key')]]
    await update.message.reply_text(f"✨ **DOMINIC SYSTEM**\nWelcome {name}!", 
                                  reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'gen_key':
        new_key = str(uuid.uuid4())[:8].upper()
        name = f"@{query.from_user.username}" if query.from_user.username else f"ID:{query.from_user.id}"
        active_keys[new_key] = {"expiry": time.time() + 10800, "used_by": None, "tg_name": name}
        await query.message.reply_text(f"✅ **Key:** `{new_key}`\n⏳ Valid for 3 Hours", parse_mode='Markdown')

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
    # Username တွေကို စာရင်းလုပ်ပြီး ပြန်ပို့ပေးမယ်
    names = [v['tg_name'] for k, v in active_keys.items()]
    return jsonify({"names": names})

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("user", user_list))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
