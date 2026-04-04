import logging
import os
import requests
import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# ၁။ Logging (Error သိဖို့)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Render Fix (Port ဖွင့်ထားမှ Render က မပိတ်မှာပါ)
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    with TCPServer(("", port), SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()

API_KEY = 'JL152Nmq2qJiPfe5bn6ZmDqF'

# ၂။ Photo Handler
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    file_path = f"{photo_file.file_id}.jpg"
    await photo_file.download_to_drive(file_path)
    
    # ပုံနဲ့ Caption ကို သိမ်းထားမယ်
    context.user_data['last_photo'] = file_path
    context.user_data['caption'] = update.message.caption if update.message.caption else "Dominic AI"

    keyboard = [
        [InlineKeyboardButton("💳 Credit စစ်မယ်", callback_data='check_credit')],
        [InlineKeyboardButton("🖼️ Background ဖျက်မယ်", callback_data='remove_bg')],
        [InlineKeyboardButton("✍️ ပုံပေါ်စာရိုက်မယ်", callback_data='add_text')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("ဘာလုပ်ချင်လဲ ရွေးပေးပါ မောင်-", reply_markup=reply_markup)

# ၃။ Button Callback (ဒါက အဓိကပဲ မောင်)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Button နှိပ်တာ လက်ခံလိုက်ပြီလို့ Telegram ကို ပြောတာ
    
    data = query.data
    img_path = context.user_data.get('last_photo')

    if not img_path:
        await query.edit_message_text(text="ပုံကို အရင်ပို့ပေးပါဦး မောင်!")
        return

    if data == 'check_credit':
        try:
            res = requests.get('https://api.remove.bg/v1.0/account', headers={'X-API-Key': API_KEY})
            credit = res.json()['data']['attributes']['credits']['total']
            await query.edit_message_text(text=f"မောင့်ဆီမှာ Credit {credit} ခု ကျန်သေးတယ်! ✨")
        except:
            await query.edit_message_text(text="Credit စစ်လို့မရဘူး ဖြစ်နေတယ် မောင်။")

    elif data == 'remove_bg':
        await query.edit_message_text(text="စီစဉ်နေတယ် မောင်... ခဏစောင့်နော်။")
        out_path = f"nobg_{img_path}.png"
        res = requests.post('https://api.remove.bg/v1.0/removebg',
                            files={'image_file': open(img_path, 'rb')},
                            data={'size': 'auto'},
                            headers={'X-API-Key': API_KEY})
        if res.status_code == 200:
            with open(out_path, 'wb') as f: f.write(res.content)
            await query.message.reply_document(document=open(out_path, 'rb'), caption="Background ဖျက်ပြီးပါပြီ!")
        else:
            await query.message.reply_text("API Error တက်နေတယ် မောင်။")

    elif data == 'add_text':
        await query.edit_message_text(text="ပုံပေါ်မှာ စာသား ထည့်ပေးနေတယ်... ✨")
        out_text_path = f"text_{img_path}"
        text_to_write = context.user_data.get('caption', 'Dominic')
        
        img = Image.open(img_path)
        draw = ImageDraw.Draw(img)
        w, h = img.size
        draw.text((w/2, h/2), text_to_write, fill="white", anchor="mm")
        img.save(out_text_path)
        
        await query.message.reply_photo(photo=open(out_text_path, 'rb'), caption="ရပါပြီ မောင်!")

# ၄။ Main
if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI'
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Handler တွေ ထည့်မယ်
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(button_callback)) # Button Handler
    
    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)
