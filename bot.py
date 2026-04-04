import logging
import os
import requests
import threading
import http.server
import socketserver
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CallbackQueryHandler, CommandHandler

# ၁။ Logging & Render Fix
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

API_KEY = 'JL152Nmq2qJiPfe5bn6ZmDqF'

# ၂။ Photo Handler (Button ပြမည့်အပိုင်း)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    file_path = f"{photo_file.file_id}.jpg"
    await photo_file.download_to_drive(file_path)
    
    # ပုံလမ်းကြောင်းနဲ့ Caption ကို ယာယီသိမ်းမယ်
    context.user_data['last_photo'] = file_path
    context.user_data['caption'] = update.message.caption if update.message.caption else "Dominic AI"

    keyboard = [
        [InlineKeyboardButton("💳 Credit စစ်မယ်", callback_data='check_credit')],
        [InlineKeyboardButton("🖼️ Background ဖျက်မယ်", callback_data='remove_bg')],
        [InlineKeyboardButton("✍️ ပုံပေါ်စာရိုက်မယ်", callback_data='add_text')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("ဘာလုပ်ချင်လဲ ရွေးပေးပါ မောင်-", reply_markup=reply_markup)

# ၃။ Button နှိပ်ရင် အလုပ်လုပ်မည့် Function
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    # Button နှိပ်လိုက်တာကို Telegram သိအောင် အရင် Answer လုပ်ရမယ်
    await query.answer()
    
    data = query.data
    img_path = context.user_data.get('last_photo')

    if not img_path or not os.path.exists(img_path):
        await query.edit_message_text(text="ဆောရီး မောင်... ပုံဖိုင် ပျောက်သွားလို့ နောက်တစ်ပုံ ထပ်ပို့ပေးပါဦး။")
        return

    if data == 'check_credit':
        res = requests.get('https://api.remove.bg/v1.0/account', headers={'X-API-Key': API_KEY})
        credit = res.json()['data']['attributes']['credits']['total'] if res.status_code == 200 else "Error"
        await query.edit_message_text(text=f"မောင့်ဆီမှာ Credit {credit} ခု ကျန်သေးတယ်နော်! ✨")

    elif data == 'remove_bg':
        await query.edit_message_text(text="Background ဖျက်ပေးနေတယ် မောင်... ခဏစောင့်နော်။")
        out_path = f"nobg_{img_path}.png"
        res = requests.post('https://api.remove.bg/v1.0/removebg',
                            files={'image_file': open(img_path, 'rb')},
                            data={'size': 'auto'},
                            headers={'X-API-Key': API_KEY})
        if res.status_code == 200:
            with open(out_path, 'wb') as f: f.write(res.content)
            await query.message.reply_document(document=open(out_path, 'rb'), caption="Background ဖျက်ပြီးပါပြီ!")
            if os.path.exists(out_path): os.remove(out_path)
        else:
            await query.message.reply_text("Credit မလောက်တာ (သို့မဟုတ်) API Error ဖြစ်နေတယ် မောင်။")

    elif data == 'add_text':
        await query.edit_message_text(text="ပုံပေါ်မှာ စာသားလေး ထည့်ပေးနေတယ်... ✨")
        out_text_path = f"text_{img_path}.jpg"
        text_to_write = context.user_data.get('caption', 'Dominic')
        
        # ပုံပေါ်စာရေးတဲ့အပိုင်း (Pillow)
        img = Image.open(img_path)
        draw = ImageDraw.Draw(img)
        w, h = img.size
        # Font မရှိရင် default ပဲ သုံးမယ် (Render ပေါ်မှာ Font ရှာရခက်လို့)
        draw.text((w/2, h/2), text_to_write, fill="white", anchor="mm")
        img.save(out_text_path)
        
        await query.message.reply_photo(photo=open(out_text_path, 'rb'), caption="စာသားထည့်ပေးလိုက်ပြီ မောင်!")
        if os.path.exists(out_text_path): os.remove(out_text_path)

# ၄။ Main
if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI'
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Handler တွေကို သေချာ ထည့်ပေးရမယ်
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(button_callback)) # Button အတွက် Handler
    
    print("Bot is running with Functional Buttons...")
    app.run_polling(drop_pending_updates=True)
