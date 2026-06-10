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
    verified_users[user_id] = False # အစပိုင်းမှာ ခွင့်မပြုသေးကြောင်း မှတ်ထားမည်

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

    # အသက်မပြည့်သေးရင် သို့မဟုတ် ခလုတ်မနှိပ်ရသေးရင် အလုပ်မလုပ်ပါ
    if not verified_users.get(user_id, False):
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ ပထမဦးစွာ /start ကိုနှိပ်ပြီး အသက် ၁၈ နှစ်ပြည့်ကြောင်း အတည်ပြုပေးပါ။")
        return

    await update.message.reply_text("⏳ ဓာတ်ပုံကို လက်ခံရရှိပါပြီ။ AI ဖြင့် လုပ်ဆောင်နေသဖြင့် ခဏစောင့်ဆိုင်းပေးပါ...")

    # (က) User ပို့လိုက်တဲ့ ဓာတ်ပုံရဲ့ လင့်ခ်ကို Telegram ဆာဗာကနေ ဆွဲယူခြင်း
    photo_file = await update.message.photo[-1].get_file()
    user_photo_url = photo_file.file_path  # User ပို့လိုက်တဲ့ ပုံလင့်ခ်ကို ရပါပြီ

    # (ခ) ပေးထားသော RapidAPI ထံသို့ ပုံလင့်ခ် ပေးပို့တောင်းဆိုခြင်း
    API_URL = "https://nodress.p.rapidapi.com/image"
    
    # များသောအားဖြင့် ဤကဲ့သို့ API များသည် ပုံလင့်ခ်ကို Parameter သို့မဟုတ် Body ထဲတွင် ထည့်ခိုင်းတတ်ပါသည်
    # ဒီနေရာမှာ API ရဲ့ လိုအပ်ချက်အတိုင်း ဖြည့်သွင်းရပါမယ် (ဥပမာအနေနဲ့ query ထဲထည့်ပြထားပါတယ်)
    query_params = {
        'DeepStrip': 'Image',
        'url': user_photo_url  # သင့် API သတ်မှတ်ချက်အတိုင်း ပြောင်းလဲနိုင်ပါသည်
    }
    
    headers = {
        'Content-Type': 'application/json',
        'x-rapidapi-host': 'nodress.p.rapidapi.com',
        'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
    }

    try:
        response = requests.get(API_URL, headers=headers, params=query_params)
        
        if response.status_code == 200:
            result = response.json()
            
            # (ဂ) API မှ ပြန်ထွက်လာသော JSON ထဲက ပုံလင့်ခ်ကို ရှာဖွေခြင်း
            # Note: API ရဲ့ JSON response key ပေါ်မူတည်ပြီး "url" နေရာမှာ ပြောင်းလဲပေးရန်
            if "url" in result:
                output_image_url = result["url"]
                # ပြီးစီးသွားသော ပုံကို User ထံ ပြန်လည် ပေးပို့ခြင်း
                await update.message.reply_photo(photo=output_image_url, caption="✨ AI ဖြင့် ပြုပြင်ပြီးစီးသော ဓာတ်ပုံ ဖြစ်ပါသည်။")
            else:
                await update.message.reply_text(f"⚠️ ပုံမထွက်လာပါ။ API အဖြေ: {str(result)}")
        else:
            await update.message.reply_text(f"❌ API Error တက်သွားသည်။ Status: {response.status_code}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ ဆာဗာချိတ်ဆက်မှု အဆင်မပြေပါ- {str(e)}")

# =====================================================================
# ၄။ ပရိုဂရမ် စတင်ပတ်မည့်နေရာ
# =====================================================================
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # စီမံမည့် Handler များ
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))
    
    # User က ဓာတ်ပုံ (Photo) ပို့လာရင် handle_image ထဲကို ပို့ပေးဖို့ သတ်မှတ်ခြင်း
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))

    print("Bot စတင်ပတ်နေပါပြီ...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
