import logging
import os
import threading
import http.server
import socketserver
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# ၁။ Logging & Render Port Fix
logging.basicConfig(level=logging.INFO)
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()

# ၂။ Video ဒေါင်းပေးမည့် Function
def download_video(url):
    ydl_opts = {
        'format': 'best', # အကောင်းဆုံး Quality ကို ယူမယ်
        'outtmpl': 'video.mp4', # နာမည်ကို video.mp4 လို့ ပေးမယ်
        'max_filesize': 50 * 1024 * 1024, # Telegram က 50MB ထက်ကြီးရင် ပို့ရခက်လို့ ကန့်သတ်ထားတာ
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "video.mp4"

# ၃။ Message Handler (Link ဝင်လာရင် စစ်မယ်)
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    # Link ဟုတ်မဟုတ် အကြမ်းဖျင်းစစ်မယ်
    if "http" not in url: return

    status = await update.message.reply_text("ဗီဒီယိုကို ရှာဖွေပြီး ဒေါင်းလုဒ်ဆွဲပေးနေတယ် မောင်... ခဏစောင့်နော်။ 📥")
    
    try:
        # ဗီဒီယို ဒေါင်းမယ်
        video_file = download_video(url)
        
        # Telegram ဆီ ပြန်ပို့မယ်
        await update.message.reply_video(video=open(video_file, 'rb'), caption="ဟောဒီမှာ မောင့်အတွက် ဗီဒီယိုလေး! 🎥")
        
        # ဆာဗာပေါ်က ဖိုင်ကို ပြန်ဖျက်မယ်
        if os.path.exists(video_file): os.remove(video_file)
        await status.delete()
        
    except Exception as e:
        await update.message.reply_text(f"ဆောရီး မောင်... ဒေါင်းလို့မရဘူး ဖြစ်နေတယ်။ Link မှားနေတာလား ဒါမှမဟုတ် ဖိုင်က အရမ်းကြီးနေတာလား မသိဘူးဗျ။")
        logging.error(f"Download Error: {e}")

# ၄။ Main
if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI'
    app = ApplicationBuilder().token(TOKEN).build()
    
    # စာသား (Link) ဝင်လာရင် ကိုင်တွယ်မယ်
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_link))
    
    print("Video Downloader Bot is running...")
    app.run_polling()
