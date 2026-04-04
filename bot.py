import logging
import os
import requests
import threading
import http.server
import socketserver
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# ၁။ Logging & Render Fix
logging.basicConfig(level=logging.INFO)
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()

API_KEY = 'JL152Nmq2qJiPfe5bn6ZmDqF'

# ၂။ Credit စစ်တဲ့ Function
def get_credit():
    response = requests.get('https://api.remove.bg/v1.0/account', headers={'X-API-Key': API_KEY})
    if response.status_code == 200:
        data = response.json()
        return data['data']['attributes']['credits']['total']
    return "Error"

# ၃။ ပုံပေါ်မှာ စာရိုက်တဲ့ Function
def add_text_to_image(input_path, output_path, text):
    img = Image.open(input_path)
    draw = ImageDraw.Draw(img)
    # စာသားအရွယ်အစားကို ပုံနဲ့လိုက်ဖက်အောင် ချိန်ညှိမယ်
    width, height = img.size
    font_size = int(height / 10)
    try:
        font = ImageFont.truetype("arial.ttf", font_size) # Font မရှိရင် default သုံးမယ်
    except:
        font = ImageFont.load_default()
    
    draw.text((width/2, height/2), text, fill="white", anchor="mm", font=font)
    img.save(output_path)

# ၄။ Photo Handler (Buttons ပြပေးမည့်အပိုင်း)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    file_path = f"{photo.file_id}.jpg"
    await photo.download_to_drive(file_path)
    context.user_data['last_photo'] = file_path
    context.user_data['caption'] = update.message.caption if update.message.caption else "Dominic AI"

    keyboard = [
        [InlineKeyboardButton("💳 Credit စစ်မယ်", callback_data='check_credit')],
        [InlineKeyboardButton("🖼️ Background ဖျက်မယ်", callback_data='remove_bg')],
        [InlineKeyboardButton("✍️ ပုံပေါ်စာရိုက်မယ်", callback_data='add_text')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("ဘာလုပ်ချင်လဲ ရွေးပေးပါ မောင်-", reply_markup=reply_markup)

# ၅။ Button နှိပ်ရင် အလုပ်လုပ်မည့်အပိုင်း
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    img_path = context.user_data.get('last_photo')
    if not img_path: return

    if query.data == 'check_credit':
        credit = get_credit()
        await query.edit_message_text(text=f"မောင့်ဆီမှာ Credit {credit} ခု ကျန်သေးတယ်နော်! ✨")

    elif query.data == 'remove_bg':
        await query.edit_message_text(text="Background ဖျက်ပေးနေတယ် မောင်... ခဏစောင့်နော်။")
        out_path = f"nobg_{img_path}"
        res = requests.post('https://api.remove.bg/v1.0/removebg',
                            files={'image_file': open(img_path, 'rb')},
                            data={'size': 'auto'},
                            headers={'X-API-Key': API_KEY})
        if res.status_code == 200:
            with open(out_path, 'wb') as f: f.write(res.content)
            await query.message.reply_document(document=open(out_path, 'rb'))
        else:
            await query.message.reply_text("Error တက်သွားတယ် မောင်။")

    elif query.data == 'add_text':
        await query.edit_message_text(text="ပုံပေါ်မှာ စာသားလေး ထည့်ပေးနေတယ်... ✨")
        out_text_path = f"text_{img_path}"
        text_to_write = context.user_data.get('caption', 'Dominic')
        add_text_to_image(img_path, out_text_path, text_to_write)
        await query.message.reply_photo(photo=open(out_text_path, 'rb'), caption="စာသားထည့်ပေးလိုက်ပြီ မောင်!")

# ၆။ Main
if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI'
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("Buttons Bot is running...")
    app.run_polling(drop_pending_updates=True)
