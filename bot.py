import logging
import os
import http.server
import socketserver
import threading
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# ၁။ Logging စနစ်
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Render Port Fix (Render ပေါ်မှာ Bot မသေအောင် လုပ်ပေးတာပါ)
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            logging.info(f"Port {port} is active.")
            httpd.serve_forever()
    except Exception as e:
        logging.error(f"Server Error: {e}")

# ၂။ Background ဖျက်ပေးမည့် Function
def remove_background(image_path, output_path):
    # မောင့်ရဲ့ API Key ကို ဒီမှာ ထည့်ထားပေးတယ်
    API_KEY = 'JL152Nmq2qJiPfe5bn6ZmDqF' 
    
    try:
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': open(image_path, 'rb')},
            data={'size': 'auto'},
            headers={'X-API-Key': API_KEY},
        )
        
        if response.status_code == 200:
            with open(output_path, 'wb') as out:
                out.write(response.content)
            return True
        else:
            logging.error(f"Remove.bg Error: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Process Error: {e}")
        return False

# ၃။ ပုံဝင်လာရင် ကိုင်တွယ်မည့် Handler
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo: return
    
    # User ကို အကြောင်းကြားစာ ပို့မယ်
    status_msg = await update.message.reply_text("ခဏစောင့်ပါ မောင်... Background ဖျက်ပေးနေပါတယ်။ ✨")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_document")
    
    # ပုံကို ဒေါင်းလုဒ် ဆွဲမယ်
    photo = await update.message.photo[-1].get_file()
    input_file = f"{photo.file_id}.jpg"
    output_file = f"{photo.file_id}_nobg.png"
    await photo.download_to_drive(input_file)
    
    # Background ဖျက်ခြင်း အလုပ်စလုပ်မယ်
    if remove_background(input_file, output_file):
        # အောင်မြင်ရင် PNG ဖိုင် (Document) အနေနဲ့ ပို့မယ် (ပုံမဝါးအောင်လို့ပါ)
        with open(output_file, 'rb') as doc:
            await update.message.reply_document(document=doc, caption="ဟောဒီမှာ မောင့်အတွက် Background ဖျက်ပြီးသားပုံလေး! ❤️")
    else:
        await update.message.reply_text("ဆောရီး မောင်... တစ်ခုခု မှားနေလို့ Background ဖျက်လို့ မရဘူးဖြစ်နေတယ်။ API limit ပြည့်သွားတာလား စစ်ပေးပါဦး။")
    
    # ဆာဗာပေါ်မှာ နေရာမယူအောင် ဖိုင်တွေကို ပြန်ဖျက်မယ်
    if os.path.exists(input_file): os.remove(input_file)
    if os.path.exists(output_file): os.remove(output_file)
    await status_msg.delete()

# ၄။ ပင်မ လုပ်ဆောင်ချက်
if __name__ == '__main__':
    # Port Server ကို Background မှာ နှိုးမယ်
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    # မောင့်ရဲ့ Telegram Bot Token
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI' 
    
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        
        # ဓာတ်ပုံ သီးသန့်ကိုပဲ လက်ခံမယ်
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        
        logging.info("--- Background Remover Bot Started ---")
        app.run_polling(drop_pending_updates=True, stop_signals=None)
    except Exception as e:
        logging.error(f"Fatal Error: {e}")
