import time, uuid, threading, os, requests, re
from flask import Flask, jsonify, send_from_directory
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# --- CONFIG ---
BOT_TOKEN = '8702294693:AAGbo2lTWP-aV1jV8Be6nN5NSnz2WO_aZJk'
ADMIN_ID = 8584422107  
DOWNLOAD_DIR = "downloads"
PATH_FILE = "paths.txt"
NOTE_FILE = "app_note.txt" # Note သိမ်းမည့်ဖိုင်

if not os.path.exists(DOWNLOAD_DIR): 
    os.makedirs(DOWNLOAD_DIR)

# Note ကို Load လုပ်ရန်
app_note = "Welcome to Dominic System!"
if os.path.exists(NOTE_FILE):
    try:
        with open(NOTE_FILE, "r", encoding="utf-8") as f:
            app_note = f.read().strip()
    except: pass

# Path များကို Load လုပ်ရန်
tv_paths = {}
if os.path.exists(PATH_FILE):
    try:
        with open(PATH_FILE, "r") as f:
            for line in f:
                if ":" in line:
                    k, v = line.strip().split(":", 1)
                    tv_paths[k] = v
    except: pass

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

# --- HANDLER: Admin Messages ---

async def handle_admin_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    # ၁။ Document ပို့လာရင်
    if update.message.document:
        file_id = update.message.document.file_id
        context.user_data['pending_file'] = file_id
        context.user_data['mode'] = 'file'
        buttons = [[InlineKeyboardButton(f"Save TV {i}", callback_data=f"save_tv{i}") for i in range(8, 11)],
                   [InlineKeyboardButton(f"Save TV {i}", callback_data=f"save_tv{i}") for i in range(11, 13)]]
        await update.message.reply_text("📁 ဖိုင်ကို ဘယ်နေရာမှာ သိမ်းမလဲ?", reply_markup=InlineKeyboardMarkup(buttons))
    
    # ၂။ စာသား ပို့လာရင် (Link, Path သို့မဟုတ် Note)
    elif update.message.text:
        msg_text = update.message.text
        
        # Note သတ်မှတ်ခြင်း (ဥပမာ- Note: မင်္ဂလာပါ)
        if msg_text.startswith("Note:"):
            global app_note
            app_note = msg_text.replace("Note:", "").strip()
            with open(NOTE_FILE, "w", encoding="utf-8") as f:
                f.write(app_note)
            await update.message.reply_text(f"✅ App Note ကို ပြောင်းလဲလိုက်ပါပြီ:\n`{app_note}`", parse_mode='Markdown')

        # MediaFire Link ဖြစ်ခဲ့လျှင်
        elif "mediafire.com" in msg_text:
            direct = get_mediafire_direct(msg_text)
            if direct:
                context.user_data['pending_link'] = direct
                context.user_data['mode'] = 'link'
                buttons = [[InlineKeyboardButton(f"Link to TV {i}", callback_data=f"save_tv{i}") for i in range(8, 11)],
                           [InlineKeyboardButton(f"Link to TV {i}", callback_data=f"save_tv{i}") for i in range(11, 13)]]
                await update.message.reply_text("🔗 MediaFire Link ရပါပြီ။ ဘယ်မှာ သိမ်းမလဲ?", reply_markup=InlineKeyboardMarkup(buttons))
        
        # / ဖြင့်စသော လမ်းကြောင်း (Path) ဖြစ်ခဲ့လျှင်
        elif msg_text.startswith("/"):
            context.user_data['pending_path'] = msg_text
            buttons = [[InlineKeyboardButton(f"Path to TV {i}", callback_data=f"setpath_tv{i}") for i in range(8, 11)],
                       [InlineKeyboardButton(f"Path to TV {i}", callback_data=f"setpath_tv{i}") for i in range(11, 13)]]
            await update.message.reply_text(f"📍 ဒီလမ်းကြောင်းကို ဘယ် TV မှာ သုံးမလဲ?\n`{msg_text}`", 
                                          reply_markup=InlineKeyboardMarkup(buttons), parse_mode='Markdown')

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
    
    if query.data == 'gen_key':
        new_key = str(uuid.uuid4())[:8].upper()
        name = f"@{query.from_user.username}" if query.from_user.username else f"ID:{query.from_user.id}"
        active_keys[new_key] = {"expiry": time.time() + 10800, "used_by": None, "tg_name": name}
        await query.message.reply_text(f"✅ **Key:** `{new_key}`\n⏳ Valid for 3 Hours", parse_mode='Markdown')

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

    elif query.data.startswith("setpath_tv"):
        tv_id = query.data.replace("setpath_", "")
        path_val = context.user_data.get('pending_path')
        if path_val:
            tv_paths[tv_id] = path_val
            with open(PATH_FILE, "w") as f:
                for k, v in tv_paths.items():
                    f.write(f"{k}:{v}\n")
            await query.edit_message_text(f"✅ {tv_id.upper()} အတွက် Path သတ်မှတ်ပြီးပါပြီ။\n📍 `{path_val}`", parse_mode='Markdown')
        context.user_data.clear()

    elif query.data.startswith("del_tv"):
        tv_id = query.data.split("_")[1]
        path = os.path.join(DOWNLOAD_DIR, f"{tv_id}.dat")
        if os.path.exists(path):
            os.remove(path)
            await query.edit_message_text(f"🗑️ {tv_id.upper()} ဖိုင်ကို ဖျက်လိုက်ပါပြီ။")
        else:
            await query.edit_message_text("❌ ဖိုင်မရှိပါ။")

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
        await update.message.reply_text(msg, parse_mode='Markdown')

async def delete_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    buttons = [[InlineKeyboardButton(f"Del TV {i}", callback_data=f"del_tv{i}") for i in range(8, 11)],
               [InlineKeyboardButton(f"Del TV {i}", callback_data=f"del_tv{i}") for i in range(11, 13)]]
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

@flask_app.route('/')
def home():
    return "DOMINIC SYSTEM IS ONLINE ✅", 200

@flask_app.route('/get_note')
def get_note():
    return app_note

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

@flask_app.route('/get_path/<tv_id>')
def get_path(tv_id):
    path = tv_paths.get(tv_id, "/storage/emulated/0/Android/data/com.mobile.legends/files/dragon2017/assets/Document/android/")
    return path

@flask_app.route('/download/<tv_id>')
def download_by_tv(tv_id):
    filename = f"{tv_id}.dat"
    path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(path):
        return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True, download_name="Document.unity3d")
    return "File Not Found", 404

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("user", user_list))
    app.add_handler(CommandHandler("delete", delete_menu))
    app.add_handler(MessageHandler(filters.Chat(ADMIN_ID) & (filters.Document.ALL | filters.TEXT), handle_admin_msg))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
