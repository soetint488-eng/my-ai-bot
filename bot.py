import logging
import os
import threading
import requests
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- CONFIGURATION ---
BOT_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
RAPIDAPI_KEY = "06b1562a59msh39810b847e9d0e2p151fd6jsn3a9d60ae50a9"
RAPIDAPI_HOST = "id-game-checker.p.rapidapi.com"

# --- RENDER PORT FIX ---
logging.basicConfig(level=logging.INFO)
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    with TCPServer(("", port), SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()

# --- CORE FUNCTION ---
def check_mlbb_data(user_id, zone_id):
    url = f"https://{RAPIDAPI_HOST}/mobile-legends/{user_id}/{zone_id}"
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": RAPIDAPI_HOST}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        return (response.json(), None) if response.status_code == 200 else (None, f"Error: {response.status_code}")
    except Exception as e:
        return None, str(e)

# --- COMMAND HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "✨ **DOMINIC MLBB UTILITY**\n\n"
        "Commands Available:\n"
        "👉 `/id [ID] [Zone]` - Check Nickname\n"
        "👉 `/servers` - View Server Regions\n\n"
        "💡 *Tap any text to copy instantly!*"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❌ **Format:** `/id [ID] [Zone]`", parse_mode='Markdown')
        return
    
    u_id, z_id = context.args[0], context.args[1]
    status_msg = await update.message.reply_text("🔍 **Searching...**", parse_mode='Markdown')
    data, error = check_mlbb_data(u_id, z_id)
    
    if data and 'data' in data:
        nickname = data['data'].get('username', 'Unknown')
        
        # Format with `backticks` for Auto-Copy feature
        result = (
            "🎮 **PLAYER FOUND**\n"
            "━━━━━━━━━━━━━━━\n"
            "👤 **Name:** `{}`\n"
            "🆔 **ID:** `{}`\n"
            "🌐 **Zone:** `{}`\n"
            "━━━━━━━━━━━━━━━\n"
            "✅ **Verified by Dominic**\n"
            "💡 *Tap the name to copy!*"
        ).format(nickname, u_id, z_id)
        
        await status_msg.edit_text(result, parse_mode='Markdown')
    else:
        await status_msg.edit_text("⚠️ **ERROR:** ID not found.", parse_mode='Markdown')

async def servers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    server_list = (
        "🌐 **SERVER REGIONS**\n"
        "━━━━━━━━━━━━━━━\n"
        "🇲🇲 **SEA:** `2xxx, 3xxx, 4xxx, 5xxx, 6xxx`\n"
        "🇧🇷 **LATAM:** `7xxx`\n"
        "🇪🇺 **Europe:** `8xxx`\n"
        "🇺🇸 **NA:** `9xxx`\n"
        "━━━━━━━━━━━━━━━\n"
        "💡 *Click numbers to copy.*"
    )
    await update.message.reply_text(server_list, parse_mode='Markdown')

# --- MAIN ---
if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", id_handler))
    app.add_handler(CommandHandler("servers", servers_handler))
    
    print("Dominic MLBB Bot is Online with Auto-Copy.")
    app.run_polling(drop_pending_updates=True)
