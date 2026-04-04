import logging
import os
import threading
import requests
import google.generativeai as genai
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from PIL import Image, ImageDraw
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# ၁။ Logging & Render Fix
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    with TCPServer(("", port), SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()

# ၂။ API Keys များ
REMOVE_BG_API = 'JL152Nmq2qJiPfe5bn6ZmDqF'
GEMINI_API_KEY = 'AIzaSyDVotL1VA-aJ9wI7nWaduQwSvpmkyf4ZZY'

# Gemini AI ကို ချိတ်ဆက်ခြင်း
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# ၃။ Gemini နဲ့ စကားပြောမည့် Function
async def chat_with_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text: return

    # စာသားဝင်လာရင် AI က ပြန်ဖြေပေးမယ်
    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("ဆောရီး မောင်... AI က ခဏနားနေလို့ပါ။")

# ၄။ Photo Handler (Buttons ပြမည့်အပိုင်း)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    file_path = f"{photo_file.file_id}.jpg"
    await photo_file.download_to_drive(file_path)
    
    context.user_data['last_photo'] = file_path
    context.user_data['caption'] = update.message.caption if update.message.caption else "Dominic AI"

    keyboard = [
        [InlineKeyboardButton("💳 Credit စစ်မယ်", callback_data='check_credit')],
        [InlineKeyboardButton("🖼️ Background ဖျက်မယ်", callback_data='remove_bg')],
        [InlineKeyboardButton("✍️ ပုံပေါ်စာရိုက်မယ်", callback_data='add_text')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("ပုံအတွက် ဘာလုပ်ပေးရမလဲ မောင်-", reply_markup=reply_markup)

# ၅။ Button Callback
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    img_path = context.user_data.get('last_photo')

    if data == 'check_credit':
        res = requests.get('https://api.remove.bg/v1.0/account', headers={'X-API-Key': REMOVE_BG_API})
        credit = res.json()['data']['attributes']['credits']['total'] if res.status_code == 200 else "Error"
        await query.message.reply_text(text=f"Credit {credit} ခု ကျန်သေးတယ် မောင်! ✨")

    elif data == 'remove_bg':
        await query.edit_message_text(text="Background ဖျက်ပေးနေတယ်... ✨")
        res = requests.post('https://api.remove.bg/v1.0/removebg',
                            files={'image_file': open(img_path, 'rb')},
                            data={'size': 'auto'},
                            headers={'X-API-Key': REMOVE_BG_API})
        if res.status_code == 200:
            out_path = f"nobg_{img_path}.png"
            with open(out_path, 'wb') as f: f.write(res.content)
            await query.message.reply_document(document=open(out_path, 'rb'))
        else:
            await query.message.reply_text("Error တက်သွားတယ် မောင်။")

    elif data == 'add_text':
        await query.edit_message_text(text="ပုံပေါ်စာရေးပေးနေတယ်... ✍️")
        img = Image.open(img_path)
        draw = ImageDraw.Draw(img)
        draw.text((img.size[0]/2, img.size[1]/2), context.user_data.get('caption'), fill="white", anchor="mm")
        out_text = f"text_{img_path}"
        img.save(out_text)
        await query.message.reply_photo(photo=open(out_text, 'rb'))

# ၆။ Main
if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    TOKEN = '8702294693:AAExt0a40BMgE0kEjlMnFmwB_zfRZn37-lI'
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Handler များ (စာပို့ရင် AI က ဖြေမယ်၊ ပုံပို့ရင် Button ပြမယ်)
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat_with_ai))
    
    print("AI Bot is running now!")
    app.run_polling(drop_pending_updates=True)
