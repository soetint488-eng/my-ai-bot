import logging
import os
import threading
import http.server
import socketserver
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# ၁။ Logging (Restart ဖြစ်တာကို သိဖို့)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Render ဆာဗာကို အမြဲနိုးနေအောင် လုပ်ပေးတဲ့အပိုင်း
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            logging.info(f"Dummy server running on port {port}")
            httpd.serve_forever()
    except Exception as e:
        logging.error(f"Server Error: {e}")

# ၂။ Video Downloader (Quality နည်းနည်းလျှော့ပြီး File Size သေးအောင် လုပ်ထားတယ်)
def download_video(url):
    ydl_opts = {
        'format': 'best[ext=mp4]/best', # MP4 အကြည်ဆုံးကို ယူမယ်
        'outtmpl': 'downloaded_video.mp4',
        'max_filesize': 45 * 1024 * 1024, # 45MB ထက် မကျော်အောင် ကန့်သတ်မယ်
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "downloaded_video.mp4"

# ၃။ Message ကို ကိုင်တွယ်တဲ့အပိုင်း
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "http" not in url: return

    status = await update.message.reply_text("ဗီဒီယိုကို စစ်ဆေးနေတယ် မောင်... ခဏစောင့်နော်။ 📥")
    
    try:
        # ဗီဒီယို ဒေါင်းမယ်
        video_file = download_video(url)
        
        # ဗီဒီယို ပို့မယ်
        sent_message = await update.message.reply_video(
            video=open(video_file, 'rb'), 
            caption="ဟောဒီမှာ မောင့်အတွက် ဗီဒီယိုလေး! 🎥"
        )
        
        # ✨ အပေါ်ဆုံးမှာ ကပ်နေအောင် Pin လုပ်ပေးမည့်အပိုင်း
        try:
            await context.bot.pin_chat_message(
                chat_id=update.effective_chat.id,
                message_id=sent_message.message_id,
                disable_notification=True
            )
        except Exception: pass # Group မဟုတ်ရင် pin ခွင့်မရှိတာမျိုးရှိလို့ error ကျော်မယ်

        # ဆာဗာပေါ်က ဖိုင်ဖျက်မယ်
        if os.path.exists(video_file): os.remove(video_file)
        await status.delete()
        
    except Exception as e:
        await update.message.reply_text("ဆောရီး မောင်... ဖိုင်အရမ်းကြီးနေတာ (သို့မဟုတ်) Link ပျက်နေတာ ဖြစ်နိုင်ပါတယ်ဗျ။")
        logging.error(f"Error: {e}")

# ၄။ ပင်မ လုပ်ဆောင်ချက်
if __name__ == '__main__':
    # Render Fix ကို Background မှာ နှိုးထားမယ်
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI'
    
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_link))
        
        logging.info("--- Bot is ready and waiting for links ---")
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        logging.error(f"Startup Error: {e}")
