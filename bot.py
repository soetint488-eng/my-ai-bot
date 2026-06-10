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
            InlineKeyboardButton("✅ ဟုတ်ကဲ့၊ ၁9 နှစ်ပြည့်ပါပြီ", callback_data='age_verified'),
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
# အသစ်ပေးထားသော curl အတိုင်း အလုပ်လုပ်မည့် Function
# =====================================================================
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not verified_users.get(user_id, False):
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ ပထမဦးစွာ /start ကိုနှိပ်ပြီး အသက် ၁၈ နှစ်ပြည့်ကြောင်း အတည်ပြုပေးပါ။")
        return

    await update.message.reply_text("⏳ ဓာတ်ပုံကို လက်ခံရရှိပါပြီ။ ဆာဗာသို့ ပေးပို့၍ AI ဖြင့် စတင်လုပ်ဆောင်နေပါပြီ။ ခဏစောင့်ဆိုင်းပေးပါ...")

    # Telegram ဆာဗာမှ ပုံလင့်ခ်ကို ရယူခြင်း
    photo_file = await update.message.photo[-1].get_file()
    user_photo_url = photo_file.file_path  

    # ပေးထားသော curl specification အသစ်များ
    API_URL = "https://undress-ai-api.p.rapidapi.com/api/videoGenerations/animate"
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-rapidapi-host': 'undress-ai-api.p.rapidapi.com',
        'x-rapidapi-key': '283b178159msh486932881be989fp157c27jsn617224a255da'
    }

    # x-www-form-urlencoded ဖြစ်သောကြောင့် requests တွင် json= အစား data= သုံးရပါမည်
    form_data = {
        'image': user_photo_url,  # Telegram ပုံလင့်ခ်ကို ထည့်သွင်းခြင်း
        'name': 'egncvJ0CJemcUX5',
        'id_gen': '123456789',
        'webhook': 'https://example.com/webhook'
    }

    try:
        # POST request ပို့ခြင်း
        response = requests.post(API_URL, headers=headers, data=form_data)
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            
            # API က ဗီဒီယို သို့မဟုတ် ပုံလင့်ခ်ကို ပြန်ပေးသည့် Key အား ရှာဖွေခြင်း
            # (များသောအားဖြင့် 'url', 'video_url' သို့မဟုတ် 'output' ဟု ပါတတ်ပါသည်)
            output_url = result.get("url") or result.get("video_url") or result.get("image") or result.get("output")
            
            if output_url:
                # ရလဒ်က ဗီဒီယိုဖိုင် ဖြစ်နိုင်ခြေများသောကြောင့် အဆင်ပြေအောင် reply_document သုံးထားပါတယ်
                await update.message.reply_document(document=output_url, caption="✨ AI ဖြင့် ပြုပြင်ဖန်တီးပြီးစီးသော ရလဒ်ဖိုင် ဖြစ်ပါသည်။")
            else:
                await update.message.reply_text(f"⚠️ လုပ်ဆောင်ချက် အောင်မြင်သော်လည်း ရလဒ်ဖိုင်လင့်ခ်ကို တိုက်ရိုက်ရှာမတွေ့ပါ။\nAPI Response: {str(result)}")
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
