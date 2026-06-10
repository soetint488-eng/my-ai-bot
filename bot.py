import sys
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8702294693:AAHff0iYwzElcLNZzPhlXodImHePQuzYDl0"
verified_users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    verified_users[user_id] = False

    keyboard = [
        [
            InlineKeyboardButton("✅ ဟုတ်ကဲ့၊ ၁၈ နှစ်ပြည့်ပါပြီ", callback_data='age_verified'),
            InlineKeyboardButton("❌ မပြည့်သေးပါ", callback_data='age_failed')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    warning_text = (
        "⚠️ **သတိပေးချက် / WARNING** ⚠️\n\n"
        "ဒီ Bot တွင် အသက် ၁၈ နှစ်အထက်သာ ကြည့်ရှုခွင့်ရှိသော အကြောင်းအရာများ ပါဝင်ပါသည်။\n"
        "အသက် ၁၈ နှစ်မပြည့်သေးသူများ အသုံးမပြုရပါ။\n\n"
        "သင်သည် အသက် ၁၈ နှစ်ပြည့်ပြီးသူ ဖြစ်ပါသလား။"
    )
    await update.message.reply_text(text=warning_text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    if query.data == 'age_failed':
        verified_users[user_id] = False
        await query.edit_message_text(text="❌ စည်းကမ်းချက်အရ အသက်မပြည့်သေးသဖြင့် ဤ Bot ကို အသုံးပြုခွင့်မရှိပါ။")
        return

    if query.data == 'age_verified':
        verified_users[user_id] = True
        await query.edit_message_text(text="✅ အတည်ပြုချက် အောင်မြင်သည်။ ယခု ပြုပြင်လိုသော **လူပုံ (ဓာတ်ပုံ)** ကို ပို့ပေးနိုင်ပါပြီ။")

# =====================================================================
# ရရှိလာသော Screenshot အရ ပြုပြင်ထားသည့် API ချိတ်ဆက်မှုအပိုင်း
# =====================================================================
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not verified_users.get(user_id, False):
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ ပထမဦးစွာ /start ကိုနှိပ်ပြီး အသက် ၁၈ နှစ်ပြည့်ကြောင်း အတည်ပြုပေးပါ။")
        return

    await update.message.reply_text("⏳ ဓာတ်ပုံကို လက်ခံရရှိပါပြီ။ AI ဖြင့် လုပ်ဆောင်နေသဖြင့် ခဏစောင့်ဆိုင်းပေးပါ...")

    # Telegram ဆာဗာပေါ်ရှိ ပုံလင့်ခ်ကို ယူခြင်း
    photo_file = await update.message.photo[-1].get_file()
    user_photo_url = photo_file.file_path  

    # သင့် Screenshot ပြကွက်အရ သတ်မှတ်ချက်အသစ်များ
    API_URL = "https://nodress.p.rapidapi.com/image" # သို့မဟုတ် သင့် endpoint URL
    
    headers = {
        'Content-Type': 'application/json',
        'x-rapidapi-host': 'nodress.p.rapidapi.com',
        'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
    }

    # Screenshot ထဲက body တောင်းဆိုချက်အရ json ပုံစံဖြင့် ထည့်သွင်းခြင်း
    # (validation error မတက်စေရန် body ထဲတွင် ပို့ရပါမည်)
    payload = {
        "id_gen": "123456789",
        "name": "egncvJ0cJemcUX5",
        "webhook": "https://example.com/webhook",
        "image": user_photo_url  # User ပို့လိုက်တဲ့ ပုံလင့်ခ်ကို ဒီနေရာမှာ ထည့်ပေးလိုက်ပါတယ်
    }

    try:
        # GET မဟုတ်ဘဲ requests.post သို့ ပြောင်းလဲလိုက်ပါတယ်
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # API က ပြန်ပေးတဲ့ JSON ထဲမှာ ပုံလင့်ခ် ပါ/မပါ စစ်ဆေးခြင်း
            # (မှတ်ချက် - API ရဲ့ ရလဒ်ပေါ်မူတည်ပြီး key နာမည် ပြောင်းလဲနိုင်သည်)
            if "url" in result:
                await update.message.reply_photo(photo=result["url"], caption="✨ AI ဖြင့် ပြုပြင်ပြီးစီးသော ဓာတ်ပုံ ဖြစ်ပါသည်။")
            elif "image" in result:
                await update.message.reply_photo(photo=result["image"], caption="✨ AI ဖြင့် ပြုပြင်ပြီးစီးသော ဓာတ်ပုံ ဖြစ်ပါသည်။")
            else:
                await update.message.reply_text(f"⚠️ လုပ်ဆောင်ချက် အောင်မြင်သော်လည်း ပုံလင့်ခ် တိုက်ရိုက်မထွက်လာပါ။\nAPI Response: {str(result)}")
        else:
            await update.message.reply_text(f"❌ API Error တက်သွားသည်။ Code: {response.status_code}\nအသေးစိတ်: {response.text}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ ဆာဗာချိတ်ဆက်မှု အဆင်မပြေပါ- {str(e)}")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))

    print("Bot စတင်ပတ်နေပါပြီ...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
