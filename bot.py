import sys
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Token သတ်မှတ်ခြင်း
TOKEN = "8702294693:AAHff0iYwzElcLNZzPhlXodImHePQuzYDl0"

# အသက်အတည်ပြုပြီးသား user စာရင်းကို မှတ်ထားရန် dictionary
verified_users = {}

# =====================================================================
# ၁။ /start ခေါ်လျှင် သတိပေးချက်စာနှင့် ခလုတ်ပြခြင်း
# =====================================================================
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
        "ဒီ Bot တွင် အသက် ၁၈ နှစ်အထက်သာ ကြည့်ရှုခွင့်ရှိသော အကြောင်းအရာများ (AI Cloth Removal) ပါဝင်ပါသည်။\n"
        "အသက် ၁၈ နှစ်မပြည့်သေးသူများ အသုံးမပြုရပါ။\n\n"
        "သင်သည် အသက် ၁၈ နှစ်ပြည့်ပြီးသူ ဖြစ်ပါသလား။"
    )
    await update.message.reply_text(text=warning_text, reply_markup=reply_markup, parse_mode="Markdown")

# =====================================================================
# ၂။ ခလုတ်နှိပ်ခြင်းကို စစ်ဆေးခြင်း
# =====================================================================
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
# ၃။ User က ဓာတ်ပုံ ပို့လာသည့်အခါ API နှင့် ချိတ်ဆက် အလုပ်လုပ်မည့်အပိုင်း
# =====================================================================
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not verified_users.get(user_id, False):
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ ပထမဦးစွာ /start ကိုနှိပ်ပြီး အသက် ၁၈ နှစ်ပြည့်ကြောင်း အတည်ပြုပေးပါ။")
        return

    await update.message.reply_text("⏳ ဓာတ်ပုံကို လက်ခံရရှိပါပြီ။ AI ဖြင့် လုပ်ဆောင်နေသဖြင့် ขဏစောင့်ဆိုင်းပေးပါ...")

    # (က) User ပို့လိုက်တဲ့ ဓာတ်ပုံရဲ့ လင့်ခ်ကို Telegram ဆာဗာကနေ ဆွဲယူခြင်း
    photo_file = await update.message.photo[-1].get_file()
    user_photo_url = photo_file.file_path  

    # (ခ) API သို့ ပုံလင့်ခ် ထည့်သွင်း၍ လှမ်းခေါ်ခြင်း
    API_URL = "https://nodress.p.rapidapi.com/image"
    
    # ပြင်ဆင်ချက်- API သတ်မှတ်ချက်အရ ဓာတ်ပုံလင့်ခ်ကို 'image' သို့မဟုတ် 'url' ဟု ထည့်ပေးရန် လိုအပ်သည်
    query_params = {
        'DeepStrip': 'Image',
        'image': user_photo_url  # သို့မဟုတ် API သတ်မှတ်ချက်အရ 'url' ဟု ပြောင်းနိုင်သည်
    }
    
    headers = {
        'Content-Type': 'application/json',
        'x-rapidapi-host': 'nodress.p.rapidapi.com',
        'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
    }

    try:
        response = requests.get(API_URL, headers=headers, params=query_params)
        
        # စစ်ဆေးရန်- API ဘက်က ဘာတွေ ပြန်ပေးလဲဆိုတာ ကြည့်ခြင်း
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # API ရဲ့ output key ပေါ်မူတည်ပြီး ပုံကို ဆွဲထုတ်ခြင်း
            if "url" in result:
                output_image_url = result["url"]
                await update.message.reply_photo(photo=output_image_url, caption="✨ AI ဖြင့် ပြုပြင်ပြီးစီးသော ဓာတ်ပုံ ဖြစ်ပါသည်။")
            elif "image" in result:
                output_image_url = result["image"]
                await update.message.reply_photo(photo=output_image_url, caption="✨ AI ဖြင့် ပြုပြင်ပြီးစီးသော ဓာတ်ပုံ ဖြစ်ပါသည်။")
            else:
                await update.message.reply_text(f"⚠️ ပုံလင့်ခ် မထွက်လာပါ။ API Response: {str(result)}")
        else:
            await update.message.reply_text(f"❌ API Error တက်သွားသည်။ Status: {response.status_code}\nအသေးစိတ်: {response.text}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ ဆာဗာချက်ဆက်မှု အဆင်မပြေပါ- {str(e)}")

# =====================================================================
# ၄။ ပရိုဂရမ် စတင်ပတ်မည့်နေရာ
# =====================================================================
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))

    print("Bot စတင်ပတ်နေပါပြီ...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
