import logging
import os
import requests
import threading
import http.server
import socketserver
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# ၁။ Logging & Render Fix
logging.basicConfig(level=logging.INFO)
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()

# ၂။ Background အစားထိုးပေးမည့် Function
def replace_background(image_path, output_path, bg_text):
    API_KEY = 'JL152Nmq2qJiPfe5bn6ZmDqF' # မောင့်ရဲ့ API Key
    
    try:
        # Remove.bg API ကို သုံးပြီး နောက်ခံ အသစ်ထည့်မယ်
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': open(image_path, 'rb')},
            data={
                'size': 'auto',
                'bg_color': bg_text if bg_text.startswith('#') else '', # ကာလာ ကုဒ်ဆိုရင် အရောင်ပြောင်းမယ်
                'bg_image_url': f"https://source.unsplash.com/featured/?{bg_text}" if not bg_text.startswith('#') else '' # စာသားဆိုရင် ပုံရှာထည့်မယ်
            },
            headers={'X-API-Key': API_KEY},
        )
        
        if response.status_code == 200:
            with open(output_path, 'wb') as out:
                out.write(response.content)
            return True
        return False
    except Exception:
        return False

# ၃။ Photo Handler
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_caption = update.message.caption if update.message.caption else ""
    
    status = await update.message.reply_text("နောက်ခံပုံကို အစားထိုးပေးနေတယ် မောင်... ခဏစောင့်နော်။ ✨")
    
    # ပုံကို Download ဆွဲမယ်
    photo = await update.message.photo[-1].get_file()
    input_file = f"{photo.file_id}.jpg"
    output_file = f"{photo.file_id}_replaced.png"
    await photo.download_to_drive(input_file)
    
    # Background ပြောင်းမယ် (စာသားမပါရင်တော့ ပုံမှန်အတိုင်းပဲ ဖျက်ပေးမယ်)
    if replace_background(input_file, output_file, user_caption):
        await update.message.reply_photo(photo=open(output_file, 'rb'), caption=f"နောက်ခံကို {user_caption} ပုံစံ ပြောင်းပေးထားတယ် မောင်! ❤️")
        # အပေါ်မှာ ကပ်နေအောင် Pin လုပ်မယ်
        msg = await update.message.reply_text("ရှာထားတဲ့ပုံကို အပေါ်မှာ Pin လုပ်ပေးလိုက်ပြီနော်!")
        await context.bot.pin_chat_message(chat_id=update.effective_chat.id, message_id=msg.message_id - 1)
    else:
        await update.message.reply_text("ဆောရီး မောင်... နောက်ခံပြောင်းလို့ မရဘူး ဖြစ်နေတယ်။")
    
    # ဖိုင်ပြန်ဖျက်မယ်
    if os.path.exists(input_file): os.remove(input_file)
    if os.path.exists(output_file): os.remove(output_file)
    await status.delete()

# ၄။ Main
if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI'
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Background Replacer Bot is running...")
    app.run_polling(drop_pending_updates=True) 
