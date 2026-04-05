import time
import uuid
import threading
import os
from flask import Flask, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# --- CONFIGURATION ---
# မောင့်ရဲ့ Bot Token ကို ဒီမှာ ထည့်ထားပါတယ်
BOT_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
flask_app = Flask(__name__)

# Key များကို သိမ်းဆည်းရန် (In-memory Storage)
active_keys = {}

# --- TELEGRAM BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Create Key 🗝️", callback_data='gen_key')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "✨ **DOMINIC ACCESS SYSTEM**\n\nClick the button to get your 3-hour key.",
        reply_markup=reply_markup, parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'gen_key':
        # ၈ လုံးပါတဲ့ Key တစ်ခု ထုတ်မယ်
        new_key = str(uuid.uuid4())[:8].upper()
        # ၃ နာရီ သက်တမ်း (10800 စက္ကန့်)
        expiry_time = time.time() + 10800
        active_keys[new_key] = expiry_time
        
        msg = (
            "✅ **Key Generated!**\n"
            "━━━━━━━━━━━━━━━\n"
            "🗝️ Key: `{}`\n"
            "⏳ Status: **Active for 3 Hours**\n"
            "━━━━━━━━━━━━━━━\n"
            "💡 *Tap the key to copy and paste in App.*"
        ).format(new_key)
        await query.message.reply_text(msg, parse_mode='Markdown')

# --- API FOR SKETCHWARE ---

# ၁။ Key စစ်ဆေးရန် API
@flask_app.route('/verify/<key_id>')
def verify(key_id):
    now = time.time()
    if key_id in active_keys:
        if now < active_keys[key_id]:
            return jsonify({"status": "success", "msg": "Access Granted"})
        else:
            del active_keys[key_id]
            return jsonify({"status": "expired", "msg": "Key Expired"})
    return jsonify({"status": "invalid", "msg": "Invalid Key"})

# ၂။ Key ထုတ်ထားသူဦးရေ စစ်ရန် API
@flask_app.rowte('/count')
def get_count():
    return jsonify({"count": len(active_keys)})

# Render အတွက် Port ဖွင့်ပေးခြင်း
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Flask Server ကို Background မှာ Run မယ်
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Telegram Bot ကို Run မယ်
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot and API are running...")
    bot_app.run_polling(drop_pending_updates=True)
