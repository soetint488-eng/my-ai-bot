import logging
import os
import http.server
import socketserver
import threading
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# ၁။ Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Render Port Fix
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            httpd.serve_forever()
    except Exception: pass

# ၂။ Anime ပြောင်းပေးတဲ့ Function (Free AI)
def convert_to_anime(image_url):
    # Pollinations AI ကို သုံးပြီး ပုံစံပြောင်းမယ်
    prompt = "convert this image to high quality anime style, studio ghibli, vibrant colors, detailed"
    encoded_prompt = requests.utils.quote(prompt)
    anime_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed=42&model=flux&image={image_url}"
    return anime_url

# ၃။ Background ဖျက်ပေးတဲ့ Function
def remove_background(image_path, output_path):
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
        return False
    except Exception: return False

# ၄။ ပုံဝင်လာရင် ကိုင်တွယ်မည့် Handler
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.caption if update.message.caption else ""
    
    # ပုံကို အရင် Download ဆွဲမယ်
    photo = await update.message.photo[-1].get_file()
    img_path = f"{photo.file_id}.jpg"
    await photo.download_to_drive(img_path)

    # အကယ်၍ Caption မှာ 'anime' လို့ပါရင် Anime ပြောင်းမယ်
    if 'anime' in user_msg.lower():
        status = await update.message.reply_text("Anime ရုပ်လေး ပြောင်းပေးနေတယ် မောင်... ❤️")
        # Telegram ရဲ့ File URL ကို ယူပြီး AI ဆီ ပို့မယ်
        anime_result = convert_to_anime(photo.file_path)
        await update.message.reply_photo(photo=anime_result, caption="ဟောဒီမှာ မောင့်ရဲ့ Anime ပုံလေး! ✨")
        await status.delete()
    
    # ပုံမှန်ဆိုရင် Background ပဲ ဖျက်ပေးမယ်
    else:
        status = await update.message.reply_text("Background ဖျက်ပေးနေပါတယ် မောင်... ✨")
        out_path = f"{photo.file_id}_nobg.png"
        if remove_background(img_path, out_path):
            await update.message.reply_document(document=open(out_path, 'rb'), caption="Background ဖျက်ပြီးပါပြီ!")
        else:
            await update.message.reply_text("ဆောရီး မောင်... Background ဖျက်လို့ မရဘူးဖြစ်နေတယ်။")
        if os.path.exists(out_path): os.remove(out_path)

    if os.path.exists(img_path): os.remove(img_path)

# ၅။ Main
if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI' 
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Bot is running with Anime & BG Remover...")
    app.run_polling(drop_pending_updates=True, stop_signals=None)
