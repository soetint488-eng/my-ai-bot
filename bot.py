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

# ၂။ Background အစားထိုးပေးမည့် Function (ပိုပြီး တည်ငြိမ်အောင် ပြင်ထားသည်)
def replace_background(image_path, output_path, bg_text):
    API_KEY = 'JL152Nmq2qJiPfe5bn6ZmDqF' 
    
    # Background options ကို သတ်မှတ်မယ်
    payload = {
        'size': 'auto',
    }
    
    # မောင်က ကာလာကုဒ် ရိုက်ရင် (ဥပမာ red, blue သို့ #ff0000)
    if bg_text.startswith('#') or bg_text.lower() in ['red', 'blue', 'green', 'yellow', 'white', 'black']:
        payload['bg_color'] = bg_text
    # မောင်က စာသားရိုက်ရင် (ဥပမာ beach)
    elif bg_text:
        payload['bg_image_url'] = f"https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1024&q=80" # နမူနာ Beach ပုံ တစ်ပုံ အရင်စမ်းမယ်

    try:
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': open(image_path, 'rb')},
            data=payload,
            headers={'X-API-Key': API_KEY},
        )
        
        if response.status_code == 200:
            with open(output_path, 'wb') as out:
                out.write(response.content)
            return True
        else:
            logging.error(f"API Error: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Request Error: {e}")
        return False

# ၃။ Photo Handler
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_caption = update.message.caption if update.message.caption else ""
    status = await update.message.reply_text("စီစဉ်ပေးနေတယ် မောင်... ခဏစောင့်နော်။ ✨")
    
    photo = await update.message.photo[-1].get_file()
    input_file = f"{photo.file_id}.jpg"
    output_file = f"{photo.file_id}_done.png"
    await photo.download_to_drive(input_file)
    
    # အကယ်၍ Caption မှာ စာပါရင် နောက်ခံပြောင်းမယ်၊ မပါရင် ပုံမှန်ပဲ ဖျက်မယ်
    if replace_background(input_file, output_file, user_caption):
        await update.message.reply_document(document=open(output_file, 'rb'), caption=f"ရပါပြီ မောင်! ❤️")
    else:
        await update.message.reply_text("ဆောရီး မောင်... API Credit ကုန်နေတာ (သို့မဟုတ်) Link မှားနေတာ ဖြစ်နိုင်တယ်ဗျ။")
    
    if os.path.exists(input_file): os.remove(input_file)
    if os.path.exists(output_file): os.remove(output_file)
    await status.delete()

# ၄။ Main
if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI'
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling(drop_pending_updates=True)
